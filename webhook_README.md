# HackRx Webhook for RAG Agent

This webhook provides an API endpoint for processing document queries using a Retrieval-Augmented Generation (RAG) approach. It integrates with a vector database for semantic search and Groq as the LLM provider.

## Prerequisites

1. Python 3.8+
2. Required Python packages (install via `pip install -r requirements.txt`)
3. Groq API key (set as environment variable `GROQ_API_KEY`)
4. API authentication token (set as environment variable `API_AUTH_TOKEN`)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
GROQ_API_KEY=your_groq_api_key_here
API_AUTH_TOKEN=your_secure_auth_token_here
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Webhook

Start the webhook server:

```
python -m hackrx_llm.webhook
```

The server will start on `http://0.0.0.0:8080` by default.

## API Endpoint

### POST /hackrx/run

Process a document and answer questions about it.

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <your_auth_token>`

**Request Body:**
```json
{
    "documents": "https://example.com/document.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing conditions?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "The grace period is 30 days.",
        "The waiting period for pre-existing conditions is 36 months."
    ]
}
```

## Deployment

The webhook can be deployed using any WSGI server. For example, with Gunicorn:

```
gunicorn --bind 0.0.0.0:8080 hackrx_llm.webhook:app
```

## Error Handling

The API returns appropriate HTTP status codes and error messages in case of issues:

- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Invalid authorization token
- `500 Internal Server Error`: Server-side error

## Security

- Always use HTTPS in production
- Keep your API keys and tokens secure
- Rotate tokens regularly
- Implement rate limiting in production
