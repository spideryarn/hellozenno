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

    fetch(resolveRoute('SENTENCE_API_GENERATE_SENTENCE_AUDIO_API', {
        target_language_code: window.target_language_code,
        slug: window.sentence_slug
    }), {
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

// Sentence operations
async function renameSentence() {
    try {
        const newText = await showModal({
            placeholder: "Enter new sentence text",
            defaultValue: window.sentence_text,
            confirmText: "Rename",
            cancelText: "Cancel"
        });

        const response = await fetch(
            resolveRoute('SENTENCE_API_RENAME_SENTENCE_API', {
                target_language_code: window.target_language_code,
                slug: window.sentence_slug
            }),
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_text: newText })
            }
        );

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to rename sentence');
        }

        const { new_text, new_slug } = await response.json();
        window.location.href = resolveRoute('SENTENCE_VIEWS_GET_SENTENCE_VW', {
            target_language_code: window.target_language_code,
            slug: new_slug
        });
    } catch (error) {
        if (error.message !== 'User cancelled') {
            alert('Error renaming sentence: ' + error.message);
        }
    }
}

function deleteSentence() {
    if (confirm('Are you sure you want to delete this sentence? This action cannot be undone.')) {
        fetch(resolveRoute('SENTENCE_API_DELETE_SENTENCE_API', {
            target_language_code: window.target_language_code,
            slug: window.sentence_slug
        }), {
            method: 'DELETE',
        }).then(response => {
            if (response.ok) {
                window.location.href = resolveRoute('SENTENCE_VIEWS_SENTENCES_LIST_VW', {
                    target_language_code: window.target_language_code
                });
            } else {
                alert('Failed to delete sentence');
            }
        });
    }
} 