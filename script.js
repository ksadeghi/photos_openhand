
// Configuration - Update this with your Lambda function URL
const API_BASE_URL = 'https://szfzftsjzuuwuuppczhfetu6ye0mipck.lambda-url.us-east-1.on.aws';

// Global variables
let currentPictures = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadPictures();
});

// Load pictures from the API
async function loadPictures() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/pictures`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const pictures = await response.json();
        currentPictures = pictures;
        displayPictures(pictures);
    } catch (error) {
        console.error('Error loading pictures:', error);
        document.getElementById('gallery').innerHTML = `
            <div style="text-align: center; color: #e53e3e; font-size: 1.2rem; grid-column: 1 / -1;">
                Failed to load pictures: ${error.message}
            </div>
        `;
    }
}

// Display pictures in the gallery
function displayPictures(pictures) {
    const gallery = document.getElementById('gallery');

    gallery.innerHTML = pictures.map(picture => `
        <div class="picture-card picture-item" data-picture-name="${picture.name}">
            <input type="checkbox" class="picture-checkbox" onchange="handleCheckboxChange()">
            <img src="${picture.url}" alt="${picture.name}" onclick="openFullSize('${picture.url}')">
            <div class="picture-info">
                <div class="picture-name">${picture.name}</div>
                <div class="picture-date">${new Date(picture.date).toLocaleDateString()}</div>
                <div class="picture-rating">
                    <div class="stars" data-picture="${picture.name}">
                        ${[1, 2, 3, 4, 5].map(star => 
                            `<span class="star ${star <= (picture.rating || 0) ? 'filled' : ''}" 
                                   onclick="ratePicture('${picture.name}', ${star})">★</span>`
                        ).join('')}
                    </div>
                    <span class="rating-text">${picture.rating || 0}/5</span>
                </div>
                <div class="comments-section">
                    <button class="toggle-comments" onclick="toggleComments('${picture.name}')">
                        Show ${(picture.comments || []).length}
                    </button>
                    <div class="comments-container" id="comments-${picture.name}">
                        ${(picture.comments || []).map(comment => `
                            <div class="comment">
                                <div class="comment-header">
                                    <span class="comment-author">${comment.author}</span>
                                    <span class="comment-date">${new Date(comment.date).toLocaleDateString()}</span>
                                </div>
                                <div class="comment-text">${comment.text}</div>
                            </div>
                        `).join('')}
                        <div class="add-comment">
                            <input type="text" placeholder="Your name" class="comment-author-input">
                            <textarea placeholder="Add a comment..." class="comment-text-input"></textarea>
                            <button onclick="postComment('${picture.name}', this)">Post Comment</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Open full-size image
function openFullSize(url) {
    const modal = document.getElementById('fullSizeModal');
    const img = document.getElementById('fullSizeImage');
    img.src = url;
    modal.style.display = 'block';
}

// Close full-size image
function closeFullSize() {
    document.getElementById('fullSizeModal').style.display = 'none';
}

// Upload pictures
async function uploadPictures() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;

    if (files.length === 0) {
        alert('Please select at least one file to upload.');
        return;
    }

    // Confirmation prompt
    const fileNames = Array.from(files).map(file => file.name).join(', ');
    if (!confirm(`Upload ${files.length} file(s)?\n\n${fileNames}`)) {
        return;
    }
    
    const uploadButton = document.getElementById('uploadBtn');
    uploadButton.disabled = true;
    uploadButton.textContent = 'Uploading...';
    
    try {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // Update button text with progress
            uploadButton.textContent = `Uploading ${i + 1}/${files.length}...`;
            
            // Convert file to base64
            const base64Data = await fileToBase64(file);
            
            const response = await fetch(`${API_BASE_URL}/api/pictures`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: file.name,
                    data: base64Data,
                    contentType: file.type
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
        }
        
        // Show success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = `Successfully uploaded ${files.length} picture(s)!`;
        document.querySelector('.container').insertBefore(successDiv, document.querySelector('main'));
        
        setTimeout(() => successDiv.remove(), 3000);
        
        // Clear file input and reload pictures
        fileInput.value = '';
        loadPictures();
        
    } catch (error) {
        console.error('Error uploading pictures:', error);
        alert(`Failed to upload pictures: ${error.message}`);
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = 'Upload Pictures';
    }
}

// Convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            // Remove the data:image/jpeg;base64, prefix
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = error => reject(error);
    });
}

// Show stats modal
async function showStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        
        const statsContent = document.getElementById('statsContent');
        statsContent.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total Pictures</span>
                <span class="stat-value">${stats.totalPictures}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Size</span>
                <span class="stat-value">${stats.totalSize}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Average Rating</span>
                <span class="stat-value">${stats.averageRating}/5</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Comments</span>
                <span class="stat-value">${stats.totalComments}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Most Recent Upload</span>
                <span class="stat-value">${stats.mostRecentUpload}</span>
            </div>
        `;
        
        document.getElementById('statsModal').style.display = 'block';
        
    } catch (error) {
        console.error('Error loading stats:', error);
        alert(`Failed to load stats: ${error.message}`);
    }
}

// Close stats modal
function closeStats() {
    document.getElementById('statsModal').style.display = 'none';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const statsModal = document.getElementById('statsModal');
    const fullSizeModal = document.getElementById('fullSizeModal');
    
    if (event.target === statsModal) {
        closeStats();
    }
    if (event.target === fullSizeModal) {
        closeFullSize();
    }
}

// Toggle comments visibility
function toggleComments(pictureName) {
    const container = document.getElementById(`comments-${pictureName}`);
    const button = event.target;
    
    if (container.classList.contains('show')) {
        container.classList.remove('show');
        button.textContent = `Show ${container.querySelectorAll('.comment').length}`;
    } else {
        container.classList.add('show');
        button.textContent = `Hide ${container.querySelectorAll('.comment').length}`;
    }
}

// Post a comment
async function postComment(pictureName, button) {
    const container = button.closest('.add-comment');
    const authorInput = container.querySelector('.comment-author-input');
    const textInput = container.querySelector('.comment-text-input');
    
    const author = authorInput.value.trim();
    const commentText = textInput.value.trim();
    
    if (!author || !commentText) {
        alert('Please enter both your name and a comment.');
        return;
    }
    
    const submitBtn = button;
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
                author: author,
                text: commentText
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        // Clear inputs
        authorInput.value = '';
        textInput.value = '';
        
        // Add new comment to the display
        const existingComments = container.parentElement.querySelector('.comments-container');
        const newComment = document.createElement('div');
        newComment.className = 'comment';
        newComment.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${author}</span>
                <span class="comment-date">${new Date().toLocaleDateString()}</span>
            </div>
            <div class="comment-text">${commentText}</div>
        `;
        existingComments.appendChild(newComment);
        
        // Update the toggle button text
        const toggleButton = container.previousElementSibling.querySelector('.toggle-comments');
        const commentCount = existingComments.querySelectorAll('.comment').length;
        toggleButton.textContent = `Show ${commentCount}`;
        
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

