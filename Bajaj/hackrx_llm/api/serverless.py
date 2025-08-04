from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from webapp
from hackrx_llm.webapp import app as application

# Vercel serverless function handler
def handler(event, context):
    # Convert Vercel event to WSGI environment
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'PATH_INFO': event['path'],
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'SERVER_NAME': 'vercel',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add headers
    if 'headers' in event:
        for key, value in event['headers'].items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = 'HTTP_' + key
            environ[key] = value
    
    # Handle body
    if event.get('body'):
        environ['wsgi.input'] = event['body']
    if event.get('isBase64Encoded', False):
        import base64
        environ['wsgi.input'] = base64.b64decode(environ['wsgi.input'])
    
    # Call the Flask app
    from io import StringIO
    from werkzeug.wrappers import Response
    from werkzeug.test import create_environ
    
    response = Response.from_app(application, environ)
    
    # Convert response to Vercel format
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }

# For local testing
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 3000, application)
