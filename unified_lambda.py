import json
import base64
import os
import boto3
import uuid
from datetime import datetime
from io import BytesIO
from PIL import Image
from urllib.parse import parse_qs

# Initialize AWS clients
s3_client = boto3.client('s3')

# Configuration
PICTURES_BUCKET = os.environ.get('PICTURES_BUCKET', 'your-pictures-bucket')
ICEBERG_WAREHOUSE_PATH = os.environ.get('ICEBERG_WAREHOUSE_PATH', 'warehouse')

def lambda_handler(event, context):
    """
    Unified Lambda handler for both frontend and backend
    """
    try:
        # Log the incoming event for debugging
        print(f"Event: {json.dumps(event)}")
        
        # Get the path from the event
        path = event.get('rawPath', '/')
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        print(f"Path: {path}, Method: {method}")
        
        # Handle CORS preflight requests
        if method == 'OPTIONS':
            return cors_response()
        
        # Route requests
        if path == '/' or path == '/index.html':
            return serve_html()
        elif path == '/style.css':
            return serve_css()
        elif path == '/script.js':
            return serve_js()
        elif path == '/api/pictures' and method == 'GET':
            return get_pictures()
        elif path == '/api/pictures' and method == 'POST':
            return upload_picture(event)
        else:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        print(f"Lambda handler error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def get_cors_headers():
    """Get CORS headers"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

def cors_response():
    """Handle CORS preflight requests"""
    return {
        'statusCode': 200,
        'headers': get_cors_headers(),
        'body': ''
    }

def serve_html():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Picture Gallery</title>
        <link rel="stylesheet" href="/style.css">
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Picture Gallery</h1>
                <div class="upload-section">
                    <input type="file" id="fileInput" accept="image/*" multiple>
                    <button onclick="uploadPictures()">Upload Pictures</button>
                </div>
            </header>
            
            <main>
                <div id="loadingMessage" class="loading">Loading pictures...</div>
                <div id="errorMessage" class="error" style="display: none;"></div>
                <div id="gallery" class="gallery"></div>
            </main>
        </div>
        
        <script src="/script.js"></script>
    </body>
    </html>
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': html_content
    }

def serve_css():
    """Serve the CSS styles"""
    css_content = """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        color: #333;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }

    header {
        text-align: center;
        margin-bottom: 40px;
        background: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }

    h1 {
        color: #4a5568;
        margin-bottom: 20px;
        font-size: 2.5em;
        font-weight: 300;
    }

    .upload-section {
        display: flex;
        gap: 15px;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
    }

    input[type="file"] {
        padding: 10px;
        border: 2px dashed #667eea;
        border-radius: 8px;
        background: #f8f9ff;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    input[type="file"]:hover {
        border-color: #764ba2;
        background: #f0f2ff;
    }

    button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }

    .gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }

    .picture-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .picture-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }

    .picture-card img {
        width: 100%;
        height: 250px;
        object-fit: cover;
        cursor: pointer;
    }

    .picture-info {
        padding: 15px;
    }

    .picture-name {
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 5px;
    }

    .picture-date {
        color: #718096;
        font-size: 0.9em;
    }

    .loading, .error {
        text-align: center;
        padding: 40px;
        font-size: 1.2em;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        margin: 20px 0;
    }

    .loading {
        color: #667eea;
    }

    .error {
        color: #e53e3e;
        background: rgba(254, 226, 226, 0.9);
    }

    .success {
        color: #38a169;
        background: rgba(198, 246, 213, 0.9);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
    }

    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        
        h1 {
            font-size: 2em;
        }
        
        .upload-section {
            flex-direction: column;
        }
        
        .gallery {
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
    }
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/css',
            'Access-Control-Allow-Origin': '*'
        },
        'body': css_content
    }

