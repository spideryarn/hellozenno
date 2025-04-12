import { Queue } from 'queue-typescript';
import { writable } from 'svelte/store';
import { getApiUrl } from './api';
import { RouteName } from './generated/routes';

// Define processing step types
export type ProcessingStep =
  | 'text_extraction'
  | 'translation'
  | 'wordforms'
  | 'phrases';

// Define a step with its API endpoint and parameters
export interface QueuedStep {
  type: ProcessingStep;
  apiEndpoint: string;
  params: Record<string, any>;
  description: string;
}

// Create a store for tracking progress
export const processingState = writable({
  isProcessing: false,
  currentStep: null as ProcessingStep | null,
  progress: 0,
  totalSteps: 0,
  error: null as string | null,
  description: ''
});

export class SourcefileProcessingQueue {
  private queue: Queue<QueuedStep>;
  private sourcefileData: {
    target_language_code: string;
    sourcedir_slug: string;
    sourcefile_slug: string;
  };

  constructor(target_language_code: string, sourcedir_slug: string, sourcefile_slug: string) {
    this.queue = new Queue<QueuedStep>();
    this.sourcefileData = {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug
    };
  }

  // Add the necessary steps based on what's needed
  public initializeQueue(sourcefile: any) {
    // Clear the existing queue
    this.queue = new Queue<QueuedStep>();

    // Check if text extraction is needed (for image or audio files)
    if (!sourcefile.text_target && (sourcefile.has_image || sourcefile.has_audio)) {
      this.queue.enqueue({
        type: 'text_extraction',
        apiEndpoint: getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API,
          {
            target_language_code: this.sourcefileData.target_language_code,
            sourcedir_slug: this.sourcefileData.sourcedir_slug,
            sourcefile_slug: this.sourcefileData.sourcefile_slug
          }
        ),
        params: {},
        description: 'Extracting text'
      });
    }

    // Check if translation is needed
    if (!sourcefile.text_english && sourcefile.text_target) {
      this.queue.enqueue({
        type: 'translation',
        apiEndpoint: getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_TRANSLATE_API,
          {
            target_language_code: this.sourcefileData.target_language_code,
            sourcedir_slug: this.sourcefileData.sourcedir_slug,
            sourcefile_slug: this.sourcefileData.sourcefile_slug
          }
        ),
        params: {},
        description: 'Translating text'
      });
    }

    // Always add wordforms and phrases processing
    this.queue.enqueue({
      type: 'wordforms',
      apiEndpoint: getApiUrl(
        RouteName.SOURCEFILE_PROCESSING_API_PROCESS_WORDFORMS_API,
        {
          target_language_code: this.sourcefileData.target_language_code,
          sourcedir_slug: this.sourcefileData.sourcedir_slug,
          sourcefile_slug: this.sourcefileData.sourcefile_slug
        }
      ),
      params: {},
      description: 'Extracting vocabulary'
    });

    this.queue.enqueue({
      type: 'phrases',
      apiEndpoint: getApiUrl(
        RouteName.SOURCEFILE_PROCESSING_API_PROCESS_PHRASES_API,
        {
          target_language_code: this.sourcefileData.target_language_code,
          sourcedir_slug: this.sourcefileData.sourcedir_slug,
          sourcefile_slug: this.sourcefileData.sourcefile_slug
        }
      ),
      params: {},
      description: 'Extracting phrases'
    });

    // Update the store with the total steps
    processingState.update(state => ({
      ...state,
      totalSteps: this.queue.length,
      progress: 0
    }));

    return this.queue.length > 0;
  }

  // Process the next step in the queue
  public async processNextStep() {
    if (this.queue.length === 0) {
      processingState.update(state => ({
        ...state,
        isProcessing: false,
        currentStep: null,
        progress: state.totalSteps,
      }));
      return false;
    }

    const step = this.queue.dequeue();

    processingState.update(state => ({
      ...state,
      isProcessing: true,
      currentStep: step.type,
      description: step.description,
      error: null,
    }));

    try {
      const response = await fetch(step.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(step.params),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `Failed to process ${step.type}`);
      }

      processingState.update(state => ({
        ...state,
        progress: state.totalSteps - this.queue.length,
      }));

      return true;
    } catch (error) {
      processingState.update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
      return false;
    }
  }

  // Start processing the entire queue
  public async processAll() {
    processingState.update(state => ({
      ...state,
      isProcessing: true,
      progress: 0,
      error: null,
    }));

    while (this.queue.length > 0) {
      const success = await this.processNextStep();
      if (!success) {
        break;
      }
    }

    processingState.update(state => ({
      ...state,
      isProcessing: this.queue.length > 0,
    }));

    return this.queue.length === 0;
  }
}