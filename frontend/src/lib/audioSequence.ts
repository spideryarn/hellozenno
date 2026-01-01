/**
 * Audio sequence playback utilities.
 * Shared by LemmaAudioButton, SentenceAudioButton, and other audio playback components.
 */

/**
 * Fisher-Yates shuffle - returns a new shuffled array without modifying the original.
 */
export function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export interface PlaybackCallbacks {
  onStart?: (total: number) => void;
  onProgress?: (current: number, total: number) => void;
  onComplete?: () => void;
  onCancel?: () => void;
  onError?: (error: Error, index: number) => void;
}

export interface PlaybackHandle {
  cancel: () => void;
}

/**
 * Plays a sequence of audio URLs one after another.
 * Returns a handle with a cancel() method to stop playback.
 * 
 * @param urls - Array of audio URLs to play sequentially
 * @param callbacks - Optional callbacks for playback events
 * @returns PlaybackHandle with cancel() method
 */
export function playAudioSequence(
  urls: string[],
  callbacks?: PlaybackCallbacks
): PlaybackHandle {
  let cancelled = false;
  let currentAudio: HTMLAudioElement | null = null;
  const audioElements: HTMLAudioElement[] = [];

  if (!urls.length) {
    callbacks?.onComplete?.();
    return { cancel: () => {} };
  }

  // Pre-create audio elements for preloading
  urls.forEach((url) => {
    const audio = new Audio(url);
    audio.preload = 'auto';
    audioElements.push(audio);
  });

  callbacks?.onStart?.(urls.length);

  let index = 0;

  const cleanup = () => {
    audioElements.forEach((audio) => {
      audio.onended = null;
      audio.onerror = null;
      audio.pause();
      audio.removeAttribute('src');
      audio.load();
    });
    currentAudio = null;
  };

  const playNext = () => {
    if (cancelled) {
      return;
    }

    if (index >= audioElements.length) {
      callbacks?.onProgress?.(urls.length, urls.length);
      cleanup();
      callbacks?.onComplete?.();
      return;
    }

    currentAudio = audioElements[index];
    const currentIndex = index;
    index += 1;
    callbacks?.onProgress?.(index, urls.length);

    currentAudio.onended = playNext;
    currentAudio.onerror = () => {
      if (cancelled) return;
      callbacks?.onError?.(new Error('Audio playback failed'), currentIndex);
      playNext();
    };
    currentAudio.play().catch((err) => {
      if (cancelled) return;
      callbacks?.onError?.(err, currentIndex);
      playNext();
    });
  };

  playNext();

  return {
    cancel: () => {
      cancelled = true;
      if (currentAudio) {
        currentAudio.pause();
      }
      cleanup();
      callbacks?.onCancel?.();
    },
  };
}