def serve_js():
    """Serve the JavaScript code"""
    js_content = """
    // Configuration - API calls to same Lambda function
    const API_BASE_URL = window.location.origin;
    
    // Load pictures when page loads
    document.addEventListener('DOMContentLoaded', function() {
        loadPictures();
    });
    
    async function loadPictures() {
        const loadingMessage = document.getElementById('loadingMessage');
        const errorMessage = document.getElementById('errorMessage');
        const gallery = document.getElementById('gallery');
        
        try {
            loadingMessage.style.display = 'block';
            errorMessage.style.display = 'none';
            
            const response = await fetch(`${API_BASE_URL}/api/pictures`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            loadingMessage.style.display = 'none';
            
            if (data.pictures && data.pictures.length > 0) {
                displayPictures(data.pictures);
            } else {
                gallery.innerHTML = '<div class="loading">No pictures found. Upload some pictures to get started!</div>';
            }
            
        } catch (error) {
            console.error('Error loading pictures:', error);
            loadingMessage.style.display = 'none';
            errorMessage.textContent = `Error loading pictures: ${error.message}`;
            errorMessage.style.display = 'block';
        }
    }
    
    function displayPictures(pictures) {
        const gallery = document.getElementById('gallery');
        
        gallery.innerHTML = pictures.map(picture => `
            <div class="picture-card">
                <img src="${picture.url}" alt="${picture.name}" onclick="openFullSize('${picture.url}')">
                <div class="picture-info">
                    <div class="picture-name">${picture.name}</div>
                    <div class="picture-date">${new Date(picture.date).toLocaleDateString()}</div>
                </div>
            </div>
        `).join('');
    }
    
    function openFullSize(url) {
        window.open(url, '_blank');
    }
    
    async function uploadPictures() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;
        
        if (files.length === 0) {
            alert('Please select at least one file to upload.');
            return;
        }
        
        const uploadButton = document.querySelector('button');
        uploadButton.disabled = true;
        uploadButton.textContent = 'Uploading...';
        
        try {
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                await uploadSinglePicture(file);
            }
            
            // Show success message
            const successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.textContent = `Successfully uploaded ${files.length} picture(s)!`;
            document.querySelector('.container').insertBefore(successDiv, document.querySelector('main'));
            
            // Remove success message after 3 seconds
            setTimeout(() => {
                successDiv.remove();
            }, 3000);
            
            // Clear file input and reload pictures
            fileInput.value = '';
            loadPictures();
            
        } catch (error) {
            console.error('Upload error:', error);
            alert(`Upload failed: ${error.message}`);
        } finally {
            uploadButton.disabled = false;
            uploadButton.textContent = 'Upload Pictures';
        }
    }
    
    async function uploadSinglePicture(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = async function(e) {
                try {
                    const base64Data = e.target.result.split(',')[1];
                    
                    const uploadData = {
                        name: file.name,
                        data: base64Data,
                        contentType: file.type
                    };
                    
                    const response = await fetch(`${API_BASE_URL}/api/pictures`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(uploadData)
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    console.log('Upload successful:', result);
                    resolve(result);
                    
                } catch (error) {
                    console.error('Error uploading file:', error);
                    reject(error);
                }
            };
            
            reader.onerror = function() {
                reject(new Error('Error reading file'));
            };
            
            reader.readAsDataURL(file);
        });
    }
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/javascript',
            'Access-Control-Allow-Origin': '*'
        },
        'body': js_content
    }

def get_pictures():
    """Get list of pictures from S3"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        pictures = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Generate presigned URL for the image
                    url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': PICTURES_BUCKET, 'Key': obj['Key']},
                        ExpiresIn=3600  # 1 hour
                    )
                    
                    pictures.append({
                        'name': obj['Key'].split('/')[-1],
                        'date': obj['LastModified'].isoformat(),
                        'url': url
                    })
        
        # Sort by date (newest first)
        pictures.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'pictures': pictures,
                'count': len(pictures)
            })
        }
        
    except Exception as e:
        print(f"Error getting pictures: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to get pictures: {str(e)}'})
        }

def upload_picture(event):
    """Upload a picture to S3"""
    try:
        # Parse the request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        data = json.loads(body)
        
        # Extract picture data
        picture_name = data.get('name', f'picture_{uuid.uuid4().hex[:8]}.jpg')
        picture_data = data.get('data', '')
        content_type = data.get('contentType', 'image/jpeg')
        
        if not picture_data:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No picture data provided'})
            }
        
        # Decode base64 image data
        image_bytes = base64.b64decode(picture_data)
        
        # Process image with Pillow (optional: resize, optimize)
        try:
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 1920x1080)
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save processed image
            output_buffer = BytesIO()
            image.save(output_buffer, format='JPEG', quality=85, optimize=True)
            processed_image_bytes = output_buffer.getvalue()
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            # Use original image data if processing fails
            processed_image_bytes = image_bytes
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = picture_name.split('.')[-1] if '.' in picture_name else 'jpg'
        s3_key = f"pictures/{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=PICTURES_BUCKET,
            Key=s3_key,
            Body=processed_image_bytes,
            ContentType=content_type,
            Metadata={
                'original_name': picture_name,
                'upload_date': datetime.now().isoformat()
            }
        )
        
        # Store metadata in Iceberg table (simplified - just log for now)
        print(f"Picture uploaded: {s3_key}, original: {picture_name}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Picture uploaded successfully',
                'key': s3_key,
                'original_name': picture_name
            })
        }
        
    except Exception as e:
        print(f"Error uploading picture: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to upload picture: {str(e)}'})
        }
