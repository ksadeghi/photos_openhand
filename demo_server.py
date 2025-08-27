

#!/usr/bin/env python3

"""
Local demo server for the Picture Gallery application
Runs without AWS dependencies for testing and demonstration
"""

import json
import base64
import uuid
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import time

# Import our Lambda functions
from frontend_lambda import lambda_handler as frontend_handler
from backend_lambda import lambda_handler as backend_handler

# Mock data storage (in-memory for demo)
MOCK_PICTURES = []
UPLOAD_DIR = "/tmp/demo_pictures"

class MockS3Client:
    """Mock S3 client for local testing"""
    
    def __init__(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    def list_objects_v2(self, Bucket):
        """Mock list objects"""
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                files.append({
                    'Key': filename,
                    'LastModified': datetime.now()
                })
        
        return {'Contents': files} if files else {}
    
    def head_object(self, Bucket, Key):
        """Mock head object"""
        filepath = os.path.join(UPLOAD_DIR, Key)
        if os.path.exists(filepath):
            return {
                'Metadata': {
                    'picture_name': Key,
                    'picture_date': datetime.now().strftime('%Y-%m-%d')
                }
            }
        else:
            raise Exception("NoSuchKey")
    
    def generate_presigned_url(self, operation, Params, ExpiresIn):
        """Mock presigned URL generation"""
        return f"http://localhost:8000/image/{Params['Key']}"
    
    def put_object(self, Bucket, Key, Body, ContentType, Metadata):
        """Mock put object"""
        filepath = os.path.join(UPLOAD_DIR, Key)
        with open(filepath, 'wb') as f:
            f.write(Body)
        
        # Store metadata
        MOCK_PICTURES.append({
            'id': Key,
            'picture_name': Metadata.get('picture_name', Key),
            'picture_date': Metadata.get('picture_date', datetime.now().strftime('%Y-%m-%d')),
            'filepath': filepath
        })

# Monkey patch the S3 client in backend_lambda
import backend_lambda
backend_lambda.s3_client = MockS3Client()

class DemoRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the demo server"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path.startswith('/image/'):
            # Serve uploaded images
            self.serve_image(path[7:])  # Remove '/image/' prefix
        elif path.startswith('/api/'):
            # Handle API requests
            self.handle_api_request('GET', path[4:], query_params)
        else:
            # Handle frontend requests
            self.handle_frontend_request(path)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/'):
            self.handle_api_request('POST', path[4:])
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def serve_image(self, filename):
        """Serve an uploaded image"""
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        if os.path.exists(filepath):
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)
    
    def handle_frontend_request(self, path):
        """Handle frontend requests using the frontend Lambda"""
        event = {
            'rawPath': path,
            'requestContext': {
                'http': {
                    'method': 'GET'
                }
            }
        }
        
        response = frontend_handler(event, {})
        
        self.send_response(response['statusCode'])
        
        # Set headers
        for header, value in response.get('headers', {}).items():
            self.send_header(header, value)
        
        self.end_headers()
        
        # Send body
        body = response.get('body', '')
        if isinstance(body, str):
            # Update API base URL for local demo
            body = body.replace(
                'https://your-backend-lambda-url.lambda-url.region.on.aws',
                'http://localhost:8000/api'
            )
            self.wfile.write(body.encode())
    
    def handle_api_request(self, method, path, query_params=None):
        """Handle API requests using the backend Lambda"""
        
        # Read request body for POST requests
        body = b''
        if method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
        
        # Build Lambda event with proper headers
        headers_dict = {}
        for header_name, header_value in self.headers.items():
            headers_dict[header_name.lower()] = header_value
        
        event = {
            'requestContext': {
                'http': {
                    'method': method
                }
            },
            'rawPath': path,
            'headers': headers_dict,
            'queryStringParameters': {k: v[0] for k, v in (query_params or {}).items()},
            'body': base64.b64encode(body).decode() if body else '',
            'isBase64Encoded': bool(body)
        }
        
        response = backend_handler(event, {})
        
        self.send_response(response['statusCode'])
        
        # Set headers
        for header, value in response.get('headers', {}).items():
            self.send_header(header, value)
        
        self.end_headers()
        
        # Send body
        response_body = response.get('body', '')
        if isinstance(response_body, str):
            self.wfile.write(response_body.encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def start_demo_server(port=8000):
    """Start the demo server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DemoRequestHandler)
    
    print(f"🚀 Starting Picture Gallery Demo Server on http://localhost:{port}")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print("🌐 Opening browser...")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo server...")
        httpd.shutdown()

if __name__ == "__main__":
    start_demo_server()

