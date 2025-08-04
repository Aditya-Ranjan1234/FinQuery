"""Vercel serverless function handler for HackRx LLM application."""
import os
import sys
import json
from pathlib import Path
from werkzeug.wrappers import Response
from werkzeug.test import create_environ

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Import the Flask app from webapp
    from hackrx_llm.webapp import create_app
    
    # Create the Flask application
    app = create_app()
except Exception as e:
    print(f"Error creating Flask app: {str(e)}")
    raise

# Vercel serverless function handler
def handler(event, context):
    """
    Handle the incoming Vercel request.
    
    Args:
        event: The incoming request event
        context: The request context
        
    Returns:
        dict: The response to be returned to the client
    """
    try:
        # Create a test request environment from the event
        environ = create_environ(
            path=event.get('path', '/'),
            method=event.get('httpMethod', 'GET'),
            headers=dict(event.get('headers', {})),
            query_string=event.get('queryStringParameters', {}),
            data=event.get('body', ''),
            content_type=event.get('headers', {}).get('content-type', 'application/json'),
        )
        
        # Handle the request
        response = Response.from_app(app, environ)
        
        # Convert the response to the format expected by Vercel
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
        
    except Exception as e:
        print(f"Error handling request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }

# For local testing
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
