import { Queue } from 'queue-typescript';
import { writable } from 'svelte/store';
import { getApiUrl } from './api';
import { RouteName } from './generated/routes';
import type { SupabaseClient } from '@supabase/supabase-js';

// Define processing step types
export type ProcessingStep =
  | 'text_extraction'
  | 'translation'
  | 'wordforms'
  | 'phrases'
  | 'lemma_metadata';

// Define a step with its API endpoint and parameters
export interface QueuedStep {
  type: ProcessingStep;
  apiEndpoint: string;
  params: Record<string, any>;
  description: string;
  lemma?: string; // Optional: for lemma_metadata steps
}

// Define the shape of the status object from the API
interface SourcefileStatus {
  has_text: boolean;
  has_translation: boolean;
  wordforms_count: number;
  phrases_count: number;
  incomplete_lemmas: Array<{
    lemma: string;
    part_of_speech?: string;
    translations?: string[];
  }>;
  incomplete_lemmas_count: number;
}

// Create a store for tracking progress
export const processingState = writable({
  isProcessing: false,
  currentStep: null as ProcessingStep | null,
  progress: 0,
  totalSteps: 0,
  error: null as string | null,
  description: '',
  currentIteration: 0,
  totalIterations: 1,
  processedSourcefileData: null as any // Will contain the updated sourcefile data after processing
});

export class SourcefileProcessingQueue {
  private queue: Queue<QueuedStep>;
  private sourcefileData: {
    target_language_code: string;
    sourcedir_slug: string;
    sourcefile_slug: string;
  };
  private sourcefileType: 'text' | 'image' | 'audio'; // Track sourcefile type
  private supabaseClient: SupabaseClient | null; // Store the client instance

  constructor(
    supabaseClient: SupabaseClient | null, // Accept client instance
    target_language_code: string,
    sourcedir_slug: string,
    sourcefile_slug: string,
    sourcefile_type: 'text' | 'image' | 'audio' // Pass type during construction
  ) {
    this.queue = new Queue<QueuedStep>();
    this.supabaseClient = supabaseClient; // Store the passed client
    this.sourcefileData = {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug
    };
    this.sourcefileType = sourcefile_type;
  }

