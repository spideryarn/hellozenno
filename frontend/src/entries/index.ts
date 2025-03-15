/**
 * Central export file for all Svelte components
 * This file serves as the entry point for the library build
 */

// Import all component classes
import MiniLemma from '../components/MiniLemma.svelte';
import MiniSentence from '../components/MiniSentence.svelte';
import MiniWordform from '../components/MiniWordform.svelte';
import MiniWordformList from '../components/MiniWordformList.svelte';
import MiniPhrase from '../components/MiniPhrase.svelte';
import Sentence from '../components/Sentence.svelte';
import FlashcardApp from '../components/FlashcardApp.svelte';
import FlashcardLanding from '../components/FlashcardLanding.svelte';
// Add other components as needed

// Export all component classes
export {
  MiniLemma,
  MiniSentence,
  MiniWordform,
  MiniWordformList,
  MiniPhrase,
  Sentence,
  FlashcardApp,
  FlashcardLanding
};

// Create a component registry with factory functions
const components = {
  minilemma: (target: HTMLElement, props: any) => new MiniLemma({ target, props }),
  minisentence: (target: HTMLElement, props: any) => new MiniSentence({ target, props }),
  miniwordform: (target: HTMLElement, props: any) => new MiniWordform({ target, props }),
  miniwordformlist: (target: HTMLElement, props: any) => new MiniWordformList({ target, props }),
  miniphrase: (target: HTMLElement, props: any) => new MiniPhrase({ target, props }),
  sentence: (target: HTMLElement, props: any) => new Sentence({ target, props }),
  flashcardapp: (target: HTMLElement, props: any) => new FlashcardApp({ target, props }),
  flashcardlanding: (target: HTMLElement, props: any) => new FlashcardLanding({ target, props })
};

// Export default component registry
export default components;

// Also expose the components to window for direct script tag access
declare global {
  interface Window {
    HzComponents: {
      components: typeof components;
      MiniLemma: typeof MiniLemma;
      MiniSentence: typeof MiniSentence;
      MiniWordform: typeof MiniWordform;
      MiniWordformList: typeof MiniWordformList;
      MiniPhrase: typeof MiniPhrase;
      Sentence: typeof Sentence;
      FlashcardApp: typeof FlashcardApp;
      FlashcardLanding: typeof FlashcardLanding;
    };
  }
}

// Expose components to window in development mode
if (typeof window !== 'undefined') {
  window.HzComponents = {
    components,
    MiniLemma,
    MiniSentence,
    MiniWordform,
    MiniWordformList,
    MiniPhrase,
    Sentence,
    FlashcardApp,
    FlashcardLanding
  };
}