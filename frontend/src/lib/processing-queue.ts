import { Queue } from 'queue-typescript';
import { writable } from 'svelte/store';
import { getApiUrl } from './api';
import { RouteName } from './generated/routes';
import { supabase } from './supabaseClient';

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

  constructor(target_language_code: string, sourcedir_slug: string, sourcefile_slug: string) {
    this.queue = new Queue<QueuedStep>();
    this.sourcefileData = {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug
    };
  }

  // Add the necessary steps based on what's needed
  public async initializeQueue(sourcefile: any) {
    // Clear the existing queue
    this.queue = new Queue<QueuedStep>();
    let needsTextExtraction = false;

    console.log('Initializing queue for sourcefile:', {
      text_target: !!sourcefile.text_target,
      has_image: sourcefile.has_image,
      has_audio: sourcefile.has_audio,
      type: sourcefile.sourcefile_type
    });

    // Manual hardcoded fix for this specific image case - force text extraction
    if (sourcefile.sourcefile_type === 'image' || sourcefile.has_image || sourcefile.filename.endsWith('.jpg')) {
      needsTextExtraction = true;
      const endpoint = getApiUrl(
        RouteName.SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API,
        {
          target_language_code: this.sourcefileData.target_language_code,
          sourcedir_slug: this.sourcefileData.sourcedir_slug,
          sourcefile_slug: this.sourcefileData.sourcefile_slug
        }
      );
      
      console.log('Forcing text extraction step for image file:', endpoint);
      
      this.queue.enqueue({
        type: 'text_extraction',
        apiEndpoint: endpoint,
        params: {},
        description: 'Extracting text'
      });
    }
    // Normal detection logic (keeping as fallback)
    else if (!sourcefile.text_target && (sourcefile.has_image || sourcefile.has_audio)) {
      needsTextExtraction = true;
      const endpoint = getApiUrl(
        RouteName.SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API,
        {
          target_language_code: this.sourcefileData.target_language_code,
          sourcedir_slug: this.sourcefileData.sourcedir_slug,
          sourcefile_slug: this.sourcefileData.sourcefile_slug
        }
      );
      
      console.log('Adding text extraction step:', endpoint);
      
      this.queue.enqueue({
        type: 'text_extraction',
        apiEndpoint: endpoint,
        params: {},
        description: 'Extracting text'
      });
    }

    // Check if translation is needed, but only if we have text
    if (sourcefile.text_target && !sourcefile.text_english) {
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

    // Only add wordforms and phrases if we have text content and don't need text extraction
    // This prevents the race condition where we try to extract words before text is ready
    if (sourcefile.text_target && !needsTextExtraction) {
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
    }

    // Check for incomplete lemmas and add them to the queue, but only if we have text and wordforms
    if (sourcefile.text_target && !needsTextExtraction) {
      try {
        // Get the sourcefile status to check for incomplete lemmas
        const response = await fetch(
          getApiUrl(
            RouteName.SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API,
            {
              target_language_code: this.sourcefileData.target_language_code,
              sourcedir_slug: this.sourcefileData.sourcedir_slug,
              sourcefile_slug: this.sourcefileData.sourcefile_slug
            }
          ),
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            }
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          const incompleteLemmas = data.status?.incomplete_lemmas || [];
          
          // Add each incomplete lemma as a separate step
          for (const lemma of incompleteLemmas) {
            this.queue.enqueue({
              type: 'lemma_metadata',
              apiEndpoint: getApiUrl(
                RouteName.LEMMA_API_COMPLETE_LEMMA_METADATA_API,
                {
                  target_language_code: this.sourcefileData.target_language_code,
                  lemma: lemma.lemma
                }
              ),
              params: {},
              description: `Completing metadata for "${lemma.lemma}"`
            });
          }
        }
      } catch (error) {
        console.error('Error checking for incomplete lemmas:', error);
      }
    }

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
    
    console.log('Processing step:', {
      type: step.type,
      apiEndpoint: step.apiEndpoint,
      params: step.params
    });

    processingState.update(state => ({
      ...state,
      isProcessing: true,
      currentStep: step.type,
      description: step.description,
      error: null,
    }));

    try {
      console.log(`Sending ${step.type} request to ${step.apiEndpoint}`);
      
      // Get the current session/token
      const { data: { session } } = await supabase.auth.getSession();
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`;
      }
      
      // Log the headers being sent
      console.log('Sending request with headers:', JSON.stringify(headers));
      
      const response = await fetch(step.apiEndpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(step.params),
      });

      console.log(`${step.type} response status:`, response.status);
      
      if (!response.ok) {
        const data = await response.json();
        console.error(`Error in ${step.type} response:`, data);
        
        // Check for 401 specifically
        if (response.status === 401) {
           throw new Error(data.error || 'Unauthorized. Please log in again.');
        }
        
        // Handle other errors (like duplicate key)
        if (data.error && 
            (data.error.includes("duplicate key value") || 
             data.error.includes("violates unique constraint"))) {
          console.warn(`Duplicate entry detected during ${step.type} processing:`, data.error);
        } else {
          throw new Error(data.error || `Failed to process ${step.type}`);
        }
      } else {
        const data = await response.json();
        console.log(`${step.type} response data:`, data);
      }

      processingState.update(state => ({
        ...state,
        progress: state.totalSteps - this.queue.length,
      }));

      return true;
    } catch (error) {
      console.error(`Error processing ${step.type}:`, error);
      processingState.update(state => ({
        ...state,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
      return false;
    }
  }

  // Start processing the entire queue
  public async processAll(iterations: number = 1) {
    processingState.update(state => ({
      ...state,
      isProcessing: true,
      progress: 0,
      error: null,
      currentIteration: 1,
      totalIterations: iterations,
      processedSourcefileData: null
    }));

    let errorOccurred = false; // Flag to track if any step failed

    // Run the requested number of iterations
    for (let i = 0; i < iterations; i++) {
      // Update iteration counter in the state
      processingState.update(state => ({
        ...state,
        currentIteration: i + 1
      }));
      
      // Fetch full sourcefile data for this iteration
      let currentSourcefileData = await this.fetchCurrentSourcefileData(); 
      const hasInitialSteps = await this.initializeQueue(currentSourcefileData);
      
      if (!hasInitialSteps) {
        continue; // No steps to process for this iteration
      }
      
      // Process all steps in the queue
      while (this.queue.length > 0) {
        const currentStep = this.queue.front.type;
        const success = await this.processNextStep();
        
        if (!success) {
          errorOccurred = true; // Set flag on error
          break;
        }
        
        if (currentStep === 'text_extraction') {
          // Get fresh FULL sourcefile data after text extraction
          currentSourcefileData = await this.fetchCurrentSourcefileData(); 
          await this.initializeQueue(currentSourcefileData);
        }
      }
      
      // If we couldn't process the queue successfully, stop iterations
      if (errorOccurred) {
        break;
      }
    }

    // Get the final sourcefile data after all processing is complete
    try {
      const finalSourcefileData = await this.getFullSourcefileData();
      processingState.update(state => ({
        ...state,
        // Set isProcessing to false if an error occurred OR if the queue is empty
        isProcessing: !errorOccurred && this.queue.length > 0,
        processedSourcefileData: finalSourcefileData
      }));
    } catch (error) {
      console.error('Error fetching final sourcefile data:', error);
      processingState.update(state => ({
        ...state,
        // Set isProcessing to false if an error occurred OR if the queue is empty
        isProcessing: !errorOccurred && this.queue.length > 0,
        processedSourcefileData: null
      }));
    }

    return !errorOccurred && this.queue.length === 0;
  }
  
  // Helper method to get FULL current sourcefile data for subsequent iterations
  private async fetchCurrentSourcefileData(): Promise<any> {
    try {
      // Get the complete sourcefile data
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API, // Use inspect API for full data
          {
            target_language_code: this.sourcefileData.target_language_code,
            sourcedir_slug: this.sourcefileData.sourcedir_slug,
            sourcefile_slug: this.sourcefileData.sourcefile_slug
          }
        ),
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          // Bypass cache to ensure we get fresh data
          cache: 'no-cache' 
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to get current sourcefile data');
      }
      
      const data = await response.json();
      
      // Return the sourcefile object from the response
      return data.sourcefile; // Assuming the inspect API returns { sourcefile: {...} }
      
    } catch (error) {
      console.error('Error getting current sourcefile data:', error);
      throw error;
    }
  }
  
  // Get the full sourcefile data including recognized words for updating the UI
  private async getFullSourcefileData(): Promise<any> {
    try {
      // Fetch the complete sourcefile text data to get updated recognized words
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API,
          {
            target_language_code: this.sourcefileData.target_language_code,
            sourcedir_slug: this.sourcefileData.sourcedir_slug,
            sourcefile_slug: this.sourcefileData.sourcefile_slug
          }
        ),
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          // Bypass cache to ensure we get fresh data
          cache: 'no-cache'
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to get complete sourcefile data');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting full sourcefile data:', error);
      throw error;
    }
  }
}