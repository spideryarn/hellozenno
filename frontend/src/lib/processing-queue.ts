import PQueue from 'p-queue';
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
  private queue: PQueue;
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
    // Default concurrency 1 to preserve step ordering; can be tuned later
    this.queue = new PQueue({ concurrency: 1 });
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

    // Determine if text extraction is needed
    const needsTextExtraction = (this.sourcefileType === 'image' || this.sourcefileType === 'audio') && !status.has_text;

    // 1. Add text extraction step if needed
    if (needsTextExtraction) {
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
    }

    // Determine if text will be available (either already exists or will be extracted)
    const willHaveText = status.has_text || needsTextExtraction;

    // 2. Translation (if needed and text exists or will exist)
    if (willHaveText && !status.has_translation) {
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

    // 3. Wordforms & Phrases (if text exists or will exist)
    if (willHaveText) {
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

    // 4. Lemma Metadata Completion (if text exists or will exist and there are incomplete lemmas)
    if (willHaveText && status.incomplete_lemmas_count > 0) {
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
        try {
          const { data } = await this.supabaseClient.auth.getSession();
          accessToken = data?.session?.access_token ?? null;
          console.log('Got access token:', accessToken ? 'Yes (token available)' : 'No (null token)');
        } catch (error) {
          console.error('Error getting Supabase session:', error);
        }
      } else {
        console.warn('No Supabase client available for authentication');
      }
      
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
        console.log('Added Authorization header with Bearer token');
      } else {
        console.warn('No access token available, request will be unauthenticated');
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
          console.error('Unauthorized error response:', errorData);
          const loginUrl = `/auth?next=${encodeURIComponent(window.location.pathname)}`;
          const errorMsg = 'Unauthorized. You may need to log in again.';
          
          // Provide a clearer error message with a login link
          throw new Error(`${errorMsg} Please <a href="${loginUrl}">log in</a> to process this file.`);
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

    // 1. Fetch current status to determine required steps
    const currentStatus = await this.fetchSourcefileStatus();
    if (!currentStatus) {
      console.error(`Failed to fetch status, aborting.`);
      processingState.update(state => ({
        ...state,
        error: "Failed to fetch sourcefile status",
        isProcessing: false
      }));
      return false;
    }

    // 2. Determine all steps needed based on current status
    const allSteps = await this.determineSteps(currentStatus);
    if (allSteps.length === 0) {
      console.log(`No processing steps needed.`);
      processingState.update(state => ({
        ...state,
        isProcessing: false,
        description: 'No processing needed'
      }));
      return true;
    }

    // 3. Separate normal steps from lemma metadata steps to prioritize wordforms extraction
    const normalSteps: QueuedStep[] = [];
    const lemmaMetadataSteps: QueuedStep[] = [];

    // Separate lemma metadata from other steps
    allSteps.forEach(step => {
      if (step.type === 'lemma_metadata') {
        lemmaMetadataSteps.push(step);
      } else {
        normalSteps.push(step);
      }
    });

    // Calculate total steps for progress bar
    const totalStepsCount = (normalSteps.length * iterations) + lemmaMetadataSteps.length;
    console.log(`Processing ${normalSteps.length} normal steps × ${iterations} iterations + ${lemmaMetadataSteps.length} lemma metadata steps`);

    processingState.update(state => ({
      ...state,
      totalSteps: totalStepsCount,
      progress: 0 // Reset progress counter
    }));

    // Build queue with desired order and preserve sequential execution.
    // Recreate queue instance to ensure empty state for this run.
    this.queue = new PQueue({ concurrency: 1 });

    // Track iteration UI state; must be declared before scheduling tasks
    let currentStepIndex = 1;
    let currentIterationTracking = 1;
    const stepsInCurrentIteration = normalSteps.length;
    let aborted = false;

    // 4. Process normal steps for each iteration
    for (let i = 0; i < iterations; i++) {
      const currentIteration = i + 1;
      console.log(`--- Queueing normal steps for iteration ${currentIteration}/${iterations} ---`);
      
      // Add all normal steps to the queue as scheduled tasks
      for (const step of normalSteps) {
        const stepCopy = { ...step } as QueuedStep;
        this.queue.add(async () => {
          if (aborted) {
            return;
          }
          // Update iteration counter for the UI prior to running the task
          if (stepCopy.type !== 'lemma_metadata') {
            if (currentStepIndex > stepsInCurrentIteration) {
              currentIterationTracking++;
              currentStepIndex = 1;
            } else {
              currentStepIndex++;
            }
            processingState.update(state => ({ 
              ...state, 
              currentIteration: currentIterationTracking 
            }));
          }
          const success = await this.processSingleStep(stepCopy);
          if (!success) {
            overallSuccess = false;
            aborted = true;
            return;
          }
          return;
        });
      }
    }

    // 5. Add all lemma metadata steps to the end of the queue (only once)
    console.log(`--- Queueing ${lemmaMetadataSteps.length} lemma metadata steps ---`);
    for (const step of lemmaMetadataSteps) {
      const stepCopy = { ...step } as QueuedStep;
      this.queue.add(async () => {
        if (aborted) {
          return;
        }
        // For lemma metadata, we're in a special "finishing" phase
        processingState.update(state => ({ 
          ...state, 
          currentIteration: iterations,
          description: stepCopy.description 
        }));
        const success = await this.processSingleStep(stepCopy);
        if (!success) {
          overallSuccess = false;
          aborted = true;
          return;
        }
      });
    }

    // 6. Process all steps in the queue

    await this.queue.onIdle();

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