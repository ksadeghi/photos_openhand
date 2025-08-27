import json
import base64
import os

def lambda_handler(event, context):
    """
    Lambda function to serve the frontend HTML page
    """
    
    # Get the path from the event
    path = event.get('rawPath', '/')
    
    if path == '/' or path == '/index.html':
        return serve_html()
    elif path == '/style.css':
        return serve_css()
    elif path == '/script.js':
        return serve_js()
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': '<h1>404 - Page Not Found</h1>'
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
                <div class="filters">
                    <input type="date" id="dateFilter" placeholder="Filter by date">
                    <input type="text" id="nameFilter" placeholder="Filter by name">
                    <button onclick="loadPictures()">Refresh</button>
                </div>
                
                <div id="gallery" class="gallery">
                    <!-- Pictures will be loaded here -->
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    Loading pictures...
                </div>
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
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
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
        font-family: 'Arial', sans-serif;
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
        background: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
        text-align: center;
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
    
    input[type="file"], input[type="date"], input[type="text"] {
        padding: 12px 15px;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    input[type="file"]:focus, input[type="date"]:focus, input[type="text"]:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .filters {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
        display: flex;
        gap: 15px;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 25px;
        margin-bottom: 30px;
    }
    
    .picture-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
        transition: transform 0.3s ease;
    }
    
    .picture-card:hover img {
        transform: scale(1.05);
    }
    
    .picture-info {
        padding: 20px;
    }
    
    .picture-name {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 8px;
        font-size: 1.1em;
    }
    
    .picture-date {
        color: #718096;
        font-size: 0.9em;
    }
    
    .loading {
        text-align: center;
        padding: 40px;
        font-size: 1.2em;
        color: #4a5568;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .error {
        background: #fed7d7;
        color: #c53030;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
        text-align: center;
    }
    
    .success {
        background: #c6f6d5;
        color: #2f855a;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
        text-align: center;
    }
    
    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        
        .upload-section, .filters {
            flex-direction: column;
        }
        
        .gallery {
            grid-template-columns: 1fr;
        }
        
        h1 {
            font-size: 2em;
        }
    }
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/css',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': css_content
    }

def serve_js():
    """Serve the JavaScript code"""
    # Get backend URL from environment variable
    backend_url = os.environ.get('BACKEND_URL', 'https://your-backend-lambda-url.lambda-url.region.on.aws')
    
    js_content = f"""
    // Configuration - Backend Lambda function URL from environment
    const API_BASE_URL = '{backend_url}';
    
    // Load pictures when page loads
    document.addEventListener('DOMContentLoaded', function() {
        loadPictures();
    });
    
    async function loadPictures() {
        const loading = document.getElementById('loading');
        const gallery = document.getElementById('gallery');
        const dateFilter = document.getElementById('dateFilter').value;
        const nameFilter = document.getElementById('nameFilter').value;
        
        loading.style.display = 'block';
        gallery.innerHTML = '';
        
        try {
            let url = `${API_BASE_URL}/pictures`;
            const params = new URLSearchParams();
            
            if (dateFilter) {
                params.append('date', dateFilter);
            }
            if (nameFilter) {
                params.append('name', nameFilter);
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.pictures && data.pictures.length > 0) {
                displayPictures(data.pictures);
            } else {
                gallery.innerHTML = '<div class="error">No pictures found</div>';
            }
        } catch (error) {
            console.error('Error loading pictures:', error);
            gallery.innerHTML = '<div class="error">Error loading pictures. Please try again.</div>';
        } finally {
            loading.style.display = 'none';
        }
    }
    
    function displayPictures(pictures) {
        const gallery = document.getElementById('gallery');
        
        pictures.forEach(picture => {
            const card = document.createElement('div');
            card.className = 'picture-card';
            
            card.innerHTML = `
                <img src="${picture.jpg_url}" alt="${picture.picture_name}" loading="lazy">
                <div class="picture-info">
                    <div class="picture-name">${picture.picture_name}</div>
                    <div class="picture-date">${formatDate(picture.picture_date)}</div>
                </div>
            `;
            
            gallery.appendChild(card);
        });
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    
    async function uploadPictures() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;
        
        if (files.length === 0) {
            alert('Please select at least one file to upload');
            return;
        }
        
        const gallery = document.getElementById('gallery');
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            if (!file.type.startsWith('image/')) {
                alert(`File ${file.name} is not an image`);
                continue;
            }
            
            try {
                await uploadSinglePicture(file);
                showMessage(`Successfully uploaded ${file.name}`, 'success');
            } catch (error) {
                console.error('Error uploading file:', error);
                showMessage(`Error uploading ${file.name}`, 'error');
            }
        }
        
        // Clear the file input and reload pictures
        fileInput.value = '';
        setTimeout(() => {
            loadPictures();
        }, 1000);
    }
    
    async function uploadSinglePicture(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('picture_name', file.name);
        formData.append('picture_date', new Date().toISOString().split('T')[0]);
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    function showMessage(message, type) {
        const container = document.querySelector('.container');
        const messageDiv = document.createElement('div');
        messageDiv.className = type;
        messageDiv.textContent = message;
        
        container.insertBefore(messageDiv, container.firstChild);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
    
    // Add event listeners for filters
    document.getElementById('dateFilter').addEventListener('change', loadPictures);
    document.getElementById('nameFilter').addEventListener('input', debounce(loadPictures, 500));
    
    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/javascript',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': js_content
    }
