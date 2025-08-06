"""Webhook endpoint for processing document queries with RAG."""
from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .retriever import Retriever
from .schema import Clause

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = Path("backend_index/store")
DOCS_DIR = Path("documents")
UPLOAD_DIR = DOCS_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize components
retriever = None
llm = None


def download_file(url: str, save_path: Path) -> Path:
    """Download a file from URL to the specified path."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return save_path


def initialize_components():
    """Initialize the retriever and LLM components."""
    global retriever, llm
    
    # Initialize retriever
    retriever = Retriever(model_name=MODEL_NAME, index_path=INDEX_PATH)
    
    # Initialize LLM (Groq)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    llm = ChatGroq(
        temperature=0,
        model_name="mixtral-8x7b-32768",
        groq_api_key=groq_api_key
    )


def format_docs(docs: List[Clause]) -> str:
    """Format documents for the prompt."""
    return "\n\n".join(f"Document {i+1}:\n{doc.text}" for i, doc in enumerate(docs))


def get_rag_chain():
    """Create a RAG chain with prompt and LLM."""
    template = """You are an AI assistant for answering questions about insurance policies.
    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    
    Context: {context}
    
    Question: {question}
    
    Answer in a clear and concise manner. Only include information that can be directly inferred from the context.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_and_retrieve(question: str) -> dict:
        """Retrieve and format documents for the question."""
        docs = retriever.retrieve(question, top_k=3)
        return {
            "context": format_docs(docs),
            "question": question
        }
    
    # Create the chain
    chain = (
        RunnablePassthrough()
        | format_and_retrieve
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


@app.route('/hackrx/run', methods=['POST'])
def process_query():
    """Process a query with documents and questions."""
    # Check authorization
    auth_header = request.headers.get('Authorization')
    expected_token = os.getenv("API_AUTH_TOKEN")
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid authorization header"}), 401
    
    token = auth_header.split(' ')[1]
    if token != expected_token:
        return jsonify({"error": "Invalid authorization token"}), 403
    
    # Parse request
    try:
        data = request.get_json()
        document_url = data.get('documents')
        questions = data.get('questions', [])
        
        if not document_url or not questions:
            return jsonify({"error": "Missing required fields: documents and questions are required"}), 400
        
        # Download document
        filename = secure_filename(Path(document_url).name)
        local_path = UPLOAD_DIR / filename
        
        try:
            download_file(document_url, local_path)
            logger.info(f"Downloaded document to {local_path}")
        except Exception as e:
            logger.error(f"Error downloading document: {str(e)}")
            return jsonify({"error": f"Failed to download document: {str(e)}"}), 400
        
        # Initialize components if not already done
        if retriever is None or llm is None:
            initialize_components()
        
        # Process questions
        answers = []
        rag_chain = get_rag_chain()
        
        for question in questions:
            try:
                # Generate answer using RAG chain
                answer = rag_chain.invoke(question)
                answers.append(answer)
                
            except Exception as e:
                logger.error(f"Error processing question: {str(e)}", exc_info=True)
                answers.append("I couldn't generate an answer for this question. Please try again or rephrase your question.")
        
        return jsonify({"answers": answers})
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    # Initialize components
    initialize_components()
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)), debug=True)
