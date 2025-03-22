// File deletion
function deleteSourcefile(slug) {
    if (confirm('Are you sure you want to delete this sourcefile? This action cannot be undone.')) {
        fetch(resolveRoute('SOURCEFILE_VIEWS_DELETE_SOURCEFILE', {
            target_language_code: window.target_language_code,
            sourcedir_slug: window.sourcedir_slug,
            sourcefile_slug: slug
        }), {
            method: 'DELETE',
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to delete sourcefile');
            }
        });
    }
}

// Directory operations
async function renameSourcedir() {
    try {
        const newName = await showModal({
            placeholder: "Enter new directory name",
            defaultValue: window.sourcedir_path,
            confirmText: "Rename",
            cancelText: "Cancel"
        });

        const response = await fetch(
            resolveRoute('SOURCEDIR_VIEWS_RENAME_SOURCEDIR', {
                target_language_code: window.target_language_code,
                sourcedir_slug: window.sourcedir_slug
            }),
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_name: newName })
            }
        );

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to rename directory');
        }

        const data = await response.json();
        // Redirect to the new URL with the new slug
        window.location.href = resolveRoute('SOURCEDIR_VIEWS_SOURCEFILE_LIST', {
            target_language_code: window.target_language_code,
            sourcedir_slug: data.slug
        });
    } catch (error) {
        if (error.message !== 'User cancelled') {
            alert('Error renaming directory: ' + error.message);
        }
    }
}

function deleteSourcedir() {
    if (confirm('Are you sure you want to delete this directory? This action cannot be undone.')) {
        fetch(resolveRoute('SOURCEDIR_VIEWS_DELETE_SOURCEDIR', {
            target_language_code: window.target_language_code,
            sourcedir_slug: window.sourcedir_slug
        }), {
            method: 'DELETE',
        }).then(async response => {
            if (response.ok) {
                window.location.href = resolveRoute('SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE', {
                    target_language_code: window.target_language_code
                });
            } else {
                // Try to get a more specific error message from the response
                let errorMsg;
                try {
                    const data = await response.json();
                    errorMsg = data.error;
                } catch (e) {
                    // If we can't parse the response as JSON
                    errorMsg = null;
                }
                
                alert(errorMsg || 'Failed to delete directory. If the directory contains files, you must delete all files first.');
            }
        }).catch(error => {
            alert('Failed to delete directory: ' + error.message);
        });
    }
}

// File upload handling
function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        uploadFiles(files);
    }
}

async function uploadFiles(files) {
    const progressContainer = document.getElementById('uploadProgress');
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const fileProgressDiv = document.getElementById('fileProgress');

    progressContainer.style.display = 'block';
    fileProgressDiv.innerHTML = '';

    const formData = new FormData();
    for (let file of files) {
        formData.append('files[]', file);
    }

    try {
        const response = await fetch(
            resolveRoute('SOURCEDIR_VIEWS_UPLOAD_FILES', {
                target_language_code: window.target_language_code,
                sourcedir_slug: window.sourcedir_slug
            }),
            {
                method: 'POST',
                body: formData
            }
        );

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert('Upload failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Upload failed: ' + error.message);
    } finally {
        progressContainer.style.display = 'none';
    }
}

// Language selection
function initLanguageSelector() {
    document.querySelector('.language-selector').addEventListener('change', function (e) {
        const newLanguage = e.target.value;

        fetch(resolveRoute('SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_LANGUAGE', {
                target_language_code: window.target_language_code,
                sourcedir_slug: window.sourcedir_slug
            }), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language_code: newLanguage })
        }).then(response => {
            if (response.ok) {
                window.location.href = resolveRoute('SOURCEDIR_VIEWS_SOURCEFILE_LIST', {
                    target_language_code: newLanguage,
                    sourcedir_slug: e.target.dataset.sourcedirSlug
                });
            } else {
                alert('Failed to update language');
            }
        });
    });
}

