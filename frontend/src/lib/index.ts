// place files you want to import through the `$lib` alias in this folder.

// Re-export components for easy imports
export { default as Card } from "./components/Card.svelte";
export { default as Sentence } from "./components/Sentence.svelte";
export { default as SourceItem } from "./components/SourceItem.svelte";
export { default as WordformCard } from "./components/WordformCard.svelte";
export { default as LemmaCard } from "./components/LemmaCard.svelte";
export { default as MetadataCard } from "./components/MetadataCard.svelte";
export { default as PhraseCard } from "./components/PhraseCard.svelte";
export { default as SentenceCard } from "./components/SentenceCard.svelte";
export { default as DescriptionFormatted } from "./components/DescriptionFormatted.svelte";

// Re-export utility functions
export * from "./utils";
export * from "./api";
export * from "./types";
