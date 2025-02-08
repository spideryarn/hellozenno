/*
 * Sentence Flashcards - Interactive Learning Interface
 * See docs/FLASHCARDS.md for detailed documentation of the behavior
 */

// State variables
let currentStage = 1; // 1: audio, 2: text, 3: translation

// DOM elements
const audioPlayer = document.getElementById('audio-player');
const sentenceElem = document.getElementById('sentence');
const translationElem = document.getElementById('translation');
const lemmaWordsElem = document.getElementById('lemma-words');
const errorMessageElem = document.getElementById('error-message');
const leftBtn = document.getElementById('left-btn');
const rightBtn = document.getElementById('right-btn');
const nextBtn = document.getElementById('next-btn');

// UI functions
function hideAllElements() {
    const stage2Content = document.getElementById('stage2-content');
    stage2Content.classList.add('d-none');
    stage2Content.style.display = 'none';

    sentenceElem.classList.add('d-none');
    sentenceElem.style.display = 'none';

    translationElem.classList.add('d-none');
    translationElem.style.display = 'none';

    lemmaWordsElem.classList.add('d-none');
    lemmaWordsElem.style.display = 'none';

    errorMessageElem.classList.add('d-none');
}

function updateStage(newStage) {
    currentStage = newStage;
    hideAllElements();

    // Update button states and labels based on stage
    switch (currentStage) {
        case 1:
            // Stage 1: Audio only
            leftBtn.innerHTML = '<i class="fas fa-play"></i> Play Audio <span class="shortcut-hint">(←)</span>';
            rightBtn.innerHTML = '<i class="fas fa-eye"></i> Show Sentence <span class="shortcut-hint">(→)</span>';
            leftBtn.classList.add('active');
            rightBtn.classList.remove('active');
            rightBtn.disabled = false;
            playAudio();
            break;
        case 2:
            // Stage 2: Show sentence
            leftBtn.innerHTML = '<i class="fas fa-play"></i> Play Audio <span class="shortcut-hint">(←)</span>';
            rightBtn.innerHTML = '<i class="fas fa-language"></i> Show Translation <span class="shortcut-hint">(→)</span>';
            leftBtn.classList.remove('active');
            rightBtn.classList.remove('active');
            rightBtn.disabled = false;
            showSentence();
            break;
        case 3:
            // Stage 3: Show translation
            leftBtn.innerHTML = '<i class="fas fa-eye"></i> Show Sentence <span class="shortcut-hint">(←)</span>';
            rightBtn.innerHTML = '<i class="fas fa-language"></i> Show Translation <span class="shortcut-hint">(→)</span>';
            leftBtn.classList.remove('active');
            rightBtn.classList.add('active');
            rightBtn.disabled = true;
            showSentence();
            showTranslation();
            break;
    }
}

function showError(message) {
    errorMessageElem.textContent = message;
    errorMessageElem.classList.remove('d-none');
}

function showSentence() {
    const stage2Content = document.getElementById('stage2-content');
    stage2Content.classList.remove('d-none');
    stage2Content.style.display = 'block';

    sentenceElem.classList.remove('d-none');
    sentenceElem.style.display = 'block';
}

function showTranslation() {
    translationElem.classList.remove('d-none');
    translationElem.style.display = 'block';
    lemmaWordsElem.classList.remove('d-none');
    lemmaWordsElem.style.display = 'block';
}

// Audio functions
async function playAudio() {
    try {
        const playPromise = audioPlayer.play();
        if (playPromise !== undefined) {
            await playPromise;
            console.log('Audio playback started successfully');
        }
    } catch (error) {
        console.error('Error playing audio:', error);
        showError('Error playing audio');
    }
}

// Button handlers
function handleLeftClick() {
    if (currentStage === 2 || currentStage === 3) {
        updateStage(currentStage === 2 ? 1 : 2);
    } else {
        playAudio();
    }
}

function handleRightClick() {
    if (currentStage === 1) {
        updateStage(2);
    } else if (currentStage === 2) {
        updateStage(3);
    }
}

function handleNextClick() {
    // Build URL with lemma parameters if we have lemmas
    let url = `/${window.target_language_code}/flashcards/random`;
    const params = new URLSearchParams();

    // Add lemmas if we have them
    if (window.lemmas && window.lemmas.length > 0) {
        window.lemmas.forEach(lemma => params.append('lemmas[]', lemma));
    }

    // Add sourcefile if we have it
    if (window.sourcefile) {
        params.append('sourcefile', window.sourcefile);
    }

    // Add sourcedir if we have it
    if (window.sourcedir) {
        params.append('sourcedir', window.sourcedir);
    }

    // Add params to URL if we have any
    if (params.toString()) {
        url += '?' + params.toString();
    }

    window.location.href = url;
}

// Event handlers
function handleKeydown(event) {
    // Ignore keyboard shortcuts if user is typing in an input field
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
    }

    switch (event.key) {
        case 'ArrowRight':
            if (!rightBtn.disabled) {
                handleRightClick();
            }
            break;
        case 'ArrowLeft':
            handleLeftClick();
            break;
        case 'Enter':
            handleNextClick();
            break;
    }
}

// Initialization
function init() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', handleKeydown);

    // Start at Stage 1 with auto-play audio
    updateStage(1);
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', init); 
