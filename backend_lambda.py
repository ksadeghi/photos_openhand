
import json
import boto3
import base64
import uuid
from datetime import datetime
from io import BytesIO
from PIL import Image
import os
from urllib.parse import parse_qs

# Initialize AWS clients
s3_client = boto3.client('s3')

# Configuration - Replace with your actual S3 bucket names
PICTURES_BUCKET = os.environ.get('PICTURES_BUCKET', 'your-pictures-bucket')
ICEBERG_BUCKET = os.environ.get('ICEBERG_BUCKET', 'your-iceberg-bucket')
ICEBERG_TABLE_PATH = os.environ.get('ICEBERG_TABLE_PATH', 'pictures_table')

def lambda_handler(event, context):
    """
    Main Lambda handler for the backend API
    """
    
    # Handle CORS preflight requests
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return cors_response()
    
    # Get the HTTP method and path
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    path = event.get('rawPath', '/')
    
    try:
        if method == 'GET' and path == '/pictures':
            return get_pictures(event)
        elif method == 'POST' and path == '/upload':
            return upload_picture(event)
        elif method == 'GET' and path.startswith('/picture/'):
            return get_picture_by_id(event)
        else:
            return error_response(404, 'Endpoint not found')
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')

def cors_response(status_code=200, body=None):
    """Return a CORS-enabled response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With'
        },
        'body': json.dumps(body) if body else ''
    }

def error_response(status_code, message):
    """Return an error response"""
    return cors_response(status_code, {'error': message})

def get_pictures(event):
    """
    Get pictures from the Iceberg table with optional filtering
    """
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        date_filter = query_params.get('date')
        name_filter = query_params.get('name')
        
        # For now, we'll simulate the Iceberg query with S3 metadata
        # In a real implementation, you would use PyIceberg to query the table
        pictures = get_pictures_from_s3(date_filter, name_filter)
        
        return cors_response(200, {
            'pictures': pictures,
            'count': len(pictures)
        })
        
    except Exception as e:
        print(f"Error getting pictures: {str(e)}")
        return error_response(500, f'Error retrieving pictures: {str(e)}')

def get_pictures_from_s3(date_filter=None, name_filter=None):
    """
    Get pictures metadata from S3 (simulating Iceberg table)
    In a real implementation, this would query the Iceberg table
    """
    try:
        # List objects in the pictures bucket
        response = s3_client.list_objects_v2(Bucket=PICTURES_BUCKET)
        pictures = []
        
        if 'Contents' not in response:
            return pictures
        
        for obj in response['Contents']:
            key = obj['Key']
            
            # Skip non-image files
            if not key.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                continue
            
            # Get object metadata
            try:
                metadata_response = s3_client.head_object(Bucket=PICTURES_BUCKET, Key=key)
                metadata = metadata_response.get('Metadata', {})
                
                picture_name = metadata.get('picture_name', key)
                picture_date = metadata.get('picture_date', obj['LastModified'].strftime('%Y-%m-%d'))
                
                # Apply filters
                if date_filter and picture_date != date_filter:
                    continue
                
                if name_filter and name_filter.lower() not in picture_name.lower():
                    continue
                
                # Generate presigned URL for the image
                jpg_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': PICTURES_BUCKET, 'Key': key},
                    ExpiresIn=3600  # 1 hour
                )
                
                pictures.append({
                    'id': key,
                    'picture_name': picture_name,
                    'picture_date': picture_date,
                    'jpg_url': jpg_url
                })
                
            except Exception as e:
                print(f"Error processing object {key}: {str(e)}")
                continue
        
        # Sort by date (newest first)
        pictures.sort(key=lambda x: x['picture_date'], reverse=True)
        
        return pictures
        
    except Exception as e:
        print(f"Error listing S3 objects: {str(e)}")
        return []

def upload_picture(event):
    """
    Upload a picture to S3 and update the Iceberg table
    """
    try:
        # Parse the multipart form data
        content_type = event.get('headers', {}).get('content-type', '')
        
        print(f"Upload request - Content-Type: {content_type}")
        
        if 'multipart/form-data' not in content_type:
            return error_response(400, 'Content-Type must be multipart/form-data')
        
        # Decode the body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            try:
                body = base64.b64decode(body)
            except Exception as e:
                return error_response(400, f'Failed to decode base64 body: {str(e)}')
        else:
            if isinstance(body, str):
                body = body.encode('utf-8')
        
        print(f"Body length: {len(body)} bytes")
        
        # Parse multipart data
        try:
            form_data = parse_multipart_form_data(body, content_type)
            print(f"Form data keys: {list(form_data.keys())}")
        except Exception as e:
            return error_response(400, f'Failed to parse form data: {str(e)}')
        
        if 'file' not in form_data:
            return error_response(400, f'No file provided. Available fields: {list(form_data.keys())}')
        
        file_data = form_data['file']
        picture_name = form_data.get('picture_name', f'picture_{uuid.uuid4().hex}')
        picture_date = form_data.get('picture_date', datetime.now().strftime('%Y-%m-%d'))
        
        print(f"File data length: {len(file_data)} bytes")
        print(f"Picture name: {picture_name}")
        print(f"Picture date: {picture_date}")
        
        # Process and validate the image
        try:
            image = Image.open(BytesIO(file_data))
            print(f"Image format: {image.format}, size: {image.size}, mode: {image.mode}")
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (optional)
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"Resized image to: {image.size}")
            
            # Save as JPEG
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            processed_image_data = output.getvalue()
            print(f"Processed image size: {len(processed_image_data)} bytes")
            
        except Exception as e:
            return error_response(400, f'Invalid image file: {str(e)}')
        
        # Generate unique filename
        file_extension = '.jpg'
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Upload to S3 (or save locally for demo)
        try:
            s3_client.put_object(
                Bucket=PICTURES_BUCKET,
                Key=unique_filename,
                Body=processed_image_data,
                ContentType='image/jpeg',
                Metadata={
                    'picture_name': picture_name,
                    'picture_date': picture_date,
                    'original_filename': picture_name
                }
            )
            
            print(f"Successfully uploaded: {unique_filename}")
            
            # In a real implementation, you would also insert into the Iceberg table here
            # insert_into_iceberg_table(unique_filename, picture_name, picture_date)
            
            return cors_response(201, {
                'message': 'Picture uploaded successfully',
                'id': unique_filename,
                'picture_name': picture_name,
                'picture_date': picture_date
            })
            
        except Exception as e:
            print(f"S3 upload error: {str(e)}")
            return error_response(500, f'Error uploading to S3: {str(e)}')
        
    except Exception as e:
        print(f"Error uploading picture: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(500, f'Error uploading picture: {str(e)}')

def get_picture_by_id(event):
    """
    Get a specific picture by ID
    """
    try:
        path = event.get('rawPath', '')
        picture_id = path.split('/')[-1]
        
        if not picture_id:
            return error_response(400, 'Picture ID is required')
        
        # Check if the object exists
        try:
            response = s3_client.head_object(Bucket=PICTURES_BUCKET, Key=picture_id)
            metadata = response.get('Metadata', {})
            
            # Generate presigned URL
            jpg_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': PICTURES_BUCKET, 'Key': picture_id},
                ExpiresIn=3600
            )
            
            return cors_response(200, {
                'id': picture_id,
                'picture_name': metadata.get('picture_name', picture_id),
                'picture_date': metadata.get('picture_date', ''),
                'jpg_url': jpg_url
            })
            
        except s3_client.exceptions.NoSuchKey:
            return error_response(404, 'Picture not found')
        
    except Exception as e:
        print(f"Error getting picture by ID: {str(e)}")
        return error_response(500, f'Error retrieving picture: {str(e)}')

def parse_multipart_form_data(body, content_type):
    """
    Simple multipart form data parser
    In production, use a proper library like python-multipart
    """
    try:
        # Extract boundary
        boundary = None
        for part in content_type.split(';'):
            if 'boundary=' in part:
                boundary = part.split('boundary=')[1].strip()
                break
        
        if not boundary:
            raise ValueError('No boundary found in Content-Type')
        
        # Convert body to bytes if it's a string
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        # Split by boundary
        boundary_bytes = f'--{boundary}'.encode()
        parts = body.split(boundary_bytes)
        form_data = {}
        
        for part in parts[1:-1]:  # Skip first empty part and last closing part
            if not part.strip():
                continue
            
            # Split headers and content
            header_end = part.find(b'\r\n\r\n')
            if header_end == -1:
                # Try with just \n\n
                header_end = part.find(b'\n\n')
                if header_end == -1:
                    continue
                headers = part[:header_end].decode('utf-8', errors='ignore')
                content = part[header_end + 2:]
            else:
                headers = part[:header_end].decode('utf-8', errors='ignore')
                content = part[header_end + 4:]
            
            # Remove trailing CRLF or LF
            if content.endswith(b'\r\n'):
                content = content[:-2]
            elif content.endswith(b'\n'):
                content = content[:-1]
            
            # Parse Content-Disposition header
            name = None
            for line in headers.split('\n'):
                line = line.strip()
                if line.startswith('Content-Disposition:'):
                    for param in line.split(';'):
                        param = param.strip()
                        if 'name=' in param:
                            name = param.split('name=')[1].strip().strip('"').strip("'")
                            break
                    break
            
            if name:
                if name == 'file':
                    form_data[name] = content
                else:
                    try:
                        form_data[name] = content.decode('utf-8')
                    except UnicodeDecodeError:
                        form_data[name] = content.decode('utf-8', errors='ignore')
        
        return form_data
        
    except Exception as e:
        print(f"Error parsing multipart data: {str(e)}")
        raise ValueError(f"Failed to parse multipart form data: {str(e)}")

def insert_into_iceberg_table(filename, picture_name, picture_date):
    """
    Insert record into Iceberg table
    This is a placeholder - implement with PyIceberg
    """
    # Example implementation with PyIceberg:
    # from pyiceberg.catalog import load_catalog
    # 
    # catalog = load_catalog("default")
    # table = catalog.load_table(f"{ICEBERG_BUCKET}.{ICEBERG_TABLE_PATH}")
    # 
    # table.append([{
    #     'picture_name': picture_name,
    #     'picture_date': picture_date,
    #     'picture_jpg': filename
    # }])
    
    pass

