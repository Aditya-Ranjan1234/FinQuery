# HackRx Webhook for RAG Agent

This webhook provides an API endpoint for processing document queries using a Retrieval-Augmented Generation (RAG) approach. It integrates with a vector database for semantic search and Groq's `llama-3.3-70b-versatile` model as the LLM provider.

## Prerequisites

1. Python 3.10+
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

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your credentials:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   API_AUTH_TOKEN=your_secure_auth_token_here
   FLASK_DEBUG=true
   ```
4. Run the webhook:
   ```bash
   python -m hackrx_llm.webhook
   ```

### Deployment to Render.com

1. Push your code to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - Name: `finquery-webhook`
   - Region: Choose the closest to your users
   - Branch: `main` (or your preferred branch)
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m hackrx_llm.webhook`
6. Add environment variables:
   - `PYTHON_VERSION`: 3.10.13
   - `GROQ_API_KEY`: Your Groq API key
   - `API_AUTH_TOKEN`: A secure token for API authentication
   - `FLASK_DEBUG`: false
7. Click "Create Web Service"

### Testing the Deployment

Once deployed, you can test the webhook with:

```bash
curl -X POST https://your-render-app.onrender.com/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{
    "documents": "https://example.com/your-policy.pdf",
    "questions": ["What is the grace period?", "What is covered?"],
    "model": "llama-3.3-70b-versatile"
  }'
```

## API Documentation

### POST /hackrx/run

Process a document and answer questions about it.

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <your_auth_token>`

**Request Body:**
```json
{
    "documents": "https://example.com/policy.pdf",
    "questions": [
        "What is the grace period?",
        "What is covered?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "The grace period is 30 days.",
        "The policy covers..."
    ]
}
```

### GET /health

Check if the service is running.

**Response:**
```json
{
    "status": "healthy",
    "model": "llama-3.3-70b-versatile"
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Invalid authorization token
- `500 Internal Server Error`: Server-side error

## Security

- Always use HTTPS in production
- Keep your API keys and tokens secure
- Rotate tokens regularly
- Implement rate limiting in production
- Set `FLASK_DEBUG=false` in production

## Monitoring

Monitor your deployment using:
- Render's built-in metrics and logs
- Health check endpoint: `GET /health`
