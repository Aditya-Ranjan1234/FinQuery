"""Flask web server providing a beautiful UI + JSON API for HackRx LLM system."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from flask import Flask, Response, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add the parent directory to the path for Vercel
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Check if running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'

from hackrx_llm.decision_engine import evaluate
from hackrx_llm.ingestion import ingest_dir
from hackrx_llm.parser import parse_query
from hackrx_llm.retriever import Retriever

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Handle paths differently for Vercel vs local
if IS_VERCEL:
    # For Vercel, use /tmp for writable directories
    BASE_DIR = Path('/tmp')
    DOCS_DIR = BASE_DIR / 'documents'
    INDEX_PATH = BASE_DIR / 'backend_index' / 'store'
    
    # Create directories if they don't exist
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
else:
    # Local development paths
    BASE_DIR = Path(__file__).parent.parent
    DOCS_DIR = Path(os.getenv("DOCS_DIR", str(BASE_DIR / "documents"))).resolve()
    INDEX_PATH = Path(os.getenv("INDEX_PATH", str(BASE_DIR / "backend_index" / "store"))).with_suffix("")

TOP_K_DEFAULT = int(os.getenv("TOP_K", "5"))

# Upload directory for user documents
UPLOAD_DIR = DOCS_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:  # noqa: D401
    """Return a configured :class:`flask.Flask` application."""
    # Configure paths based on environment
    static_folder = str(Path(__file__).parent / 'static')
    template_folder = str(Path(__file__).parent / 'templates')

    app = Flask(
        __name__,
        static_folder=static_folder,
        template_folder=template_folder,
    )
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Handle preflight requests
    @app.after_request
    def after_request(response: Response) -> Response:
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Serve static files
    @app.route('/static/<path:path>')
    def serve_static(path: str) -> Response:
        return send_from_directory(static_folder, path)
    
    # Serve index.html for all other routes (SPA support)
    @app.route('/')
    @app.route('/<path:path>')
    def serve_app(path: str = '') -> Response:
        if path.startswith('api/') or path.startswith('static/'):
            return '', 404
        return send_from_directory(template_folder, 'index.html')

    retriever = _init_retriever()

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------
    @app.route("/api/ask", methods=['POST', 'OPTIONS'])
    def api_ask() -> Tuple[Response, int]:
        """Handle question-answering requests."""
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        try:
            data: Dict = request.get_json(force=True)
            if not data or 'query' not in data:
                return jsonify({"error": "Missing 'query' field"}), 400
                
            query_text: str = data.get("query", "").strip()
            if not query_text:
                return jsonify({"error": "Query cannot be empty"}), 400

            top_k = min(int(data.get("top_k", TOP_K_DEFAULT)), 20)  # Limit top_k to 20
            
            try:
                q_struct = parse_query(query_text)
                clauses = retriever.retrieve(query_text, top_k=top_k)
                resp = evaluate(q_struct, clauses)
                
                return app.response_class(
                    response=json.dumps(resp.model_dump(), indent=2, ensure_ascii=False),
                    mimetype="application/json"
                )
                
            except Exception as e:
                app.logger.error(f"Error processing query: {str(e)}", exc_info=True)
                return jsonify({
                    "error": "Error processing query",
                    "details": str(e)
                }), 500
                
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON payload"}), 400
        except Exception as e:
            app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/upload", methods=['POST', 'OPTIONS'])
    def api_upload() -> Tuple[Response, int]:
        """Receive one or more files via multipart/form-data and add to index."""
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        if "files" not in request.files:
            return jsonify({"error": "No 'files' field"}), 400
            
        files = request.files.getlist("files")
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "No selected files"}), 400
            
        uploaded, total_clauses, errors = [], 0, []
        
        for file in files:
            if not file or file.filename == "":
                continue
                
            try:
                filename = secure_filename(file.filename)
                if not filename:
                    errors.append(f"Invalid filename: {file.filename}")
                    continue
                    
                save_path = UPLOAD_DIR / filename
                
                # Save the file
                file.save(save_path)
                
                try:
                    from hackrx_llm.ingestion import ingest_file
                    
                    # Process the file
                    clauses = ingest_file(save_path)
                    retriever.add_clauses(clauses)
                    uploaded.append(filename)
                    total_clauses += len(clauses)
                    
                except Exception as e:
                    errors.append(f"Error processing {filename}: {str(e)}")
                    # Clean up the saved file if there was an error
                    if save_path.exists():
                        save_path.unlink()
                    
            except Exception as e:
                errors.append(f"Error handling {getattr(file, 'filename', 'unknown')}: {str(e)}")
                continue
        
        # Save the updated index if we processed any files
        if uploaded:
            try:
                retriever.save(INDEX_PATH)
            except Exception as e:
                errors.append(f"Error saving index: {str(e)}")
        
        response = {
            "uploaded": uploaded,
            "clauses_added": total_clauses,
            "success": len(uploaded) > 0 and not errors
        }
        
        if errors:
            response["errors"] = errors
            
        status_code = 200 if response["success"] else 400
        return jsonify(response), status_code

    return app


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _init_retriever() -> Retriever:
    """
    Load existing index or build from documents.
    
    Returns:
        Retriever: An initialized Retriever instance
        
    Raises:
        RuntimeError: If there's an error initializing the retriever
    """
    try:
        # Check if index exists and load it
        index_file = INDEX_PATH.with_suffix(".faiss")
        if index_file.exists():
            try:
                app.logger.info(f"Loading existing index from {index_file}")
                return Retriever(index_path=INDEX_PATH)
            except Exception as e:
                app.logger.error(f"Error loading existing index: {e}")
                # Continue to rebuild the index if loading fails
                pass

        # Ensure documents directory exists
        if not DOCS_DIR.exists():
            app.logger.info(f"Creating documents directory at {DOCS_DIR}")
            DOCS_DIR.mkdir(parents=True, exist_ok=True)

        # Build index from documents
        current_app.logger.info(f"Building index from documents in {DOCS_DIR}")
        
        try:
            clauses = ingest_dir(DOCS_DIR)
            if not clauses:
                current_app.logger.warning(f"No documents found in {DOCS_DIR}")
                # Create an empty retriever if no documents found
                return Retriever()
                
            retriever = Retriever()
            retriever.fit(clauses)
            
            # Ensure index directory exists
            INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                retriever.save(INDEX_PATH)
                current_app.logger.info(f"Saved index to {INDEX_PATH}.faiss")
                return retriever
                
            except Exception as save_error:
                current_app.logger.error(f"Error saving index: {save_error}")
                # Return the in-memory retriever even if save fails
                return retriever
                
        except Exception as ingest_error:
            current_app.logger.error(f"Error ingesting documents: {ingest_error}")
            # Return an empty retriever if there's an error
            return Retriever()
            
    except Exception as e:
        error_msg = f"Failed to initialize retriever: {str(e)}"
        current_app.logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


# Create app instance for Vercel
app = create_app()

# Stand-alone run -----------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=True)
