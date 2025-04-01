import type { FlashcardState, FlashcardStage } from './types';

/**
 * Pure function to advance to the next stage of a flashcard
 * @param state Current flashcard state
 * @returns New flashcard state with advanced stage
 */
export function advanceStage(state: FlashcardState): FlashcardState {
  // Can't advance beyond stage 3
  if (state.stage >= 3) {
    return state;
  }
  
  const nextStage = (state.stage + 1) as FlashcardStage;
  
  return {
    ...state,
    stage: nextStage
  };
}

/**
 * Pure function to go back to the previous stage of a flashcard
 * @param state Current flashcard state
 * @returns New flashcard state with previous stage
 */
export function previousStage(state: FlashcardState): FlashcardState {
  // Can't go back before stage 1
  if (state.stage <= 1) {
    return state;
  }
  
  const prevStage = (state.stage - 1) as FlashcardStage;
  
  return {
    ...state,
    stage: prevStage
  };
}

/**
 * Reset to stage 1 (initial state)
 * @param state Current flashcard state
 * @returns New flashcard state reset to stage 1
 */
export function resetStage(state: FlashcardState): FlashcardState {
  return {
    ...state,
    stage: 1
  };
}

/**
 * Get the labels for navigation buttons based on the current stage
 * @param stage Current flashcard stage
 * @returns Object with left and right button labels
 */
export function getButtonLabels(stage: FlashcardStage): { left: string, right: string, leftDisabled: boolean, rightDisabled: boolean } {
  switch (stage) {
    case 1:
      return { 
        left: 'Play Audio',
        right: 'Show Sentence',
        leftDisabled: false,
        rightDisabled: false
      };
    case 2:
      return { 
        left: 'Play Audio',
        right: 'Show Translation', 
        leftDisabled: false,
        rightDisabled: false
      };
    case 3:
      return { 
        left: 'Show Sentence',
        right: 'Show Translation',
        leftDisabled: false,
        rightDisabled: true
      };
    default:
      return { 
        left: 'Play Audio',
        right: 'Next',
        leftDisabled: false,
        rightDisabled: false
      };
  }
}