  // Fetch the current status of the sourcefile
  private async fetchSourcefileStatus(): Promise<SourcefileStatus | null> {
    try {
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API,
          this.sourcefileData
        ),
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          cache: 'no-cache' // Ensure fresh status
        }
      );

      if (!response.ok) {
        console.error('Failed to fetch sourcefile status:', response.status);
        return null;
      }

      const data = await response.json();
      return data.status as SourcefileStatus;
    } catch (error) {
      console.error('Error fetching sourcefile status:', error);
      return null;
    }
  }

  // Determine the necessary steps based on the current status
  private async determineSteps(status: SourcefileStatus | null): Promise<QueuedStep[]> {
    const steps: QueuedStep[] = [];
    if (!status) {
      console.error("Cannot determine steps without sourcefile status.");
      return []; // Cannot proceed without status
    }

    console.log('Determining steps based on status:', status);

    // 1. Text Extraction (if needed)
    if ((this.sourcefileType === 'image' || this.sourcefileType === 'audio') && !status.has_text) {
      console.log('Adding text extraction step.');
      steps.push({
        type: 'text_extraction',
        apiEndpoint: getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API,
          this.sourcefileData
        ),
        params: {},
        description: 'Extracting text'
      });
      // If text extraction is needed, subsequent steps depend on its success,
      // so we determine them in the next iteration after status refresh.
      return steps;
    }

    // 2. Translation (if needed and text exists)
    if (status.has_text && !status.has_translation) {
      console.log('Adding translation step.');
      steps.push({
        type: 'translation',
        apiEndpoint: getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_TRANSLATE_API,
          this.sourcefileData
        ),
        params: {},
        description: 'Translating text'
      });
    }

    // 3. Wordforms & Phrases (if text exists)
    // These can be added regardless of translation status
    if (status.has_text) {
      console.log('Adding wordforms extraction step.');
      steps.push({
        type: 'wordforms',
        apiEndpoint: getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_PROCESS_WORDFORMS_API,
          this.sourcefileData
        ),
        params: {}, // Consider adding max_new_words if needed per iteration
        description: 'Extracting vocabulary'
      });

      console.log('Adding phrases extraction step.');
      steps.push({
        type: 'phrases',
        apiEndpoint: getApiUrl(
          RouteName.SOURCEFILE_PROCESSING_API_PROCESS_PHRASES_API,
          this.sourcefileData
        ),
        params: {}, // Consider adding max_new_phrases if needed per iteration
        description: 'Extracting phrases'
      });
    }

    // 4. Lemma Metadata Completion (if text exists and there are incomplete lemmas)
    if (status.has_text && status.incomplete_lemmas_count > 0) {
      console.log(`Adding ${status.incomplete_lemmas_count} lemma metadata completion steps.`);
      for (const lemmaInfo of status.incomplete_lemmas) {
        steps.push({
          type: 'lemma_metadata',
          apiEndpoint: getApiUrl(
            RouteName.LEMMA_API_COMPLETE_LEMMA_METADATA_API,
            {
              target_language_code: this.sourcefileData.target_language_code,
              lemma: lemmaInfo.lemma // Pass lemma identifier
            }
          ),
          params: {},
          description: `Completing metadata for "${lemmaInfo.lemma}"`,
          lemma: lemmaInfo.lemma // Store lemma for potential detailed logging/UI
        });
      }
    }

    return steps;
  }


  // Process a single step
  private async processSingleStep(step: QueuedStep): Promise<boolean> {
     console.log(`Processing step: ${step.type}`, { apiEndpoint: step.apiEndpoint, params: step.params });

     processingState.update(state => ({
      ...state,
      isProcessing: true,
      currentStep: step.type,
      description: step.description,
      error: null,
    }));

    try {
      console.log(`Sending ${step.type} request to ${step.apiEndpoint}`);
      
      // Use the stored supabaseClient instance
      const headers: HeadersInit = { 'Content-Type': 'application/json' };
      let accessToken: string | null = null;
      if (this.supabaseClient) {
          const { data: { session } } = await this.supabaseClient.auth.getSession();
          accessToken = session?.access_token ?? null;
      }
      
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
      }

      const response = await fetch(step.apiEndpoint, {
        method: 'POST', 
        headers: headers,
        body: JSON.stringify(step.params),
      });

      console.log(`${step.type} response status:`, response.status);

      if (!response.ok) {
        let errorData = { error: `HTTP error ${response.status}`};
        try {
          errorData = await response.json();
        } catch (e) { /* Ignore JSON parsing error */ }

        console.error(`Error in ${step.type} response:`, errorData);

        if (response.status === 401) {
           throw new Error(errorData.error || 'Unauthorized. Please log in again.');
        }

        // Handle duplicate key errors gracefully (as warnings)
        if (errorData.error &&
            (errorData.error.includes("duplicate key value") ||
             errorData.error.includes("violates unique constraint"))) {
          console.warn(`Duplicate entry detected during ${step.type} processing:`, errorData.error);
          // Treat as success to allow queue to continue for other steps
          processingState.update(state => ({ ...state, progress: state.progress + 1 }));
          return true;
        } else {
          throw new Error(errorData.error || `Failed to process ${step.type}`);
        }
      } else {
        const responseData = await response.json();
        console.log(`${step.type} response data:`, responseData);
        processingState.update(state => ({ ...state, progress: state.progress + 1 }));
        return true; // Step succeeded
      }
    } catch (error) {
      console.error(`Error processing ${step.type}:`, error);
      processingState.update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Unknown error',
        isProcessing: false, // Stop processing on error
      }));
      return false; // Step failed
    }
  }


  // Start processing for a given number of iterations
  public async processAll(iterations: number = 1): Promise<boolean> {
    processingState.update(state => ({
      ...state,
      isProcessing: true,
      progress: 0,
      totalSteps: 0, // Will be updated per iteration
      error: null,
      currentIteration: 0,
      totalIterations: iterations,
      processedSourcefileData: null
    }));

    let overallSuccess = true;

    for (let i = 0; i < iterations; i++) {
      const currentIteration = i + 1;
      console.log(`--- Starting Iteration ${currentIteration}/${iterations} ---`);

      processingState.update(state => ({ ...state, currentIteration }));

      // 1. Fetch current status for this iteration
      const currentStatus = await this.fetchSourcefileStatus();
      if (!currentStatus) {
        console.error(`Iteration ${currentIteration}: Failed to fetch status, aborting.`);
        processingState.update(state => ({
          ...state,
          error: "Failed to fetch sourcefile status",
          isProcessing: false
        }));
        overallSuccess = false;
        break; // Stop all iterations if status fails
      }

      // 2. Determine steps for *this* iteration based on *current* status
      const stepsForThisIteration = await this.determineSteps(currentStatus);
      if (stepsForThisIteration.length === 0) {
        console.log(`Iteration ${currentIteration}: No steps needed.`);
        continue; // Move to the next iteration if no steps are required
      }

      // Update total steps for the UI progress bar (relative to this iteration)
      processingState.update(state => ({
        ...state,
        totalSteps: stepsForThisIteration.length,
        progress: 0 // Reset progress for the new iteration
      }));

      // 3. Process steps for this iteration
      this.queue = new Queue<QueuedStep>(...stepsForThisIteration); // Load queue for this iteration

      while (this.queue.length > 0) {
        const step = this.queue.dequeue();
        const success = await this.processSingleStep(step);

        if (!success) {
          console.error(`Iteration ${currentIteration}: Step ${step.type} failed. Aborting further processing.`);
          overallSuccess = false;
          // State updated within processSingleStep
          break; // Stop processing this iteration
        }
      }

      if (!overallSuccess) {
        break; // Stop all iterations if one fails
      }

      console.log(`--- Finished Iteration ${currentIteration}/${iterations} ---`);
    } // End of iterations loop

    // Final state update
    console.log("Processing finished. Fetching final data...");
    try {
      const finalSourcefileData = await this.getFullSourcefileData(); // Fetch final state for UI update
      processingState.update(state => ({
        ...state,
        isProcessing: false, // Processing is complete (or stopped due to error)
        currentStep: null,
         // Ensure progress reflects completion if successful
        progress: overallSuccess ? state.totalSteps : state.progress,
        processedSourcefileData: finalSourcefileData,
        description: overallSuccess ? 'Processing complete!' : 'Processing failed.',
      }));
    } catch (error) {
      console.error('Error fetching final sourcefile data:', error);
      processingState.update(state => ({
        ...state,
        isProcessing: false,
        currentStep: null,
        error: state.error || "Failed to fetch final sourcefile data",
        processedSourcefileData: null,
        description: 'Processing finished with errors.',
      }));
      overallSuccess = false;
    }

    console.log(`Overall processing success: ${overallSuccess}`);
    return overallSuccess;
  }

  // Get the full sourcefile data including recognized words for updating the UI
  private async getFullSourcefileData(): Promise<any> {
    try {
      // Fetch the complete sourcefile text data to get updated recognized words
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API,
          this.sourcefileData
        ),
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          cache: 'no-cache' // Ensure fresh data
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get complete sourcefile data (status: ${response.status})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting full sourcefile data:', error);
      // Return a minimal error structure or null? Decide based on consuming component needs
      const errorMessage = error instanceof Error ? error.message : String(error);
      return { error: `Failed to load final data: ${errorMessage}` };
    }
  }
}