#!/usr/bin/env python3

"""
Test script for the comments functionality
"""

import json
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import Mock, patch
from unified_lambda import lambda_handler

def test_comments_functionality():
    """Test the complete comments functionality"""
    
    print("🧪 Testing Comments Functionality")
    print("=" * 50)
    
    # Mock S3 responses
    mock_s3_client = Mock()
    
    # Mock list_objects_v2 response
    mock_s3_client.list_objects_v2.return_value = {
        'Contents': [
            {
                'Key': 'pictures/test-image.jpg',
                'LastModified': datetime(2024, 1, 1, 0, 0, 0)
            }
        ]
    }
    
    # Mock head_object response (no existing comments)
    mock_s3_client.head_object.return_value = {
        'Metadata': {
            'original-name': 'test-image.jpg',
            'rating': '4'
        }
    }
    
    # Mock generate_presigned_url
    mock_s3_client.generate_presigned_url.return_value = 'https://example.com/test-image.jpg'
    
    # Mock copy_object (for updating metadata)
    mock_s3_client.copy_object.return_value = {}
    
    # Patch the S3 client
    with patch('unified_lambda.s3_client', mock_s3_client):
        
        # Test 1: Get pictures (should include empty comments array)
        print("1️⃣ Testing get_pictures with comments...")
        
        event = {
            'requestContext': {'http': {'method': 'GET'}},
            'rawPath': '/api/pictures'
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        pictures = body['pictures']
        
        assert len(pictures) == 1
        assert 'comments' in pictures[0]
        assert pictures[0]['comments'] == []
        assert pictures[0]['name'] == 'test-image.jpg'
        assert pictures[0]['rating'] == 4
        
        print("✅ get_pictures includes comments field")
        
        # Test 2: Add a comment
        print("2️⃣ Testing add_comment...")
        
        comment_event = {
            'requestContext': {'http': {'method': 'POST'}},
            'rawPath': '/api/pictures/comment',
            'body': json.dumps({
                'picture': 'test-image.jpg',
                'author': 'John Doe',
                'text': 'Beautiful sunset!'
            }),
            'isBase64Encoded': False
        }
        
        response = lambda_handler(comment_event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        
        assert body['message'] == 'Comment added successfully'
        assert 'comment' in body
        assert body['comment']['author'] == 'John Doe'
        assert body['comment']['text'] == 'Beautiful sunset!'
        assert 'date' in body['comment']
        
        print("✅ add_comment works correctly")
        
        # Verify copy_object was called with updated metadata
        mock_s3_client.copy_object.assert_called_once()
        call_args = mock_s3_client.copy_object.call_args
        
        # Check that metadata contains the new comment
        updated_metadata = call_args[1]['Metadata']
        assert 'comments' in updated_metadata
        
        comments_json = updated_metadata['comments']
        comments = json.loads(comments_json)
        
        assert len(comments) == 1
        assert comments[0]['author'] == 'John Doe'
        assert comments[0]['text'] == 'Beautiful sunset!'
        
        print("✅ S3 metadata updated correctly")
        
        # Test 3: Test with existing comments
        print("3️⃣ Testing add_comment with existing comments...")
        
        # Mock head_object to return existing comments
        existing_comments = [
            {
                'author': 'Jane Smith',
                'text': 'Great photo!',
                'date': '2024-01-01T10:00:00'
            }
        ]
        
        mock_s3_client.head_object.return_value = {
            'Metadata': {
                'original-name': 'test-image.jpg',
                'rating': '4',
                'comments': json.dumps(existing_comments)
            }
        }
        
        # Reset the mock
        mock_s3_client.copy_object.reset_mock()
        
        # Add another comment
        comment_event2 = {
            'requestContext': {'http': {'method': 'POST'}},
            'rawPath': '/api/pictures/comment',
            'body': json.dumps({
                'picture': 'test-image.jpg',
                'author': 'Bob Wilson',
                'text': 'Amazing colors!'
            }),
            'isBase64Encoded': False
        }
        
        response = lambda_handler(comment_event2, {})
        
        assert response['statusCode'] == 200
        
        # Verify both comments are preserved
        call_args = mock_s3_client.copy_object.call_args
        updated_metadata = call_args[1]['Metadata']
        comments_json = updated_metadata['comments']
        comments = json.loads(comments_json)
        
        assert len(comments) == 2
        assert comments[0]['author'] == 'Jane Smith'  # Existing comment
        assert comments[1]['author'] == 'Bob Wilson'  # New comment
        
        print("✅ Multiple comments handled correctly")
        
        # Test 4: Test error handling
        print("4️⃣ Testing error handling...")
        
        # Test missing fields
        invalid_event = {
            'requestContext': {'http': {'method': 'POST'}},
            'rawPath': '/api/pictures/comment',
            'body': json.dumps({
                'picture': 'test-image.jpg',
                'author': 'John Doe'
                # Missing 'text' field
            }),
            'isBase64Encoded': False
        }
        
        response = lambda_handler(invalid_event, {})
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Missing required fields' in body['error']
        
        print("✅ Error handling works correctly")
        
        # Test 5: Test frontend JavaScript functions (basic syntax check)
        print("5️⃣ Testing JavaScript functions...")
        
        js_event = {
            'requestContext': {'http': {'method': 'GET'}},
            'rawPath': '/script.js'
        }
        
        response = lambda_handler(js_event, {})
        
        assert response['statusCode'] == 200
        assert 'application/javascript' in response['headers']['Content-Type']
        
        js_content = response['body']
        
        # Check that our functions are included
        assert 'function toggleComments(' in js_content
        assert 'async function submitComment(' in js_content
        assert '/api/pictures/comment' in js_content
        
        print("✅ JavaScript functions included correctly")
        
        print("\n🎉 All tests passed! Comments functionality is working correctly.")
        print("\nFeatures tested:")
        print("  ✅ Comments field included in picture data")
        print("  ✅ Adding new comments via API")
        print("  ✅ Preserving existing comments")
        print("  ✅ S3 metadata storage")
        print("  ✅ Error handling")
        print("  ✅ JavaScript functions")

if __name__ == "__main__":
    test_comments_functionality()
