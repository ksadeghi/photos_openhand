
import json
import boto3
import base64
import uuid
from datetime import datetime
import zipfile
import io
import os

# Initialize AWS clients
s3_client = boto3.client('s3')

# Configuration
PICTURES_BUCKET = os.environ.get('PICTURES_BUCKET', 'photos-openhand-bucket')

def lambda_handler(event, context):
    """
    Backend-only Lambda handler for API endpoints
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
        
        # Route API requests only
        if path == '/api/pictures' and method == 'GET':
            return get_pictures()
        elif path == '/api/pictures' and method == 'POST':
            return upload_picture(event)
        elif path == '/api/pictures' and method == 'DELETE':
            return delete_pictures(event)
        elif path == '/api/pictures/rate' and method == 'POST':
            return rate_picture(event)
        elif path == '/api/pictures/comment' and method == 'POST':
            return add_comment(event)
        elif path == '/api/pictures/download' and method == 'POST':
            return download_pictures(event)
        elif path == '/api/stats' and method == 'GET':
            return get_stats()
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
        'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

def cors_response():
    """Handle CORS preflight requests"""
    return {
        'statusCode': 200,
        'headers': get_cors_headers(),
        'body': ''
    }

def get_pictures():
    """Get list of pictures from S3"""
    try:
        print(f"Getting pictures from bucket: {PICTURES_BUCKET}")
        
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        print(f"S3 response keys: {list(response.keys())}")
        
        pictures = []
        if 'Contents' in response:
            print(f"Found {len(response['Contents'])} objects")
            for obj in response['Contents']:
                print(f"Processing object: {obj['Key']}")
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    try:
                        # Get object metadata
                        head_response = s3_client.head_object(
                            Bucket=PICTURES_BUCKET,
                            Key=obj['Key']
                        )
                        
                        metadata = head_response.get('Metadata', {})
                        
                        # Generate presigned URL for the image
                        url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': PICTURES_BUCKET, 'Key': obj['Key']},
                            ExpiresIn=3600  # 1 hour
                        )
                        
                        # Parse comments from metadata
                        comments = []
                        if 'comments' in metadata:
                            try:
                                comments = json.loads(metadata['comments'])
                            except:
                                comments = []
                        
                        picture = {
                            'name': metadata.get('original-name', obj['Key'].split('/')[-1]),
                            'url': url,
                            'date': obj['LastModified'].isoformat(),
                            'size': obj['Size'],
                            'rating': int(metadata.get('rating', 0)),
                            'comments': comments
                        }
                        
                        pictures.append(picture)
                        print(f"Added picture: {picture['name']}")
                        
                    except Exception as e:
                        print(f"Error processing {obj['Key']}: {str(e)}")
                        continue
        
        print(f"Returning {len(pictures)} pictures")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(pictures)
        }
        
    except Exception as e:
        print(f"Error getting pictures: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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
        
        # Use original image data (no processing to avoid PIL dependency)
        processed_image_bytes = image_bytes
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = picture_name.split('.')[-1] if '.' in picture_name else 'jpg'
        s3_key = f"pictures/{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        print(f"Uploading to S3: {s3_key}")
        
        # Upload to S3 with metadata
        s3_client.put_object(
            Bucket=PICTURES_BUCKET,
            Key=s3_key,
            Body=processed_image_bytes,
            ContentType=content_type,
            Metadata={
                'original-name': picture_name,
                'upload-date': datetime.now().isoformat(),
                'rating': '0',
                'comments': '[]'
            }
        )
        
        print(f"Successfully uploaded: {s3_key}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Picture uploaded successfully',
                'key': s3_key,
                'originalName': picture_name
            })
        }
        
    except Exception as e:
        print(f"Error uploading picture: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to upload picture: {str(e)}'})
        }

def delete_pictures(event):
    """Delete multiple pictures from S3"""
    try:
        # Parse the request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        data = json.loads(body)
        picture_names = data.get('pictures', [])
        
        if not picture_names:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No pictures specified for deletion'})
            }
        
        print(f"Deleting pictures: {picture_names}")
        
        # Get list of all objects in S3
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        if 'Contents' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No pictures found'})
            }
        
        # Find and delete the specified pictures
        deleted_count = 0
        for picture_name in picture_names:
            # Find the S3 key for this picture name
            for obj in response['Contents']:
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    try:
                        # Get metadata to check original name
                        head_response = s3_client.head_object(
                            Bucket=PICTURES_BUCKET,
                            Key=obj['Key']
                        )
                        metadata = head_response.get('Metadata', {})
                        original_name = metadata.get('original-name', obj['Key'].split('/')[-1])
                        
                        if original_name == picture_name:
                            # Delete the object
                            s3_client.delete_object(
                                Bucket=PICTURES_BUCKET,
                                Key=obj['Key']
                            )
                            print(f"Deleted: {obj['Key']}")
                            deleted_count += 1
                            break
                    except Exception as e:
                        print(f"Error checking/deleting {obj['Key']}: {e}")
                        continue
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': f'Successfully deleted {deleted_count} picture(s)',
                'deletedCount': deleted_count
            })
        }
        
    except Exception as e:
        print(f"Error deleting pictures: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to delete pictures: {str(e)}'})
        }

def rate_picture(event):
    """Rate a picture by updating S3 object metadata"""
    try:
        # Parse the request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')

        data = json.loads(body)
        picture_name = data.get('picture')
        rating = data.get('rating')

        if not picture_name or rating is None:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Picture name and rating are required'})
            }

        if not (1 <= rating <= 5):
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Rating must be between 1 and 5'})
            }

        print(f"Rating picture {picture_name} with {rating} stars")

        # Find the picture in S3
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )

        target_key = None
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Get metadata to check original name
                    try:
                        head_response = s3_client.head_object(
                            Bucket=PICTURES_BUCKET,
                            Key=obj['Key']
                        )
                        metadata = head_response.get('Metadata', {})
                        original_name = metadata.get('original-name', obj['Key'].split('/')[-1])

                        if original_name == picture_name:
                            target_key = obj['Key']
                            break
                    except Exception as e:
                        print(f"Error checking metadata for {obj['Key']}: {e}")
                        continue

        if not target_key:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Picture not found'})
            }

        # Get current metadata
        head_response = s3_client.head_object(
            Bucket=PICTURES_BUCKET,
            Key=target_key
        )
        
        current_metadata = head_response.get('Metadata', {})
        current_metadata['rating'] = str(rating)

        # Copy object with updated metadata
        s3_client.copy_object(
            Bucket=PICTURES_BUCKET,
            Key=target_key,
            CopySource={'Bucket': PICTURES_BUCKET, 'Key': target_key},
            Metadata=current_metadata,
            MetadataDirective='REPLACE'
        )

        print(f"Successfully rated {picture_name} with {rating} stars")

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Rating saved successfully',
                'picture': picture_name,
                'rating': rating
            })
        }
        
    except Exception as e:
        print(f"Error rating picture: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to rate picture: {str(e)}'})
        }

def add_comment(event):
    """Add a comment to a picture by updating S3 object metadata"""
    try:
        # Parse the request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')

        data = json.loads(body)
        picture_name = data.get('picture')
        author = data.get('author')
        comment_text = data.get('text')

        if not all([picture_name, author, comment_text]):
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Picture name, author, and comment text are required'})
            }

        print(f"Adding comment to {picture_name} by {author}")

        # Find the picture in S3
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )

        target_key = None
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Get metadata to check original name
                    try:
                        head_response = s3_client.head_object(
                            Bucket=PICTURES_BUCKET,
                            Key=obj['Key']
                        )
                        metadata = head_response.get('Metadata', {})
                        original_name = metadata.get('original-name', obj['Key'].split('/')[-1])

                        if original_name == picture_name:
                            target_key = obj['Key']
                            break
                    except Exception as e:
                        print(f"Error checking metadata for {obj['Key']}: {e}")
                        continue

        if not target_key:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Picture not found'})
            }

        # Get current metadata
        head_response = s3_client.head_object(
            Bucket=PICTURES_BUCKET,
            Key=target_key
        )
        
        current_metadata = head_response.get('Metadata', {})
        
        # Parse existing comments
        existing_comments = []
        if 'comments' in current_metadata:
            try:
                existing_comments = json.loads(current_metadata['comments'])
            except:
                existing_comments = []

        # Add new comment
        new_comment = {
            'author': author,
            'text': comment_text,
            'date': datetime.now().isoformat()
        }
        existing_comments.append(new_comment)

        # Update metadata
        current_metadata['comments'] = json.dumps(existing_comments)

        # Copy object with updated metadata
        s3_client.copy_object(
            Bucket=PICTURES_BUCKET,
            Key=target_key,
            CopySource={'Bucket': PICTURES_BUCKET, 'Key': target_key},
            Metadata=current_metadata,
            MetadataDirective='REPLACE'
        )

        print(f"Successfully added comment to {picture_name}")

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Comment added successfully',
                'comment': new_comment
            })
        }
        
    except Exception as e:
        print(f"Error adding comment: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to add comment: {str(e)}'})
        }

def download_pictures(event):
    """Create and return a ZIP file containing selected pictures"""
    try:
        # Parse the request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        data = json.loads(body)
        picture_names = data.get('pictures', [])
        
        if not picture_names:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No pictures specified for download'})
            }
        
        print(f"Creating ZIP for {len(picture_names)} pictures: {picture_names}")
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get list of all objects in S3
            response = s3_client.list_objects_v2(
                Bucket=PICTURES_BUCKET,
                Prefix='pictures/'
            )
            
            if 'Contents' not in response:
                return {
                    'statusCode': 404,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': 'No pictures found'})
                }
            
            found_pictures = 0
            for picture_name in picture_names:
                # Find the S3 key for this picture name
                target_key = None
                for obj in response['Contents']:
                    if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        try:
                            # Get metadata to check original name
                            head_response = s3_client.head_object(
                                Bucket=PICTURES_BUCKET,
                                Key=obj['Key']
                            )
                            metadata = head_response.get('Metadata', {})
                            original_name = metadata.get('original-name', obj['Key'].split('/')[-1])
                            
                            if original_name == picture_name:
                                target_key = obj['Key']
                                break
                        except Exception as e:
                            print(f"Error checking metadata for {obj['Key']}: {e}")
                            continue
                
                if target_key:
                    try:
                        # Download the picture from S3
                        print(f"Downloading {target_key} for {picture_name}")
                        obj_response = s3_client.get_object(
                            Bucket=PICTURES_BUCKET,
                            Key=target_key
                        )
                        
                        # Add to ZIP file with original name
                        zip_file.writestr(picture_name, obj_response['Body'].read())
                        found_pictures += 1
                        print(f"Added {picture_name} to ZIP")
                        
                    except Exception as e:
                        print(f"Error downloading {target_key}: {e}")
                        continue
                else:
                    print(f"Picture not found: {picture_name}")
        
        if found_pictures == 0:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'None of the requested pictures were found'})
            }
        
        # Get ZIP data
        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()
        
        print(f"Created ZIP file with {found_pictures} pictures, size: {len(zip_data)} bytes")
        
        # Return ZIP file as binary response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/zip',
                'Content-Disposition': f'attachment; filename="photos_{datetime.now().strftime("%Y%m%d")}.zip"',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': base64.b64encode(zip_data).decode('utf-8'),
            'isBase64Encoded': True
        }
        
    except Exception as e:
        print(f"Error creating download ZIP: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to create download: {str(e)}'})
        }

def get_stats():
    """Get gallery statistics"""
    try:
        print("Getting gallery statistics")
        
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        total_pictures = 0
        total_size = 0
        total_rating = 0
        rated_pictures = 0
        total_comments = 0
        most_recent_date = None
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    total_pictures += 1
                    total_size += obj['Size']
                    
                    # Track most recent upload
                    if most_recent_date is None or obj['LastModified'] > most_recent_date:
                        most_recent_date = obj['LastModified']
                    
                    try:
                        # Get metadata for rating and comments
                        head_response = s3_client.head_object(
                            Bucket=PICTURES_BUCKET,
                            Key=obj['Key']
                        )
                        metadata = head_response.get('Metadata', {})
                        
                        # Count ratings
                        rating = int(metadata.get('rating', 0))
                        if rating > 0:
                            total_rating += rating
                            rated_pictures += 1
                        
                        # Count comments
                        if 'comments' in metadata:
                            try:
                                comments = json.loads(metadata['comments'])
                                total_comments += len(comments)
                            except:
                                pass
                                
                    except Exception as e:
                        print(f"Error getting metadata for {obj['Key']}: {e}")
                        continue
        
        # Calculate averages
        average_rating = round(total_rating / rated_pictures, 1) if rated_pictures > 0 else 0
        
        # Format total size
        if total_size < 1024:
            size_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        
        # Format most recent date
        most_recent_str = most_recent_date.strftime('%Y-%m-%d') if most_recent_date else 'Never'
        
        stats = {
            'totalPictures': total_pictures,
            'totalSize': size_str,
            'averageRating': average_rating,
            'totalComments': total_comments,
            'mostRecentUpload': most_recent_str
        }
        
        print(f"Stats: {stats}")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(stats)
        }
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to get stats: {str(e)}'})
        }

