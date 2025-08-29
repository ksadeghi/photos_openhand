import json
import base64
import os
import boto3
import uuid
from datetime import datetime
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
        elif path == '/api/pictures' and method == 'DELETE':
            return delete_pictures(event)
        elif path == '/api/pictures/rate' and method == 'POST':
            return rate_picture(event)
        elif path == '/api/pictures/comment' and method == 'POST':
            return add_comment(event)
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
                <button id="statsButton" class="stats-button" onclick="showStats()">📊 Stats</button>
                <button id="selectModeBtn" class="select-mode-button" onclick="enterSelectMode()">✓ Select</button>
                <div class="upload-section">
                    <input type="file" id="fileInput" accept="image/*" multiple>
                    <button onclick="uploadPictures()">Upload Pictures</button>
                </div>
                
                <div id="deleteSection" class="delete-section" style="display: none;">
                    <button id="selectAllBtn" onclick="toggleSelectAll()">Select All</button>
                    <button id="deleteSelectedBtn" onclick="deleteSelected()" class="delete-btn">🗑️ Delete Selected</button>
                    <button onclick="cancelSelection()" class="cancel-btn">Cancel</button>
                    <span id="selectedCount" class="selected-count">0 selected</span>
                </div>
            </header>
            
            <main>
                <div id="loadingMessage" class="loading">Loading pictures...</div>
                <div id="errorMessage" class="error" style="display: none;"></div>
                <div id="gallery" class="gallery"></div>
            </main>
        </div>
        
        <!-- Stats Modal -->
        <div id="statsModal" class="modal" style="display: none;">
            <div class="modal-content">
                <span class="close" onclick="closeStats()">&times;</span>
                <h2>📊 Gallery Statistics</h2>
                <div id="statsContent">
                    <div class="loading">Loading statistics...</div>
                </div>
            </div>
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
        position: relative;
    }

    .stats-button {
        position: absolute;
        top: 20px;
        right: 20px;
        background: #667eea;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .stats-button:hover {
        background: #5a67d8;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .select-mode-button {
        position: absolute;
        top: 20px;
        right: 120px;
        background: #48bb78;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.3);
    }

    .select-mode-button:hover {
        background: #38a169;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(72, 187, 120, 0.4);
    }

    .delete-section {
        display: flex;
        gap: 10px;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        flex-wrap: wrap;
    }

    .delete-btn {
        background: #e53e3e;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .delete-btn:hover {
        background: #c53030;
        transform: translateY(-2px);
    }

    .cancel-btn {
        background: #718096;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .cancel-btn:hover {
        background: #4a5568;
        transform: translateY(-2px);
    }

    .selected-count {
        font-weight: 600;
        color: #4a5568;
        margin-left: 10px;
    }

    .picture-item {
        position: relative;
    }

    .picture-checkbox {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 20px;
        height: 20px;
        cursor: pointer;
        z-index: 10;
        display: none;
    }

    .selection-mode .picture-checkbox {
        display: block;
    }

    .picture-item.selected {
        opacity: 0.7;
        transform: scale(0.95);
        transition: all 0.3s ease;
    }

    .picture-item.selected::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(72, 187, 120, 0.3);
        border: 3px solid #48bb78;
        border-radius: 15px;
        pointer-events: none;
    }

    .picture-rating {
        margin-top: 8px;
        text-align: center;
    }

    .stars {
        display: flex;
        justify-content: center;
        gap: 2px;
        margin-bottom: 4px;
    }

    .star {
        font-size: 18px;
        color: #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
    }

    .star:hover {
        transform: scale(1.1);
        color: #ffd700;
    }

    .star.filled {
        color: #ffd700;
    }

    /* Star hover effects for rating preview */
    .stars:hover .star {
        color: #e2e8f0;
    }

    .stars .star:hover {
        color: #ffd700 !important;
    }

    .stars .star:hover ~ .star {
        color: #e2e8f0 !important;
    }

    .rating-text {
        font-size: 12px;
        color: #718096;
        font-weight: 500;
    }

    h1 {
        color: #4a5568;
        margin-bottom: 20px;
        font-size: 2.5em;
        font-weight: 300;
    }

    .comments-section {
        margin-top: 12px;
        border-top: 1px solid #e2e8f0;
        padding-top: 8px;
    }

    .comments-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .comments-title {
        font-size: 13px;
        font-weight: 600;
        color: #4a5568;
    }

    .toggle-comments {
        background: #4299e1;
        color: white;
        border: none;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .toggle-comments:hover {
        background: #3182ce;
    }

    .comments-container {
        background: #f7fafc;
        border-radius: 6px;
        padding: 8px;
        margin-top: 8px;
    }

    .existing-comments {
        margin-bottom: 12px;
    }

    .comment {
        background: white;
        border-radius: 4px;
        padding: 8px;
        margin-bottom: 6px;
        border-left: 3px solid #4299e1;
    }

    .comment:last-child {
        margin-bottom: 0;
    }

    .comment-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }

    .comment-author {
        font-weight: 600;
        color: #2d3748;
        font-size: 12px;
    }

    .comment-date {
        font-size: 10px;
        color: #718096;
    }

    .comment-text {
        font-size: 12px;
        color: #4a5568;
        line-height: 1.4;
        word-wrap: break-word;
    }

    .add-comment-form {
        border-top: 1px solid #e2e8f0;
        padding-top: 8px;
    }

    .comment-name {
        width: 100%;
        padding: 6px 8px;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        font-size: 12px;
        margin-bottom: 6px;
        box-sizing: border-box;
    }

    .comment-input {
        width: 100%;
        padding: 6px 8px;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        font-size: 12px;
        resize: vertical;
        min-height: 60px;
        margin-bottom: 6px;
        box-sizing: border-box;
        font-family: inherit;
    }

    .submit-comment {
        background: #48bb78;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .submit-comment:hover {
        background: #38a169;
    }

    .submit-comment:disabled {
        background: #a0aec0;
        cursor: not-allowed;
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

    /* Modal Styles */
    .modal {
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
    }

    .modal-content {
        background-color: white;
        margin: 10% auto;
        padding: 30px;
        border-radius: 15px;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
        animation: modalSlideIn 0.3s ease-out;
    }

    @keyframes modalSlideIn {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .close {
        position: absolute;
        right: 20px;
        top: 15px;
        color: #aaa;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
        transition: color 0.3s ease;
    }

    .close:hover {
        color: #667eea;
    }

    .stats-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid #eee;
        font-size: 16px;
    }

    .stats-item:last-child {
        border-bottom: none;
    }

    .stats-label {
        font-weight: 500;
        color: #4a5568;
    }

    .stats-value {
        font-weight: 600;
        color: #667eea;
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
            <div class="picture-card picture-item" data-picture-name="${picture.name}">
                <input type="checkbox" class="picture-checkbox" onchange="updateSelection()">
                <img src="${picture.url}" alt="${picture.name}" onclick="openFullSize('${picture.url}')">
                <div class="picture-info">
                    <div class="picture-name">${picture.name}</div>
                    <div class="picture-date">${new Date(picture.date).toLocaleDateString()}</div>
                    <div class="picture-rating">
                        <div class="stars" data-picture="${picture.name}">
                            ${[1,2,3,4,5].map(star => `
                                <span class="star ${(picture.rating || 0) >= star ? 'filled' : ''}" 
                                      data-rating="${star}" 
                                      onclick="ratePicture('${picture.name}', ${star})">★</span>
                            `).join('')}
                        </div>
                        <span class="rating-text">${picture.rating ? `${picture.rating}/5` : 'Not rated'}</span>
                    </div>
                    <div class="comments-section">
                        <div class="comments-header">
                            <span class="comments-title">💬 Comments</span>
                            <button class="toggle-comments" onclick="toggleComments('${picture.name}')">
                                ${(picture.comments && picture.comments.length > 0) ? `Show ${picture.comments.length}` : 'Add Comment'}
                            </button>
                        </div>
                        <div class="comments-container" id="comments-${picture.name.replace(/[^a-zA-Z0-9]/g, '_')}" style="display: none;">
                            <div class="existing-comments">
                                ${(picture.comments || []).map(comment => `
                                    <div class="comment">
                                        <div class="comment-header">
                                            <span class="comment-author">${comment.author}</span>
                                            <span class="comment-date">${new Date(comment.date).toLocaleDateString()}</span>
                                        </div>
                                        <div class="comment-text">${comment.text}</div>
                                    </div>
                                `).join('')}
                            </div>
                            <div class="add-comment-form">
                                <input type="text" class="comment-name" placeholder="Your name" maxlength="50">
                                <textarea class="comment-input" placeholder="Write a comment..." maxlength="500"></textarea>
                                <button class="submit-comment" onclick="submitComment('${picture.name}')">Post Comment</button>
                            </div>
                        </div>
                    </div>
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
        
        // Confirmation prompt
        const fileNames = Array.from(files).map(file => file.name).join(', ');
        const confirmMessage = files.length === 1 
            ? `Are you sure you want to upload "${fileNames}"?`
            : `Are you sure you want to upload ${files.length} pictures?\n\nFiles: ${fileNames}`;
        
        if (!confirm(confirmMessage)) {
            return;
        }
        
        const uploadButton = document.querySelector('.upload-section button');
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
    
    async function showStats() {
        const modal = document.getElementById('statsModal');
        const statsContent = document.getElementById('statsContent');
        
        // Show modal
        modal.style.display = 'block';
        
        // Show loading
        statsContent.innerHTML = '<div class="loading">Loading statistics...</div>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/stats`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const stats = await response.json();
            
            // Format storage size
            const formatBytes = (bytes) => {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            };
            
            // Display stats
            statsContent.innerHTML = `
                <div class="stats-item">
                    <span class="stats-label">📸 Total Pictures</span>
                    <span class="stats-value">${stats.totalPictures}</span>
                </div>
                <div class="stats-item">
                    <span class="stats-label">💾 Total Storage</span>
                    <span class="stats-value">${formatBytes(stats.totalStorage)}</span>
                </div>
                <div class="stats-item">
                    <span class="stats-label">📅 Last Updated</span>
                    <span class="stats-value">${new Date().toLocaleString()}</span>
                </div>
            `;
            
        } catch (error) {
            console.error('Error loading stats:', error);
            statsContent.innerHTML = `
                <div class="error">
                    Failed to load statistics: ${error.message}
                </div>
            `;
        }
    }
    
    function closeStats() {
        const modal = document.getElementById('statsModal');
        modal.style.display = 'none';
    }
    
    // Close modal when clicking outside of it
    window.onclick = function(event) {
        const modal = document.getElementById('statsModal');
        if (event.target === modal) {
            closeStats();
        }
    }
    
    // Delete functionality
    function enterSelectMode() {
        const gallery = document.getElementById('gallery');
        const deleteSection = document.getElementById('deleteSection');
        const uploadSection = document.querySelector('.upload-section');
        const selectModeBtn = document.getElementById('selectModeBtn');
        
        gallery.classList.add('selection-mode');
        deleteSection.style.display = 'flex';
        uploadSection.style.display = 'none';
        selectModeBtn.style.display = 'none';
        
        updateSelection();
    }
    
    function cancelSelection() {
        const gallery = document.getElementById('gallery');
        const deleteSection = document.getElementById('deleteSection');
        const uploadSection = document.querySelector('.upload-section');
        const selectModeBtn = document.getElementById('selectModeBtn');
        const checkboxes = document.querySelectorAll('.picture-checkbox');
        
        gallery.classList.remove('selection-mode');
        deleteSection.style.display = 'none';
        uploadSection.style.display = 'flex';
        selectModeBtn.style.display = 'block';
        
        // Uncheck all checkboxes and remove selected class
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
            checkbox.closest('.picture-item').classList.remove('selected');
        });
    }
    
    function toggleSelectAll() {
        const checkboxes = document.querySelectorAll('.picture-checkbox');
        const selectAllBtn = document.getElementById('selectAllBtn');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = !allChecked;
            const pictureItem = checkbox.closest('.picture-item');
            if (checkbox.checked) {
                pictureItem.classList.add('selected');
            } else {
                pictureItem.classList.remove('selected');
            }
        });
        
        selectAllBtn.textContent = allChecked ? 'Select All' : 'Deselect All';
        updateSelection();
    }
    
    function updateSelection() {
        const checkboxes = document.querySelectorAll('.picture-checkbox');
        const selectedCount = document.getElementById('selectedCount');
        const deleteBtn = document.getElementById('deleteSelectedBtn');
        const selectAllBtn = document.getElementById('selectAllBtn');
        
        let checkedCount = 0;
        checkboxes.forEach(checkbox => {
            const pictureItem = checkbox.closest('.picture-item');
            if (checkbox.checked) {
                checkedCount++;
                pictureItem.classList.add('selected');
            } else {
                pictureItem.classList.remove('selected');
            }
        });
        
        selectedCount.textContent = `${checkedCount} selected`;
        deleteBtn.disabled = checkedCount === 0;
        
        const allChecked = checkedCount === checkboxes.length && checkboxes.length > 0;
        selectAllBtn.textContent = allChecked ? 'Deselect All' : 'Select All';
    }
    
    async function deleteSelected() {
        const checkboxes = document.querySelectorAll('.picture-checkbox:checked');
        const pictureNames = Array.from(checkboxes).map(cb => 
            cb.closest('.picture-item').dataset.pictureName
        );
        
        if (pictureNames.length === 0) {
            alert('Please select at least one picture to delete.');
            return;
        }
        
        const confirmMessage = pictureNames.length === 1 
            ? `Are you sure you want to delete "${pictureNames[0]}"?`
            : `Are you sure you want to delete ${pictureNames.length} pictures?\\n\\nThis action cannot be undone.`;
        
        if (!confirm(confirmMessage)) {
            return;
        }
        
        const deleteBtn = document.getElementById('deleteSelectedBtn');
        deleteBtn.disabled = true;
        deleteBtn.textContent = 'Deleting...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/pictures`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pictures: pictureNames
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Delete successful:', result);
            
            // Show success message
            const successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.textContent = `Successfully deleted ${pictureNames.length} picture(s)!`;
            document.querySelector('.container').insertBefore(successDiv, document.querySelector('main'));
            
            setTimeout(() => successDiv.remove(), 3000);
            
            // Reload pictures and exit selection mode
            cancelSelection();
            loadPictures();
            
        } catch (error) {
            console.error('Error deleting pictures:', error);
            alert(`Failed to delete pictures: ${error.message}`);
        } finally {
            deleteBtn.disabled = false;
            deleteBtn.textContent = '🗑️ Delete Selected';
        }
    }
    
    async function ratePicture(pictureName, rating) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/pictures/rate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    picture: pictureName,
                    rating: rating
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Rating saved:', result);
            
            // Update the stars display immediately
            const starsContainer = document.querySelector(`[data-picture="${pictureName}"]`);
            if (starsContainer) {
                const stars = starsContainer.querySelectorAll('.star');
                const ratingText = starsContainer.parentElement.querySelector('.rating-text');
                
                stars.forEach((star, index) => {
                    if (index < rating) {
                        star.classList.add('filled');
                    } else {
                        star.classList.remove('filled');
                    }
                });
                
                ratingText.textContent = `${rating}/5`;
            }
            
        } catch (error) {
            console.error('Error rating picture:', error);
            alert(`Failed to save rating: ${error.message}`);
        }
    }

    function toggleComments(pictureName) {
        const containerId = `comments-${pictureName.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const container = document.getElementById(containerId);
        const button = container.previousElementSibling.querySelector('.toggle-comments');
        
        if (container.style.display === 'none') {
            container.style.display = 'block';
            button.textContent = 'Hide Comments';
        } else {
            container.style.display = 'none';
            // Reset button text based on comment count
            const existingComments = container.querySelectorAll('.comment');
            button.textContent = existingComments.length > 0 ? `Show ${existingComments.length}` : 'Add Comment';
        }
    }

    async function submitComment(pictureName) {
        const containerId = `comments-${pictureName.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const container = document.getElementById(containerId);
        const nameInput = container.querySelector('.comment-name');
        const textInput = container.querySelector('.comment-input');
        const submitBtn = container.querySelector('.submit-comment');
        
        const authorName = nameInput.value.trim();
        const commentText = textInput.value.trim();
        
        if (!authorName) {
            alert('Please enter your name');
            nameInput.focus();
            return;
        }
        
        if (!commentText) {
            alert('Please enter a comment');
            textInput.focus();
            return;
        }
        
        // Disable form while submitting
        submitBtn.disabled = true;
        submitBtn.textContent = 'Posting...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/pictures/comment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    picture: pictureName,
                    author: authorName,
                    text: commentText
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Comment saved:', result);
            
            // Clear the form
            nameInput.value = '';
            textInput.value = '';
            
            // Add the new comment to the display
            const existingComments = container.querySelector('.existing-comments');
            const newComment = document.createElement('div');
            newComment.className = 'comment';
            newComment.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${authorName}</span>
                    <span class="comment-date">${new Date().toLocaleDateString()}</span>
                </div>
                <div class="comment-text">${commentText}</div>
            `;
            existingComments.appendChild(newComment);
            
            // Update the toggle button text
            const button = container.previousElementSibling.querySelector('.toggle-comments');
            const commentCount = existingComments.querySelectorAll('.comment').length;
            button.textContent = `Show ${commentCount}`;
            
            // Show success message
            alert('Comment posted successfully!');
            
        } catch (error) {
            console.error('Error posting comment:', error);
            alert(`Failed to post comment: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Post Comment';
        }
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
                    # Generate presigned URL for the image
                    url = s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': PICTURES_BUCKET, 'Key': obj['Key']},
                        ExpiresIn=3600  # 1 hour
                    )
                    
                    # Get object metadata to retrieve rating
                    try:
                        head_response = s3_client.head_object(
                            Bucket=PICTURES_BUCKET,
                            Key=obj['Key']
                        )
                        metadata = head_response.get('Metadata', {})
                        rating = int(metadata.get('rating', 0)) if metadata.get('rating') else 0
                        original_name = metadata.get('original-name', obj['Key'].split('/')[-1])
                        
                        # Parse comments from metadata
                        comments = []
                        comments_json = metadata.get('comments', '')
                        if comments_json:
                            try:
                                comments = json.loads(comments_json)
                            except json.JSONDecodeError as json_error:
                                print(f"Error parsing comments JSON for {obj['Key']}: {json_error}")
                                comments = []
                    except Exception as meta_error:
                        print(f"Error getting metadata for {obj['Key']}: {meta_error}")
                        rating = 0
                        original_name = obj['Key'].split('/')[-1]
                        comments = []
                    
                    picture_info = {
                        'name': original_name,
                        'date': obj['LastModified'].isoformat(),
                        'url': url,
                        'rating': rating,
                        'comments': comments
                    }
                    pictures.append(picture_info)
                    print(f"Added picture: {picture_info['name']} (rating: {rating})")
        else:
            print("No 'Contents' key in S3 response - bucket may be empty or prefix not found")
        
        # Sort by date (newest first)
        pictures.sort(key=lambda x: x['date'], reverse=True)
        
        print(f"Returning {len(pictures)} pictures")
        
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
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Failed to get pictures: {str(e)}'})
        }

