#!/usr/bin/env python3

"""
Demo server for the unified Picture Gallery application
Shows the complete comments functionality
"""

import json
import os
import tempfile
import shutil
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import time
from unittest.mock import Mock

# Import our unified Lambda function
from unified_lambda import lambda_handler

# Mock data storage (in-memory for demo)
UPLOAD_DIR = "/tmp/demo_pictures"
MOCK_PICTURES_DATA = {}

class MockS3Client:
    """Mock S3 client for local testing with comments support"""
    
    def __init__(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        # Add some sample pictures with comments
        self.setup_sample_data()
    
    def setup_sample_data(self):
        """Setup sample pictures with comments for demo"""
        sample_pictures = [
            {
                'filename': 'sunset.jpg',
                'metadata': {
                    'original-name': 'Beautiful Sunset.jpg',
                    'rating': '5',
                    'comments': json.dumps([
                        {
                            'author': 'Alice Johnson',
                            'text': 'Absolutely stunning! The colors are incredible.',
                            'date': '2024-01-15T10:30:00'
                        },
                        {
                            'author': 'Bob Smith',
                            'text': 'Perfect timing for this shot!',
                            'date': '2024-01-16T14:20:00'
                        }
                    ])
                }
            },
            {
                'filename': 'mountain.jpg',
                'metadata': {
                    'original-name': 'Mountain View.jpg',
                    'rating': '4',
                    'comments': json.dumps([
                        {
                            'author': 'Carol Davis',
                            'text': 'Love the composition and depth.',
                            'date': '2024-01-17T09:15:00'
                        }
                    ])
                }
            },
            {
                'filename': 'beach.jpg',
                'metadata': {
                    'original-name': 'Beach Paradise.jpg',
                    'rating': '3',
                    'comments': json.dumps([])  # No comments yet
                }
            }
        ]
        
        for pic in sample_pictures:
            MOCK_PICTURES_DATA[f"pictures/{pic['filename']}"] = pic['metadata']
            # Create a placeholder image file
            filepath = os.path.join(UPLOAD_DIR, pic['filename'])
            with open(filepath, 'w') as f:
                f.write(f"Mock image: {pic['filename']}")
    
    def list_objects_v2(self, Bucket, Prefix=''):
        """Mock list objects"""
        files = []
        for key in MOCK_PICTURES_DATA.keys():
            if key.startswith(Prefix):
                files.append({
                    'Key': key,
                    'LastModified': datetime(2024, 1, 15, 12, 0, 0)
                })
        
        return {'Contents': files} if files else {}
    
    def head_object(self, Bucket, Key):
        """Mock head object"""
        if Key in MOCK_PICTURES_DATA:
            return {'Metadata': MOCK_PICTURES_DATA[Key].copy()}
        else:
            raise Exception("NoSuchKey")
    
    def generate_presigned_url(self, operation, Params, ExpiresIn):
        """Mock presigned URL generation"""
        filename = Params['Key'].split('/')[-1]
        return f"http://localhost:8000/image/{filename}"
    
    def copy_object(self, Bucket, CopySource, Key, Metadata, MetadataDirective):
        """Mock copy object (for updating metadata)"""
        MOCK_PICTURES_DATA[Key] = Metadata.copy()
        print(f"📝 Updated metadata for {Key}")

# Monkey patch the S3 client in unified_lambda
import unified_lambda
unified_lambda.s3_client = MockS3Client()

class DemoRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the demo server"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path.startswith('/image/'):
            # Serve mock images
            self.serve_mock_image(path[7:])  # Remove '/image/' prefix
        else:
            # Handle all requests through unified Lambda
            self.handle_lambda_request('GET', path, query_params)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        self.handle_lambda_request('POST', path)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def serve_mock_image(self, filename):
        """Serve a mock image"""
        self.send_response(200)
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Send a simple mock image response
        mock_image_data = f"🖼️ Mock Image: {filename}".encode()
        self.wfile.write(mock_image_data)
    
    def handle_lambda_request(self, method, path, query_params=None):
        """Handle requests using the unified Lambda"""
        
        # Read request body for POST requests
        body = b''
        if method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
        
        # Build Lambda event
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
            'body': body.decode() if body else '',
            'isBase64Encoded': False
        }
        
        response = lambda_handler(event, {})
        
        self.send_response(response['statusCode'])
        
        # Set headers
        for header, value in response.get('headers', {}).items():
            self.send_header(header, value)
        
        self.end_headers()
        
        # Send body
        response_body = response.get('body', '')
        if isinstance(response_body, str):
            # Update API base URL for local demo
            response_body = response_body.replace(
                'window.location.origin',
                '"http://localhost:8000"'
            )
            self.wfile.write(response_body.encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        if 'image/' not in args[0]:  # Don't log image requests
            print(f"🌐 {format % args}")

def start_demo_server(port=8000):
    """Start the demo server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DemoRequestHandler)
    
    print("🎨 Picture Gallery with Comments - Demo Server")
    print("=" * 50)
    print(f"🚀 Server running on http://localhost:{port}")
    print(f"📁 Mock upload directory: {UPLOAD_DIR}")
    print("\n📸 Sample pictures with comments loaded:")
    print("  • Beautiful Sunset.jpg (5⭐, 2 comments)")
    print("  • Mountain View.jpg (4⭐, 1 comment)")
    print("  • Beach Paradise.jpg (3⭐, 0 comments)")
    print("\n✨ Features to test:")
    print("  • View existing comments by clicking comment buttons")
    print("  • Add new comments with your name")
    print("  • Rate pictures (1-5 stars)")
    print("  • Comments persist and display with author/date")
    print("\n🌐 Opening browser...")
    
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

