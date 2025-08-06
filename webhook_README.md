# HackRx Webhook for RAG Agent

This webhook provides an API endpoint for processing document queries using a Retrieval-Augmented Generation (RAG) approach. It integrates with a vector database for semantic search and Groq's `llama-3.3-70b-versatile` model as the LLM provider.

## Prerequisites

1. Python 3.10+
2. Node.js 16+ (for Vercel deployment)
3. Vercel CLI (`npm install -g vercel`)
4. Groq API key (set as environment variable `GROQ_API_KEY`)
5. API authentication token (set as environment variable `API_AUTH_TOKEN`)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Required for local development
GROQ_API_KEY=your_groq_api_key_here
API_AUTH_TOKEN=your_secure_auth_token_here
FLASK_DEBUG=true

# For Vercel deployment (set these in Vercel dashboard)
VERCEL=1
PYTHONUNBUFFERED=1
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

## Local Development

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Node.js dependencies (for Vercel):
   ```bash
   npm install @vercel/node
   ```
4. Create a `.env` file with your credentials (see Environment Variables section)
5. Run the webhook locally:
   ```bash
   # For development with hot-reload
   python -m hackrx_llm.webhook --serverless
   
   # Or for production-like environment
   FLASK_DEBUG=false python -m hackrx_llm.webhook --serverless
   ```

## Vercel Deployment

### Prerequisites
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Login to Vercel:
   ```bash
   vercel login
   ```

### Deployment Steps

1. **Link your project** (first time only):
   ```bash
   cd /path/to/your/project
   vercel link
   ```

2. **Set environment variables**:
   ```bash
   vercel env add GROQ_API_KEY production
   vercel env add API_AUTH_TOKEN production
   vercel env add PYTHON_VERSION production  # Set to 3.10.13
   ```

3. **Deploy to production**:
   ```bash
   vercel --prod
   ```

4. **For subsequent deployments**, just push to your connected Git repository or run:
   ```bash
   vercel --prod
   ```

### Manual Deployment via GitHub

1. Push your code to a GitHub repository
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New" > "Project"
4. Import your GitHub repository
5. Configure project settings:
   - Framework Preset: "Other"
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `public` (for static files)
   - Install Command: (leave blank)
6. Add environment variables in the Vercel dashboard:
   - `GROQ_API_KEY`: Your Groq API key
   - `API_AUTH_TOKEN`: Your secure token
   - `PYTHON_VERSION`: 3.10.13
   - `VERCEL`: 1
   - `PYTHONUNBUFFERED`: 1
7. Click "Deploy"

## Testing the Webhook

### Local Testing

```bash
# Health check
curl http://localhost:3000/api/webhook/health

# Test query
curl -X POST http://localhost:3000/api/webhook/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{
    "documents": "https://example.com/your-policy.pdf",
    "questions": ["What is the grace period?"],
    "model": "llama-3.3-70b-versatile"
  }'
```

### Production Testing

Replace `your-vercel-app.vercel.app` with your actual Vercel deployment URL:

```bash
# Health check
curl https://your-vercel-app.vercel.app/api/webhook/health

# Test query
curl -X POST https://your-vercel-app.vercel.app/api/webhook/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{
    "documents": "https://example.com/your-policy.pdf",
    "questions": ["What is the grace period?"],
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