// Create from Text functionality
function showCreateFromTextModal() {
    const modal = document.getElementById('createFromTextModal');
    const titleInput = document.getElementById('textTitle');
    const textInput = document.getElementById('textContent');
    const submitBtn = document.getElementById('submitText');
    const cancelBtn = document.getElementById('cancelText');

    modal.classList.add('show');
    titleInput.focus();

    const closeModal = () => {
        modal.classList.remove('show');
        titleInput.value = '';
        textInput.value = '';
    };

    submitBtn.onclick = async () => {
        const title = titleInput.value.trim();
        const text = textInput.value.trim();

        if (!title) {
            alert('Please enter a title');
            return;
        }
        if (!text) {
            alert('Please enter some text');
            return;
        }

        try {
            const response = await fetch(
                resolveRoute('SOURCEFILE_VIEWS_CREATE_FROM_TEXT', {
                    target_language_code: window.target_language_code,
                    sourcedir_slug: window.sourcedir_slug
                }),
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        text_target: text
                    })
                }
            );

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to create sourcefile');
            }

            const data = await response.json();
            window.location.href = resolveRoute('SOURCEFILE_VIEWS_GET_SOURCEFILE', {
                target_language_code: window.target_language_code,
                sourcedir_slug: window.sourcedir_slug,
                sourcefile_slug: data.slug
            });
        } catch (error) {
            alert(error.message);
        }
    };

    cancelBtn.onclick = closeModal;

    window.onclick = (event) => {
        if (event.target == modal) {
            closeModal();
        }
    };
}

// YouTube URL functionality
function showYouTubeModal() {
    const modal = document.getElementById('youtubeModal');
    const urlInput = document.getElementById('youtubeUrl');
    const downloadBtn = document.getElementById('downloadYoutube');
    const cancelBtn = document.getElementById('cancelYoutube');
    const progressDiv = document.getElementById('youtubeProgress');

    modal.classList.add('show');
    urlInput.value = '';
    urlInput.focus();

    const closeModal = () => {
        modal.classList.remove('show');
        progressDiv.style.display = 'none';
    };

    const handleDownload = async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please enter a YouTube URL');
            return;
        }

        try {
            // Show progress
            downloadBtn.disabled = true;
            cancelBtn.disabled = true;
            progressDiv.style.display = 'block';

            const response = await fetch(
                resolveRoute('SOURCEFILE_VIEWS_ADD_FROM_YOUTUBE', {
                    target_language_code: window.target_language_code,
                    sourcedir_slug: window.sourcedir_slug
                }),
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ youtube_url: url }),
                }
            );

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Failed to download audio');
            }

            window.location.href = resolveRoute('SOURCEFILE_VIEWS_GET_SOURCEFILE', {
                target_language_code: window.target_language_code,
                sourcedir_slug: window.sourcedir_slug,
                sourcefile_slug: data.slug
            });
        } catch (error) {
            // More informative error messages
            let errorMessage = error.message;
            if (error.message === 'Failed to fetch') {
                errorMessage = 'Network error: Could not connect to server. Please check your internet connection and try again.';
            } else if (error.message.includes('HTTP Error 403')) {
                errorMessage = 'YouTube access error: The video is not accessible. This can happen if the video is private or region-restricted.';
            }
            alert('Error: ' + errorMessage);
            downloadBtn.disabled = false;
            cancelBtn.disabled = false;
            progressDiv.style.display = 'none';
        }
    };

    // Handle keyboard shortcuts
    const handleKeydown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleDownload();
        } else if (event.key === 'Escape') {
            event.preventDefault();
            closeModal();
        }
    };

    downloadBtn.onclick = handleDownload;
    cancelBtn.onclick = closeModal;
    urlInput.addEventListener('keydown', handleKeydown);

    // Close modal when clicking outside
    modal.onclick = (event) => {
        if (event.target === modal) {
            closeModal();
        }
    };

    // Cleanup event listeners when modal is closed
    modal.addEventListener('hide', () => {
        urlInput.removeEventListener('keydown', handleKeydown);
    }, { once: true });
}

// Initialize everything
function init() {
    // Set up file input handlers
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    document.getElementById('cameraInput').addEventListener('change', handleFileSelect);
    document.getElementById('libraryInput').addEventListener('change', handleFileSelect);
    document.getElementById('audioInput').addEventListener('change', handleFileSelect);
    document.getElementById('desktopAudioInput').addEventListener('change', handleFileSelect);

    // Initialize language selector
    initLanguageSelector();
    
    // Set up mobile/desktop specific UI elements
    setupDeviceSpecificUI();
}

