#!/usr/bin/env python3

"""
Test script for bulk download functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import base64
import zipfile
import io
from unified_lambda import download_pictures

class TestDownloadFunctionality(unittest.TestCase):
    
    @patch('unified_lambda.s3_client')
    def test_download_pictures_success(self, mock_s3):
        """Test successful download of multiple pictures"""
        
        # Mock S3 responses
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'pictures/20240101_123456_abc123.jpg'},
                {'Key': 'pictures/20240102_234567_def456.png'}
            ]
        }
        
        # Mock head_object responses for metadata
        def mock_head_object(Bucket, Key):
            if 'abc123.jpg' in Key:
                return {'Metadata': {'original-name': 'sunset.jpg'}}
            elif 'def456.png' in Key:
                return {'Metadata': {'original-name': 'mountain.png'}}
            return {'Metadata': {}}
        
        mock_s3.head_object.side_effect = mock_head_object
        
        # Mock get_object responses for actual image data
        def mock_get_object(Bucket, Key):
            mock_body = Mock()
            if 'abc123.jpg' in Key:
                mock_body.read.return_value = b'fake_jpg_data'
            elif 'def456.png' in Key:
                mock_body.read.return_value = b'fake_png_data'
            return {'Body': mock_body}
        
        mock_s3.get_object.side_effect = mock_get_object
        
        # Create test event
        event = {
            'body': json.dumps({
                'pictures': ['sunset.jpg', 'mountain.png']
            })
        }
        
        # Call the function
        response = download_pictures(event)
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers']['Content-Type'], 'application/zip')
        self.assertTrue(response['isBase64Encoded'])
        
        # Decode and verify ZIP content
        zip_data = base64.b64decode(response['body'])
        zip_buffer = io.BytesIO(zip_data)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            file_list = zip_file.namelist()
            self.assertIn('sunset.jpg', file_list)
            self.assertIn('mountain.png', file_list)
            
            # Verify file contents
            self.assertEqual(zip_file.read('sunset.jpg'), b'fake_jpg_data')
            self.assertEqual(zip_file.read('mountain.png'), b'fake_png_data')
    
    def test_download_no_pictures_specified(self):
        """Test error when no pictures are specified"""
        event = {
            'body': json.dumps({
                'pictures': []
            })
        }
        
        response = download_pictures(event)
        
        self.assertEqual(response['statusCode'], 400)
        error_data = json.loads(response['body'])
        self.assertIn('No pictures specified', error_data['error'])
    
    @patch('unified_lambda.s3_client')
    def test_download_pictures_not_found(self, mock_s3):
        """Test when requested pictures are not found"""
        
        # Mock empty S3 response
        mock_s3.list_objects_v2.return_value = {
            'Contents': []
        }
        
        event = {
            'body': json.dumps({
                'pictures': ['nonexistent.jpg']
            })
        }
        
        response = download_pictures(event)
        
        self.assertEqual(response['statusCode'], 404)
        error_data = json.loads(response['body'])
        self.assertIn('None of the requested pictures were found', error_data['error'])

def run_tests():
    """Run the download functionality tests"""
    print("🧪 Testing bulk download functionality...")
    
    # Run tests
    unittest.main(argv=[''], exit=False, verbosity=2)

if __name__ == '__main__':
    run_tests()
