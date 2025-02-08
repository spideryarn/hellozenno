// File deletion
function deleteSourcefile(slug) {
    if (confirm('Are you sure you want to delete this sourcefile? This action cannot be undone.')) {
        fetch(`/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/${slug}`, {
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
            `/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/rename`,
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
        window.location.href = `/${window.target_language_code}/${data.slug}`;
    } catch (error) {
        if (error.message !== 'User cancelled') {
            alert('Error renaming directory: ' + error.message);
        }
    }
}

function deleteSourcedir() {
    if (confirm('Are you sure you want to delete this directory? This action cannot be undone.')) {
        fetch(`/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}`, {
            method: 'DELETE',
        }).then(response => {
            if (response.ok) {
                window.location.href = `/${window.target_language_code}`;
            } else {
                alert('Failed to delete directory');
            }
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
            `/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/upload`,
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

        fetch(`/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/language`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ language_code: newLanguage })
        }).then(response => {
            if (response.ok) {
                window.location.href = `/${newLanguage}/${e.target.dataset.sourcedirSlug}`;
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
                `/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/create_from_text`,
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
            window.location.href = `/${window.target_language_code}/${window.sourcedir_slug}/${data.slug}`;
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
                `/${window.target_language_code}/${window.sourcedir_slug}/add_from_youtube`,
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

            window.location.href = `/${window.target_language_code}/${window.sourcedir_slug}/${data.slug}`;
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
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', init); 