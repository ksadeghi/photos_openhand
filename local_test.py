
#!/usr/bin/env python3

"""
Local testing script for the Picture Gallery Lambda functions
"""

import json
import base64
from frontend_lambda import lambda_handler as frontend_handler
from backend_lambda import lambda_handler as backend_handler

def test_frontend():
    """Test the frontend Lambda function"""
    print("🧪 Testing Frontend Lambda Function...")
    
    # Test main page
    event = {
        'rawPath': '/',
        'requestContext': {
            'http': {
                'method': 'GET'
            }
        }
    }
    
    response = frontend_handler(event, {})
    print(f"✅ Main page status: {response['statusCode']}")
    
    # Test CSS
    event['rawPath'] = '/style.css'
    response = frontend_handler(event, {})
    print(f"✅ CSS status: {response['statusCode']}")
    
    # Test JavaScript
    event['rawPath'] = '/script.js'
    response = frontend_handler(event, {})
    print(f"✅ JavaScript status: {response['statusCode']}")
    
    # Test 404
    event['rawPath'] = '/nonexistent'
    response = frontend_handler(event, {})
    print(f"✅ 404 page status: {response['statusCode']}")

def test_backend():
    """Test the backend Lambda function"""
    print("\n🧪 Testing Backend Lambda Function...")
    
    # Test CORS preflight
    event = {
        'requestContext': {
            'http': {
                'method': 'OPTIONS'
            }
        },
        'rawPath': '/pictures'
    }
    
    response = backend_handler(event, {})
    print(f"✅ CORS preflight status: {response['statusCode']}")
    
    # Test get pictures (will fail without S3 setup, but should handle gracefully)
    event = {
        'requestContext': {
            'http': {
                'method': 'GET'
            }
        },
        'rawPath': '/pictures',
        'queryStringParameters': None
    }
    
    try:
        response = backend_handler(event, {})
        print(f"✅ Get pictures status: {response['statusCode']}")
    except Exception as e:
        print(f"⚠️  Get pictures failed (expected without AWS setup): {str(e)}")
    
    # Test invalid endpoint
    event['rawPath'] = '/invalid'
    response = backend_handler(event, {})
    print(f"✅ Invalid endpoint status: {response['statusCode']}")

def create_sample_upload_event():
    """Create a sample multipart upload event for testing"""
    
    # Sample image data (1x1 pixel PNG)
    sample_image = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
    )
    
    # Create multipart form data
    boundary = 'boundary123456789'
    
    form_data = f'''--{boundary}\r
Content-Disposition: form-data; name="picture_name"\r
\r
test_picture.png\r
--{boundary}\r
Content-Disposition: form-data; name="picture_date"\r
\r
2024-01-01\r
--{boundary}\r
Content-Disposition: form-data; name="file"; filename="test.png"\r
Content-Type: image/png\r
\r
'''.encode() + sample_image + f'\r\n--{boundary}--\r\n'.encode()
    
    event = {
        'requestContext': {
            'http': {
                'method': 'POST'
            }
        },
        'rawPath': '/upload',
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': base64.b64encode(form_data).decode(),
        'isBase64Encoded': True
    }
    
    return event

def test_upload():
    """Test the upload functionality"""
    print("\n🧪 Testing Upload Functionality...")
    
    event = create_sample_upload_event()
    
    try:
        response = backend_handler(event, {})
        print(f"✅ Upload test status: {response['statusCode']}")
        if response['statusCode'] != 201:
            print(f"   Response: {response.get('body', 'No body')}")
    except Exception as e:
        print(f"⚠️  Upload test failed (expected without AWS setup): {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting Local Tests for Picture Gallery Lambda Functions\n")
    
    test_frontend()
    test_backend()
    test_upload()
    
    print("\n✅ Local testing completed!")
    print("\n📝 Note: Some backend tests may fail without proper AWS configuration.")
    print("   This is expected when running locally without S3 access.")

if __name__ == "__main__":
    main()
