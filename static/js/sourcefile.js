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

    fetch(`/api/sourcefile/${window.target_language_code}/${window.sourcedir_slug}/${window.sourcefile_slug}/update_description`, {
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

    fetch(`/api/sourcefile/${window.target_language_code}/${window.sourcedir_slug}/${window.sourcefile_slug}/generate_audio`, {
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

        const response = await fetch(
            `/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/${window.sourcefile_slug}/rename`,
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
            throw new Error(data.error || 'Failed to rename file');
        }

        const { new_name, new_slug } = await response.json();
        window.location.href = `/${window.target_language_code}/${window.sourcedir_slug}/${new_slug}`;
    } catch (error) {
        if (error.message !== 'User cancelled') {
            alert('Error renaming file: ' + error.message);
        }
    }
}

function deleteSourcefile() {
    if (confirm('Are you sure you want to delete this sourcefile? This action cannot be undone.')) {
        fetch(`/api/sourcedir/${window.target_language_code}/${window.sourcedir_slug}/${window.sourcefile_slug}`, {
            method: 'DELETE',
        }).then(response => {
            if (response.ok) {
                window.location.href = `/${window.target_language_code}/${window.sourcedir_slug}`;
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

    fetch(`/api/sourcefile/${window.target_language_code}/${window.sourcedir_slug}/${window.sourcefile_slug}/process_individual`, {
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