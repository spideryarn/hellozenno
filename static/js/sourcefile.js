// Audio playback controls
function setPlaybackRate(rate) {
    const audio = document.getElementById('audioPlayer');
    if (audio) {
        audio.playbackRate = rate;
        document.querySelectorAll('.speed-controls button').forEach(btn => {
            btn.classList.remove('active');
            const btnRate = parseFloat(btn.textContent);
            if (btnRate === rate) {
                btn.classList.add('active');
            }
        });
    }
}

// Description editing
function editDescription() {
    const descriptionDisplay = document.getElementById('description-display');
    const currentDescription = descriptionDisplay.querySelector('p').textContent.trim();
    const isNoDescription = descriptionDisplay.querySelector('.no-description') !== null;

    // Create editor if it doesn't exist
    if (!document.getElementById('description-editor')) {
        const editor = document.createElement('div');
        editor.id = 'description-editor';

        const textarea = document.createElement('textarea');
        textarea.id = 'description-textarea';
        textarea.placeholder = 'Enter a description for this file...';

        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'button-group';

        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';
        saveButton.className = 'button';
        saveButton.onclick = saveDescription;

        const cancelButton = document.createElement('button');
        cancelButton.textContent = 'Cancel';
        cancelButton.className = 'button';
        cancelButton.onclick = cancelEditDescription;

        buttonGroup.appendChild(cancelButton);
        buttonGroup.appendChild(saveButton);

        editor.appendChild(textarea);
        editor.appendChild(buttonGroup);

        descriptionDisplay.parentNode.insertBefore(editor, descriptionDisplay.nextSibling);
    }

    // Show editor and hide display
    const editor = document.getElementById('description-editor');
    const textarea = document.getElementById('description-textarea');

    // Set current description in textarea (if not the placeholder)
    textarea.value = isNoDescription ? '' : currentDescription;

    editor.style.display = 'block';
    descriptionDisplay.style.display = 'none';
}

function saveDescription() {
    const textarea = document.getElementById('description-textarea');
    const description = textarea.value.trim();

    // Show loading state
    const saveButton = textarea.nextElementSibling.querySelector('button:last-child');
    const originalText = saveButton.textContent;
    saveButton.disabled = true;
    saveButton.innerHTML = `Saving... <div class="spinner"></div>`;

    const url = resolveRoute('SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API', {
        target_language_code: window.target_language_code,
        sourcedir_slug: window.sourcedir_slug,
        sourcefile_slug: window.sourcefile_slug
    });
    
    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: description })
    }).then(async response => {
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to update description');
        }

        // Update the displayed description
        const descriptionDisplay = document.getElementById('description-display');
        const descriptionParagraph = descriptionDisplay.querySelector('p');

        if (description) {
            if (descriptionParagraph.classList.contains('no-description')) {
                descriptionParagraph.classList.remove('no-description');
                descriptionParagraph.innerHTML = description;
            } else {
                descriptionParagraph.textContent = description;
            }
        } else {
            descriptionParagraph.classList.add('no-description');
            descriptionParagraph.innerHTML = '<em>No description available</em>';
        }

        // Hide editor and show display
        document.getElementById('description-editor').style.display = 'none';
        descriptionDisplay.style.display = 'block';
    }).catch(error => {
        alert('Error updating description: ' + error.message);
    }).finally(() => {
        // Reset button state
        saveButton.disabled = false;
        saveButton.textContent = originalText;
    });
}

function cancelEditDescription() {
    // Hide editor and show display
    document.getElementById('description-editor').style.display = 'none';
    document.getElementById('description-display').style.display = 'block';
}

// Audio generation
function generateAudio() {
    showAudioGenerationProgress();

    const url = resolveRoute('SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API', {
        target_language_code: window.target_language_code,
        sourcedir_slug: window.sourcedir_slug,
        sourcefile_slug: window.sourcefile_slug
    });
    
    fetch(url, {
        method: 'POST'
    }).then(async response => {
        if (response.status === 204) {
            window.location.reload();
            return;
        }

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate audio');
        }
        window.location.reload();
    }).catch(error => {
        alert('Error generating audio: ' + error.message);
        hideAudioGenerationProgress();
    });
}

