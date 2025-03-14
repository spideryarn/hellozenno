// Reusable modal functions
function showModal(options) {
    const modal = document.getElementById('reusableModal');
    const input = document.getElementById('modalInput');
    const confirmBtn = document.getElementById('modalConfirm');
    const cancelBtn = document.getElementById('modalCancel');

    // Set up the modal
    input.value = options.defaultValue || '';
    input.placeholder = options.placeholder || '';
    confirmBtn.textContent = options.confirmText || 'Confirm';
    cancelBtn.textContent = options.cancelText || 'Cancel';

    // Show the modal
    modal.classList.add('show');
    input.focus();

    // Return a promise that resolves with the input value or rejects if cancelled
    return new Promise((resolve, reject) => {
        const handleConfirm = () => {
            const value = input.value.trim();
            if (value) {
                cleanup();
                resolve(value);
            }
        };

        const handleCancel = () => {
            cleanup();
            reject(new Error('User cancelled'));
        };

        const handleKeydown = (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                handleConfirm();
            } else if (event.key === 'Escape') {
                event.preventDefault();
                handleCancel();
            }
        };

        const handleClickOutside = (event) => {
            if (event.target === modal) {
                handleCancel();
            }
        };

        // Set up event listeners
        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        input.addEventListener('keydown', handleKeydown);
        modal.addEventListener('click', handleClickOutside);

        // Cleanup function to remove event listeners
        function cleanup() {
            modal.classList.remove('show');
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
            input.removeEventListener('keydown', handleKeydown);
            modal.removeEventListener('click', handleClickOutside);
        }
    });
}

// Initialize Tippy.js for all word links
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded - checking for Tippy.js');

    // Check if Tippy.js is loaded
    if (typeof tippy === 'undefined') {
        console.error('Tippy.js is not loaded! This will cause errors.');
        // Continue with other initialization that doesn't depend on tippy
    } else {
        console.log('Tippy.js is loaded, initializing tooltips');
        // Initialize Tippy.js for all word links
        tippy('.word-link', {
            content: 'Loading...',
            allowHTML: true,
            theme: 'light',
            placement: 'bottom',
            touch: true,
            touchHold: true,
            interactive: true,
            appendTo: document.body,
            maxWidth: 300,
            delay: [200, 0],
            onShow(instance) {
                // Hide all other tooltips when showing a new one
                document.querySelectorAll('[data-tippy-root]').forEach(tooltip => {
                    const tippyInstance = tooltip._tippy;
                    if (tippyInstance && tippyInstance !== instance) {
                        tippyInstance.hide();
                    }
                });

                // Get the word from the link text content instead of URL
                const link = instance.reference;
                const word = link.textContent.trim();
                const url = new URL(link.href);
                const pathParts = url.pathname.split('/');
                const langCode = pathParts[1];

                console.log(`Fetching preview for word: "${word}" in language: ${langCode}`);

                // Fetch preview data from API
                fetch(`/api/word-preview/${langCode}/${encodeURIComponent(word)}`)
                    .then(r => {
                        if (!r.ok) {
                            throw new Error(`API request failed: ${r.status}`);
                        }
                        return r.json();
                    })
                    .then(data => {
                        console.log(`Preview data for "${word}":`, data);
                        instance.setContent(`
                            <h4>${data.lemma}</h4>
                            ${data.translation ? `<p class="translation">Translation: ${data.translation}</p>` : ''}
                            ${data.etymology ? `<p class="etymology">Etymology: ${data.etymology}</p>` : ''}
                        `);
                    })
                    .catch(error => {
                        console.error(`Error fetching preview for "${word}":`, error);
                        instance.setContent('Error loading preview');
                    });
            }
        });

        // Initialize Tippy.js for sourcefile icons
        tippy('.sourcefile-icon', {
            theme: 'light',
            placement: 'right',
            touch: true,
            touchHold: true,
            delay: [200, 0],
            allowHTML: true,
            content(reference) {
                const content = reference.getAttribute('data-tippy-content');
                return content.replace(/\n/g, '<br>');
            }
        });
    }

    console.log('DOM initialization complete');
});

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

// Audio generation UI helpers
function showAudioGenerationProgress() {
    const button = document.querySelector('button[onclick="generateAudio()"]');
    const progress = document.getElementById('audioGenerationProgress');
    if (button && progress) {
        button.style.display = 'none';
        progress.style.display = 'block';
    }
}

function hideAudioGenerationProgress() {
    const button = document.querySelector('button[onclick="generateAudio()"]');
    const progress = document.getElementById('audioGenerationProgress');
    if (button && progress) {
        button.style.display = 'block';
        progress.style.display = 'none';
    }
}