// Setup device-specific UI elements
function setupDeviceSpecificUI() {
    // Check if the global isMobileOrTablet function is available
    if (typeof window.isMobileOrTablet === 'function') {
        const isMobile = window.isMobileOrTablet();
        const mobileOptions = document.querySelector('.mobile-upload-options');
        
        if (mobileOptions) {
            if (isMobile) {
                // Show mobile upload options on mobile/tablet devices
                mobileOptions.style.display = 'flex';
            } else {
                // Hide mobile options on desktop
                mobileOptions.style.display = 'none';
            }
            
            // Log the detection for debugging
            console.log(`Device detection: ${isMobile ? 'Mobile/Tablet' : 'Desktop'}`);
        }
    } else {
        console.warn('isMobileOrTablet function not available, unable to set device-specific UI');
    }
}

// Sourcedir description functionality
function editSourcedirDescription() {
    const descriptionDisplay = document.getElementById('sourcedir-description-display');
    const currentDescription = descriptionDisplay.querySelector('p');
    const currentText = currentDescription.classList.contains('no-description') ? '' : currentDescription.textContent.trim();
    
    // Create edit container
    const editContainer = document.createElement('div');
    editContainer.className = 'description-edit';
    
    // Create textarea
    const textarea = document.createElement('textarea');
    textarea.id = 'sourcedir-description-editor';
    textarea.value = currentText;
    textarea.placeholder = 'Enter description for this directory...';
    
    // Create buttons
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'description-edit-buttons';
    
    const saveButton = document.createElement('button');
    saveButton.className = 'button small-button success-btn';
    saveButton.innerHTML = '<i class="fas fa-save"></i> Save';
    saveButton.onclick = saveSourcedirDescription;
    
    const cancelButton = document.createElement('button');
    cancelButton.className = 'button small-button';
    cancelButton.innerHTML = '<i class="fas fa-times"></i> Cancel';
    cancelButton.onclick = cancelEditSourcedirDescription;
    
    // Add elements to the DOM
    buttonsContainer.appendChild(saveButton);
    buttonsContainer.appendChild(cancelButton);
    editContainer.appendChild(textarea);
    editContainer.appendChild(buttonsContainer);
    
    // Replace display with edit view
    descriptionDisplay.innerHTML = '';
    descriptionDisplay.appendChild(editContainer);
    
    // Focus the textarea
    textarea.focus();
}

function saveSourcedirDescription() {
    const textarea = document.getElementById('sourcedir-description-editor');
    const description = textarea.value.trim();
    
    // Show loading state
    textarea.disabled = true;
    
    // Save the description
    fetch(resolveRoute('SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_DESCRIPTION', {
            target_language_code: window.target_language_code,
            sourcedir_slug: window.sourcedir_slug
        }), {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: description })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to update description');
        }
        
        // Update the display
        const descriptionDisplay = document.getElementById('sourcedir-description-display');
        if (description) {
            descriptionDisplay.innerHTML = `<p>${description}</p>`;
        } else {
            descriptionDisplay.innerHTML = `<p class="no-description"><em>No description available</em></p>`;
        }
    })
    .catch(error => {
        alert(`Error: ${error.message}`);
        // Re-enable the textarea
        textarea.disabled = false;
    });
}

function cancelEditSourcedirDescription() {
    // Get the current description from the server state
    fetch(resolveRoute('SOURCEDIR_VIEWS_SOURCEFILE_LIST', {
        target_language_code: window.target_language_code,
        sourcedir_slug: window.sourcedir_slug
    }))
        .then(response => response.text())
        .then(html => {
            // Parse the HTML to extract the current description
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const descriptionElement = doc.getElementById('sourcedir-description-display');
            
            // Restore the display
            if (descriptionElement) {
                document.getElementById('sourcedir-description-display').innerHTML = descriptionElement.innerHTML;
            } else {
                // Fallback if we can't parse the description from the response
                window.location.reload();
            }
        })
        .catch(() => {
            // If there's an error, just reload the page
            window.location.reload();
        });
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', init); 