// File operations
async function renameSourcefile() {
    try {
        const newName = await showModal({
            placeholder: "Enter new filename",
            defaultValue: window.sourcefile,
            confirmText: "Rename",
            cancelText: "Cancel"
        });

        const url = resolveRoute('SOURCEFILE_API_RENAME_SOURCEFILE_API', {
            target_language_code: window.target_language_code,
            sourcedir_slug: window.sourcedir_slug,
            sourcefile_slug: window.sourcefile_slug
        });
        
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ new_name: newName })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to rename file');
        }

        const { new_name, new_slug } = await response.json();
        const redirectUrl = resolveRoute('SOURCEFILE_VIEWS_SOURCEFILE', {
            target_language_code: window.target_language_code,
            sourcedir_slug: window.sourcedir_slug,
            sourcefile_slug: new_slug
        });
        window.location.href = redirectUrl;
    } catch (error) {
        if (error.message !== 'User cancelled') {
            alert('Error renaming file: ' + error.message);
        }
    }
}

function deleteSourcefile() {
    if (confirm('Are you sure you want to delete this sourcefile? This action cannot be undone.')) {
        const url = resolveRoute('SOURCEFILE_API_DELETE_SOURCEFILE_API', {
            target_language_code: window.target_language_code,
            sourcedir_slug: window.sourcedir_slug,
            sourcefile_slug: window.sourcefile_slug
        });
        
        fetch(url, {
            method: 'DELETE',
        }).then(response => {
            if (response.ok) {
                const redirectUrl = resolveRoute('SOURCEFILE_VIEWS_SOURCEFILES_LIST', {
                    target_language_code: window.target_language_code,
                    sourcedir_slug: window.sourcedir_slug
                });
                window.location.href = redirectUrl;
            } else {
                alert('Failed to delete sourcefile');
            }
        });
    }
}

function processIndividualWords() {
    // Show progress indicator
    const button = document.querySelector('button[onclick="processIndividualWords()"]');
    const originalText = button.textContent;
    button.disabled = true;
    button.innerHTML = `Processing... <div class="spinner"></div>`;

    const url = resolveRoute('SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API', {
        target_language_code: window.target_language_code,
        sourcedir_slug: window.sourcedir_slug,
        sourcefile_slug: window.sourcefile_slug
    });
    
    fetch(url, {
        method: 'POST'
    }).then(async response => {
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to process individual words');
        }
        // Show success message before reloading
        button.innerHTML = 'Processing complete!';
        setTimeout(() => window.location.reload(), 1000);
    }).catch(error => {
        alert('Error processing individual words: ' + error.message);
        // Reset button on error
        button.disabled = false;
        button.textContent = originalText;
    });
}

// Sourcedir selector functionality
function initSourcedirSelector() {
    const selector = document.querySelector('.sourcedir-selector');
    
    if (selector) {
        selector.addEventListener('change', function() {
            const newSourcedirSlug = this.value;
            
            // Don't do anything if nothing is selected
            if (!newSourcedirSlug) {
                return;
            }
            
            // Show confirmation dialog
            if (confirm('Are you sure you want to move this file to a different directory?')) {
                // Show loading indicator
                this.disabled = true;
                
                // Store the original option text
                const selectedIndex = this.selectedIndex;
                const originalText = this.options[selectedIndex].text;
                this.options[selectedIndex].text = 'Moving...';
                
                const url = resolveRoute('SOURCEFILE_API_MOVE_SOURCEFILE_API', {
                    target_language_code: window.target_language_code,
                    sourcedir_slug: window.sourcedir_slug,
                    sourcefile_slug: window.sourcefile_slug
                });
                
                fetch(url, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ new_sourcedir_slug: newSourcedirSlug })
                }).then(async response => {
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Failed to move file');
                    }
                    
                    // Redirect to the file in its new location
                    const redirectUrl = resolveRoute('SOURCEFILE_VIEWS_SOURCEFILE', {
                        target_language_code: window.target_language_code,
                        sourcedir_slug: data.new_sourcedir_slug,
                        sourcefile_slug: data.new_sourcefile_slug
                    });
                    window.location.href = redirectUrl;
                }).catch(error => {
                    alert('Error moving file: ' + error.message);
                    // Reset the dropdown
                    this.options[selectedIndex].text = originalText;
                    this.selectedIndex = 0; // Reset to the first option (placeholder)
                    this.disabled = false;
                });
            } else {
                // Reset selection if user cancels
                this.selectedIndex = 0; // Reset to the first option (placeholder)
            }
        });
    }
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initSourcedirSelector();
}); 