def get_stats():
    """Get gallery statistics from S3"""
    try:
        print(f"Getting stats from bucket: {PICTURES_BUCKET}")
        
        # List all objects in the pictures folder
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        total_pictures = 0
        total_storage = 0
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    total_pictures += 1
                    total_storage += obj['Size']
        
        print(f"Stats: {total_pictures} pictures, {total_storage} bytes")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'totalPictures': total_pictures,
                'totalStorage': total_storage
            })
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

def delete_pictures(event):
    """Delete multiple pictures from S3"""
    try:
        # Parse the request body
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        if not body:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No request body provided'})
            }
        
        data = json.loads(body)
        picture_names = data.get('pictures', [])
        
        if not picture_names:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No pictures specified for deletion'})
            }
        
        print(f"Deleting pictures: {picture_names}")
        print(f"Picture names type: {type(picture_names)}")
        for i, name in enumerate(picture_names):
            print(f"Picture {i}: '{name}' (type: {type(name)})")
        
        # First, get all objects to find the actual S3 keys
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        # Create a mapping of picture names to S3 keys using metadata
        name_to_key = {}
        keys_to_delete = []
        not_found = []
        
        if 'Contents' in response:
            print(f"Found {len(response['Contents'])} objects in S3")
            for obj in response['Contents']:
                key = obj['Key']
                try:
                    # Get object metadata to find original name
                    head_response = s3_client.head_object(
                        Bucket=PICTURES_BUCKET,
                        Key=key
                    )
                    metadata = head_response.get('Metadata', {})
                    original_name = metadata.get('original-name', key.split('/')[-1])
                    print(f"S3 object: {key} -> original_name: '{original_name}' (metadata: {metadata})")
                    
                    # Check if this picture should be deleted
                    for picture_name in picture_names:
                        print(f"Comparing '{picture_name}' with '{original_name}'")
                        if (original_name == picture_name or 
                            picture_name.lower() in original_name.lower() or
                            original_name.lower() in picture_name.lower()):
                            keys_to_delete.append({'Key': key})
                            name_to_key[picture_name] = key
                            print(f"Found match: {picture_name} -> {key} (original: {original_name})")
                            break
                            
                except Exception as meta_error:
                    print(f"Error getting metadata for {key}: {meta_error}")
                    # Fallback to filename matching
                    filename = key.split('/')[-1]
                    for picture_name in picture_names:
                        if (picture_name.lower() in filename.lower() or
                            filename.lower().startswith(picture_name.lower())):
                            keys_to_delete.append({'Key': key})
                            name_to_key[picture_name] = key
                            print(f"Found fallback match: {picture_name} -> {key}")
                            break
        
        # Check for pictures that weren't found
        for picture_name in picture_names:
            if picture_name not in name_to_key:
                not_found.append(picture_name)
                print(f"Picture not found: {picture_name}")
        
        if not keys_to_delete:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'No matching pictures found for deletion',
                    'not_found': not_found
                })
            }
        
        # Delete the objects from S3
        delete_response = s3_client.delete_objects(
            Bucket=PICTURES_BUCKET,
            Delete={
                'Objects': keys_to_delete,
                'Quiet': False
            }
        )
        
        deleted_count = len(delete_response.get('Deleted', []))
        errors = delete_response.get('Errors', [])
        
        print(f"Successfully deleted {deleted_count} pictures")
        if errors:
            print(f"Errors during deletion: {errors}")
        
        result = {
            'deleted_count': deleted_count,
            'requested_count': len(picture_names)
        }
        
        if not_found:
            result['not_found'] = not_found
        
        if errors:
            result['errors'] = errors
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(result)
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
        
        if not body:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'No request body provided'})
            }
        
        data = json.loads(body)
        picture_name = data.get('picture', '')
        rating = data.get('rating', 0)
        
        if not picture_name:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Picture name is required'})
            }
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Rating must be an integer between 1 and 5'})
            }
        
        print(f"Rating picture '{picture_name}' with {rating} stars")
        
        # Find the S3 object for this picture using metadata
        response = s3_client.list_objects_v2(
            Bucket=PICTURES_BUCKET,
            Prefix='pictures/'
        )
        
        s3_key = None
        if 'Contents' in response:
            print(f"Found {len(response['Contents'])} objects in S3 for rating")
            for obj in response['Contents']:
                key = obj['Key']
                try:
                    # Get object metadata to find original name
                    head_response = s3_client.head_object(
                        Bucket=PICTURES_BUCKET,
                        Key=key
                    )
                    metadata = head_response.get('Metadata', {})
                    original_name = metadata.get('original-name', key.split('/')[-1])
                    print(f"Checking S3 object: {key} -> original_name: '{original_name}'")
                    
                    # Match by original name from metadata
                    if (original_name == picture_name or 
                        picture_name.lower() in original_name.lower() or
                        original_name.lower() in picture_name.lower()):
                        s3_key = key
                        print(f"Found match for rating: '{picture_name}' -> {key}")
                        break
                        
                except Exception as meta_error:
                    print(f"Error getting metadata for {key}: {meta_error}")
                    # Fallback to filename matching
                    filename = key.split('/')[-1]
                    if picture_name.lower() in filename.lower():
                        s3_key = key
                        print(f"Found fallback match for rating: '{picture_name}' -> {key}")
                        break
        
        if not s3_key:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': f'Picture "{picture_name}" not found'})
            }
        
        # Get current object metadata
        head_response = s3_client.head_object(
            Bucket=PICTURES_BUCKET,
            Key=s3_key
        )
        
        # Update metadata with rating
        current_metadata = head_response.get('Metadata', {})
        current_metadata['rating'] = str(rating)
        current_metadata['original-name'] = picture_name
        
        # Copy object with new metadata (S3 doesn't allow direct metadata updates)
        copy_source = {'Bucket': PICTURES_BUCKET, 'Key': s3_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=PICTURES_BUCKET,
            Key=s3_key,
            Metadata=current_metadata,
            MetadataDirective='REPLACE',
            ContentType=head_response.get('ContentType', 'image/jpeg')
        )
        
        print(f"Successfully rated picture {picture_name} with {rating} stars")
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
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
        
        if not picture_name or not author or not comment_text:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Missing required fields: picture, author, text'})
            }
        
        print(f"Adding comment to picture: {picture_name}")
        
        # Find the S3 object key for this picture
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
                'body': json.dumps({'error': f'Picture not found: {picture_name}'})
            }
        
        # Get current metadata
        head_response = s3_client.head_object(
            Bucket=PICTURES_BUCKET,
            Key=target_key
        )
        current_metadata = head_response.get('Metadata', {})
        
        # Parse existing comments
        existing_comments = []
        comments_json = current_metadata.get('comments', '')
        if comments_json:
            try:
                existing_comments = json.loads(comments_json)
            except json.JSONDecodeError as e:
                print(f"Error parsing existing comments: {e}")
                existing_comments = []
        
        # Add new comment
        new_comment = {
            'author': author,
            'text': comment_text,
            'date': datetime.now().isoformat()
        }
        existing_comments.append(new_comment)
        
        # Update metadata with new comments
        updated_metadata = current_metadata.copy()
        updated_metadata['comments'] = json.dumps(existing_comments)
        
        # Copy object with updated metadata
        s3_client.copy_object(
            Bucket=PICTURES_BUCKET,
            CopySource={'Bucket': PICTURES_BUCKET, 'Key': target_key},
            Key=target_key,
            Metadata=updated_metadata,
            MetadataDirective='REPLACE'
        )
        
        print(f"Comment added successfully to {picture_name}")
        
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
        
        # Upload to S3
        s3_client.put_object(
            Bucket=PICTURES_BUCKET,
            Key=s3_key,
            Body=processed_image_bytes,
            ContentType=content_type,
            Metadata={
                'original-name': picture_name,
                'upload_date': datetime.now().isoformat(),
                'rating': '0'
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
