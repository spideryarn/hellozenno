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