// Delete functionality
function enterSelectMode() {
    const gallery = document.getElementById('gallery');
    const deleteSection = document.getElementById('deleteSection');
    const uploadSection = document.querySelector('.upload-section');
    const selectModeBtn = document.getElementById('selectModeBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const downloadModeBtn = document.getElementById('downloadModeBtn');
    
    gallery.classList.add('selection-mode');
    deleteSection.style.display = 'flex';
    uploadSection.style.display = 'flex';
    selectModeBtn.style.display = 'none';
    
    // Hide upload elements and show download button
    uploadBtn.style.display = 'none';
    fileInput.style.display = 'none';
    downloadModeBtn.style.display = 'inline-block';
    
    updateSelection();
}

function cancelSelection() {
    const gallery = document.getElementById('gallery');
    const deleteSection = document.getElementById('deleteSection');
    const uploadSection = document.querySelector('.upload-section');
    const selectModeBtn = document.getElementById('selectModeBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const downloadModeBtn = document.getElementById('downloadModeBtn');
    const checkboxes = document.querySelectorAll('.picture-checkbox');
    
    gallery.classList.remove('selection-mode');
    deleteSection.style.display = 'none';
    uploadSection.style.display = 'flex';
    selectModeBtn.style.display = 'block';
    
    // Restore upload elements and hide download button
    uploadBtn.style.display = 'inline-block';
    fileInput.style.display = 'inline-block';
    downloadModeBtn.style.display = 'none';
    
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

function handleCheckboxChange() {
    const deleteSection = document.getElementById('deleteSection');
    const downloadSection = document.getElementById('downloadSection');
    
    if (deleteSection.style.display === 'flex') {
        updateSelection();
    } else if (downloadSection.style.display === 'flex') {
        updateDownloadSelection();
    }
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
    
    if (!confirm(`Are you sure you want to delete ${pictureNames.length} picture(s)?\n\nThis action cannot be undone.`)) {
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

// Download functionality
function enterDownloadMode() {
    const gallery = document.getElementById('gallery');
    const downloadSection = document.getElementById('downloadSection');
    const deleteSection = document.getElementById('deleteSection');
    const uploadSection = document.querySelector('.upload-section');
    const downloadModeBtn = document.getElementById('downloadModeBtn');
    const selectModeBtn = document.getElementById('selectModeBtn');
    
    gallery.classList.add('selection-mode');
    downloadSection.style.display = 'flex';
    deleteSection.style.display = 'none';
    uploadSection.style.display = 'flex';
    downloadModeBtn.style.display = 'none';
    selectModeBtn.style.display = 'none';
    
    updateDownloadSelection();
}

function cancelDownloadSelection() {
    const gallery = document.getElementById('gallery');
    const downloadSection = document.getElementById('downloadSection');
    const uploadSection = document.querySelector('.upload-section');
    const downloadModeBtn = document.getElementById('downloadModeBtn');
    const selectModeBtn = document.getElementById('selectModeBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const deleteSection = document.getElementById('deleteSection');
    const checkboxes = document.querySelectorAll('.picture-checkbox');
    
    gallery.classList.remove('selection-mode');
    downloadSection.style.display = 'none';
    deleteSection.style.display = 'flex';
    uploadSection.style.display = 'flex';
    downloadModeBtn.style.display = 'inline-block';
    selectModeBtn.style.display = 'none';
    
    // Show delete section and hide upload elements, keep download button visible
    uploadBtn.style.display = 'none';
    fileInput.style.display = 'none';
    
    // Uncheck all checkboxes and remove selected class
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
        checkbox.closest('.picture-item').classList.remove('selected');
    });
}

function toggleSelectAllDownload() {
    const checkboxes = document.querySelectorAll('.picture-checkbox');
    const selectAllBtn = document.getElementById('selectAllDownloadBtn');
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
    updateDownloadSelection();
}

function updateDownloadSelection() {
    const checkboxes = document.querySelectorAll('.picture-checkbox');
    const selectedCount = document.getElementById('selectedDownloadCount');
    const downloadBtn = document.getElementById('downloadSelectedBtn');
    const selectAllBtn = document.getElementById('selectAllDownloadBtn');
    
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
    downloadBtn.disabled = checkedCount === 0;
    
    const allChecked = checkedCount === checkboxes.length && checkboxes.length > 0;
    selectAllBtn.textContent = allChecked ? 'Deselect All' : 'Select All';
}

async function downloadSelected() {
    const checkboxes = document.querySelectorAll('.picture-checkbox:checked');
    const pictureNames = Array.from(checkboxes).map(cb => 
        cb.closest('.picture-item').dataset.pictureName
    );
    
    if (pictureNames.length === 0) {
        alert('Please select at least one picture to download.');
        return;
    }
    
    const downloadBtn = document.getElementById('downloadSelectedBtn');
    downloadBtn.disabled = true;
    downloadBtn.textContent = 'Preparing Download...';
    
    try {
        // Request ZIP file from backend
        const response = await fetch(`${API_BASE_URL}/api/pictures/download`, {
            method: 'POST',
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
        
        // Get the ZIP file as blob
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `photos_${new Date().toISOString().split('T')[0]}.zip`;
        
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = `Successfully prepared download of ${pictureNames.length} picture(s)!`;
        document.querySelector('.container').insertBefore(successDiv, document.querySelector('main'));
        
        setTimeout(() => successDiv.remove(), 3000);
        
        // Exit download mode
        cancelDownloadSelection();
        
    } catch (error) {
        console.error('Error downloading pictures:', error);
        alert(`Failed to download pictures: ${error.message}`);
    } finally {
        downloadBtn.disabled = false;
        downloadBtn.textContent = '📥 Download Selected';
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
        alert(`Failed to rate picture: ${error.message}`);
    }
}

