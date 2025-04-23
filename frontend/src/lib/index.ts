// place files you want to import through the `$lib` alias in this folder.

// Re-export components for easy imports
export { default as Card } from "./components/Card.svelte";
export { default as Sentence } from "./components/Sentence.svelte";
export { default as SourceItem } from "./components/SourceItem.svelte";
export { default as WordformCard } from "./components/WordformCard.svelte";
export { default as LemmaCard } from "./components/LemmaCard.svelte";
export { default as LemmaContent } from "./components/LemmaContent.svelte";
export { default as LemmaDetails } from "./components/LemmaDetails.svelte";
export { default as MetadataCard } from "./components/MetadataCard.svelte";
export { default as PhraseCard } from "./components/PhraseCard.svelte";
export { default as SentenceCard } from "./components/SentenceCard.svelte";
export { default as DescriptionFormatted } from "./components/DescriptionFormatted.svelte";
export { default as CollapsibleHeader } from "./components/CollapsibleHeader.svelte";
export { default as MetadataSection } from "./components/MetadataSection.svelte";
export { default as DescriptionSection } from "./components/DescriptionSection.svelte";
export { default as FileOperationsSection } from "./components/FileOperationsSection.svelte";
export { default as DirectoryOperationsSection } from "./components/DirectoryOperationsSection.svelte";
export { default as SourcedirHeader } from "./components/SourcedirHeader.svelte";
export { default as SourcefileImage } from "./components/SourcefileImage.svelte";
export { default as SourcefileAudio } from "./components/SourcefileAudio.svelte";
export { default as NavTabs } from "./components/NavTabs.svelte";
export { default as LoadingSpinner } from "./components/LoadingSpinner.svelte";
export { default as SearchBarMini } from "./components/SearchBarMini.svelte";

// Re-export utility functions
export * from "./utils";
export * from "./api";
export * from "./types";
export * from "./processing-queue";