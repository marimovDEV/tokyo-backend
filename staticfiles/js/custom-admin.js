// Custom Admin JavaScript for Logo Preview and File Upload

document.addEventListener('DOMContentLoaded', function() {
    // Logo Preview Functionality
    const logoInput = document.getElementById('id_logo');
    const logoPreview = document.querySelector('.logo-preview img');
    
    if (logoInput) {
        logoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file.');
                    this.value = '';
                    return;
                }
                
                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size must be less than 5MB.');
                    this.value = '';
                    return;
                }
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (logoPreview) {
                        logoPreview.src = e.target.result;
                        logoPreview.style.display = 'block';
                    } else {
                        // Create preview if it doesn't exist
                        createLogoPreview(e.target.result);
                    }
                    
                    // Show success message
                    showMessage('Logo preview updated successfully!', 'success');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Favicon Preview Functionality
    const faviconInput = document.getElementById('id_favicon');
    const faviconPreview = document.querySelector('.favicon-preview img');
    
    if (faviconInput) {
        faviconInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file.');
                    this.value = '';
                    return;
                }
                
                // Validate file size (max 1MB)
                if (file.size > 1 * 1024 * 1024) {
                    alert('Favicon file size must be less than 1MB.');
                    this.value = '';
                    return;
                }
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (faviconPreview) {
                        faviconPreview.src = e.target.result;
                        faviconPreview.style.display = 'block';
                    } else {
                        createFaviconPreview(e.target.result);
                    }
                    
                    showMessage('Favicon preview updated successfully!', 'success');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Drag and Drop Functionality
    const fileUploadAreas = document.querySelectorAll('.file-upload-area');
    
    fileUploadAreas.forEach(area => {
        area.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        area.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                const input = this.querySelector('input[type="file"]');
                if (input) {
                    input.files = files;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        });
    });
    
    // Initialize previews on page load
    initializePreviews();
});

function createLogoPreview(src) {
    const container = document.querySelector('.field-logo_preview');
    if (container) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'logo-preview';
        previewDiv.innerHTML = `
            <img src="${src}" alt="Logo Preview" style="max-width: 200px; max-height: 100px;">
            <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">Logo Preview</p>
        `;
        container.appendChild(previewDiv);
    }
}

function createFaviconPreview(src) {
    const container = document.querySelector('.field-favicon_preview');
    if (container) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'favicon-preview';
        previewDiv.innerHTML = `
            <img src="${src}" alt="Favicon Preview" style="width: 32px; height: 32px;">
            <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">Favicon Preview</p>
        `;
        container.appendChild(previewDiv);
    }
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.custom-message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `custom-message logo-upload-${type}`;
    messageDiv.textContent = message;
    
    // Insert after the form
    const form = document.querySelector('form');
    if (form) {
        form.insertAdjacentElement('afterend', messageDiv);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

function initializePreviews() {
    // Check if there are existing images to show
    const logoPreview = document.querySelector('.logo-preview img');
    const faviconPreview = document.querySelector('.favicon-preview img');
    
    if (logoPreview && logoPreview.src && !logoPreview.src.includes('data:')) {
        // Image is loaded from server, make sure it's visible
        logoPreview.style.display = 'block';
    }
    
    if (faviconPreview && faviconPreview.src && !faviconPreview.src.includes('data:')) {
        faviconPreview.style.display = 'block';
    }
}

// Form validation
function validateImageUpload(input, maxSize, allowedTypes) {
    const file = input.files[0];
    if (!file) return true;
    
    // Check file type
    if (!allowedTypes.includes(file.type)) {
        alert(`Invalid file type. Please upload: ${allowedTypes.join(', ')}`);
        input.value = '';
        return false;
    }
    
    // Check file size
    if (file.size > maxSize) {
        alert(`File size must be less than ${Math.round(maxSize / 1024 / 1024)}MB`);
        input.value = '';
        return false;
    }
    
    return true;
}