# Plan: Fix Word Highlighting Bugs

**Date:** 2026-01-03
**Status:** Draft

## Overview

Fix six bugs in the HelloZenno "Process this text" word highlighting functionality. These bugs affect:
- Data synchronization between backend response and frontend state
- Tooltip attachment for duplicate words
- Event listener cleanup on touch devices
- XSS vulnerability in structured text mode
- Redundant tooltip refresh operations
- Empty word list handling

## Context

**Affected Files:**
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`
- `frontend/src/lib/components/EnhancedText.svelte`

**Success Criteria:**
1. All recognized words display tooltips on hover/touch (including duplicates)
2. Backend response data correctly updates frontend state
3. No event listener leaks on touch devices
4. User-generated text properly escaped (no XSS)
5. No redundant tooltip initialization calls
6. Empty `recognized_words` array handled gracefully

## Stages

### Stage 1: Fix `text_target` Field Path Mismatch

**Goal:** Ensure backend response data correctly updates the `text_target` state variable

**Files:** `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`

**Problem Analysis:**
- Line 54-56: Handler checks `newData.text_target` but backend returns `newData.sourcefile.text_target`
- This prevents the text from updating after processing

**Steps:**
1. Update line 54-56 to check `newData.sourcefile?.text_target` instead of `newData.text_target`
2. Add fallback to also check `newData.text_target` for backward compatibility

**Code Change:**
```typescript
// Before (line 54-56):
if (newData.text_target) {
  text_target = newData.text_target;
  dataUpdated = true;
}

// After:
if (newData.sourcefile?.text_target || newData.text_target) {
  text_target = newData.sourcefile?.text_target ?? newData.text_target;
  dataUpdated = true;
}
```

**Verification:**
1. Navigate to a sourcefile with unprocessed text
2. Click "Process this text" 
3. Verify the text content updates with highlighted words
4. Check browser console for any errors
5. Run `cd frontend && npm run check` - no new type errors

---

### Stage 2: Fix Structured-Mode Tooltips for Duplicate Words

**Goal:** Ensure all occurrences of a word get tooltips, not just the first one

**Files:** `frontend/src/lib/components/EnhancedText.svelte`

**Problem Analysis:**
- Lines 290-305 in `initializeStructuredDataTooltips()`: Uses `Map<string, HTMLElement>` keyed by word text
- When the same word appears multiple times, only the last occurrence is stored in the map
- Result: Only one tooltip per unique word text

**Steps:**
1. Remove the intermediate Map lookup - it serves no purpose
2. Iterate directly over all `.word-link` elements
3. Attach tippy to each element individually

**Code Change:**
```typescript
// Before:
function initializeStructuredDataTooltips() {
  if (!container || !text || recognizedWords.length === 0) {
    console.log("Skipping structured data tooltip initialization: missing data");
    return;
  }
  
  // Get the container's text nodes and create a map to track spans we've inserted
  const wordSpans = new Map<string, HTMLElement>();
  
  // Find all the word spans we created
  const spans = container.querySelectorAll('.word-link');
  spans.forEach(span => {
    const wordElem = span as HTMLElement;
    const word = wordElem.textContent?.trim() || '';
    wordSpans.set(word, wordElem);
  });
  
  console.log(`Found ${spans.length} interactive words in structured data mode`);
  
  // Create Tippy instances for each word span
  for (const [word, element] of wordSpans.entries()) {
    const instance = attachTippy(element, word);
    tippyInstances.push(instance);
  }
}

// After:
function initializeStructuredDataTooltips() {
  if (!container || !text || recognizedWords.length === 0) {
    console.log("Skipping structured data tooltip initialization: missing data");
    return;
  }
  
  // Find all word link elements and attach tooltips to each one
  const spans = container.querySelectorAll('.word-link');
  console.log(`Found ${spans.length} interactive words in structured data mode`);
  
  // Create Tippy instances for each word span - attach to ALL occurrences
  spans.forEach(span => {
    const wordElem = span as HTMLElement;
    const word = wordElem.textContent?.trim() || '';
    if (word) {
      const instance = attachTippy(wordElem, word);
      tippyInstances.push(instance);
    }
  });
}
```

**Verification:**
1. Navigate to a sourcefile with repeated words (e.g., "the", "and")
2. Hover over the first occurrence - tooltip appears
3. Hover over a later occurrence of the same word - tooltip appears
4. Verify all highlighted words show tooltips
5. Run `cd frontend && npm run check` - no type errors

---

### Stage 3: Fix Touch-Device Click Handler Accumulation

**Goal:** Prevent click event listeners from accumulating on tooltip refresh

**Files:** `frontend/src/lib/components/EnhancedText.svelte`

**Problem Analysis:**
- Line 222+ in `attachTippy()`: Click listener added unconditionally for touch devices
- When `refreshTooltips()` is called, old tippy instances are destroyed but click listeners remain
- Results in multiple click handlers firing on each tap

**Steps:**
1. Use a data attribute to track whether the click handler has been attached
2. Check for this attribute before adding the listener
3. Set the attribute after adding the listener

**Code Change:**
```typescript
// Before (in attachTippy function, line 222+):
if (isTouchDevice()) {
  element.addEventListener('click', (e) => {
    // Only prevent default if modifier keys aren't pressed
    // This allows opening in new tab with Ctrl/Cmd+click
    if (!e.ctrlKey && !e.metaKey) {
      e.preventDefault();
    }
  });
}

// After:
if (isTouchDevice() && !element.hasAttribute('data-touch-handler')) {
  element.setAttribute('data-touch-handler', 'true');
  element.addEventListener('click', (e) => {
    // Only prevent default if modifier keys aren't pressed
    // This allows opening in new tab with Ctrl/Cmd+click
    if (!e.ctrlKey && !e.metaKey) {
      e.preventDefault();
    }
  });
}
```

**Verification:**
1. Test on a touch device or Chrome DevTools touch simulation
2. Process text to trigger tooltip refresh
3. Tap on highlighted words multiple times
4. Verify tooltip appears once (not multiple times)
5. Check console for any listener errors
6. Run `cd frontend && npm run check` - no type errors

---

### Stage 4: Fix XSS Vulnerability in Structured Mode

**Goal:** Escape HTML entities in user text before inserting `<br>` tags

**Files:** `frontend/src/lib/components/EnhancedText.svelte`

**Problem Analysis:**
- Lines 415-420 in `processLineBreaks()`: Returns text with `<br>` tags
- Line 432: `{@html segment.text}` renders this HTML
- If user text contains `<script>` or other HTML, it will be executed

**Steps:**
1. Create a helper function to escape HTML entities
2. Apply escaping before converting newlines to `<br>`
3. Ensure the helper handles all dangerous characters

**Code Change:**
```typescript
// Add new helper function:
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Before (processLineBreaks):
function processLineBreaks(text: string): string {
  // Simple conversion: keep all spaces, convert all newlines to <br>.
  // Double newlines naturally become <br><br>, avoiding paragraph wrappers
  // that could split around inline word links.
  return text.replace(/\n/g, '<br>');
}

// After:
function processLineBreaks(text: string): string {
  // First escape HTML entities, then convert newlines to <br>.
  // Double newlines naturally become <br><br>, avoiding paragraph wrappers
  // that could split around inline word links.
  return escapeHtml(text).replace(/\n/g, '<br>');
}
```

**Verification:**
1. Create a test sourcefile with text containing `<script>alert('XSS')</script>`
2. Process the text
3. Verify the script tag is displayed as text, not executed
4. Verify text like `<b>bold</b>` shows the literal tags
5. Verify newlines still convert to visible line breaks
6. Run `cd frontend && npm run check` - no type errors

---

### Stage 5: Remove Double Tooltip Refresh and Fix Reactive Triggers

**Goal:** Eliminate redundant tooltip initialization and ensure reactive refresh covers all input changes

**Files:** 
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`
- `frontend/src/lib/components/EnhancedText.svelte`

**Problem Analysis:**
- `SourcefileText.svelte` line 68-73: Manual `refreshTooltips()` call after data update
- `EnhancedText.svelte` line 325-330: Reactive statement triggers refresh when `recognizedWords` changes
- Both fire on the same data update, causing double initialization
- **Additionally:** The reactive statement only watches `recognizedWords`, not `text` or `html` changes

**Steps:**
1. Remove the manual `refreshTooltips()` call from `SourcefileText.svelte`
2. Update the reactive statement in `EnhancedText.svelte` to watch ALL rendering inputs (`html`, `text`, `recognizedWords`)
3. Add a guard to prevent double-initialization on mount (use `didMount` flag)
4. Keep `checkContentHeight()` call since it's independent

**Code Change (SourcefileText.svelte):**
```typescript
// Before (SourcefileText.svelte lines 64-73):
// If data was updated, manually refresh tooltips after a short delay
// to ensure the DOM has updated with the new content
if (dataUpdated && enhancedTextComponent) {
  setTimeout(() => {
    console.log('Manually refreshing tooltips after data update');
    enhancedTextComponent.refreshTooltips();
    // Check if we need to show bottom navigation after content update
    checkContentHeight();
  }, 200);
}

// After:
// Check if we need to show bottom navigation after content update
if (dataUpdated) {
  setTimeout(() => {
    checkContentHeight();
  }, 200);
}
```

**Code Change (EnhancedText.svelte):**
```typescript
// Add new variable at top of script:
let didMount = false;

// Before (reactive statement around line 325):
$: if (recognizedWords) {
  // Use setTimeout to ensure the DOM has been updated before refreshing tooltips
  if (typeof document !== 'undefined' && container) {
    setTimeout(() => refreshTooltips(), 0);
  }
}

// After:
$: if (didMount && container && (html || text || recognizedWords)) {
  // Use setTimeout to ensure the DOM has been updated before refreshing tooltips
  if (typeof document !== 'undefined') {
    setTimeout(() => refreshTooltips(), 0);
  }
}

// Update onMount to set didMount flag after initialization:
onMount(() => {
  if (import.meta.env.DEV) console.log(`EnhancedText component mounted with target_language_code: ${target_language_code}`);
  
  if (html) {
    initializeHTMLBasedTooltips();
  } else if (text && recognizedWords.length > 0) {
    initializeStructuredDataTooltips();
  }
  
  didMount = true; // Set AFTER initial initialization to prevent duplicate refresh
});
```

**Verification:**
1. Add temporary console.log to `refreshTooltips()` counting calls
2. Navigate to a sourcefile - verify tooltips initialize once on mount
3. Process text - verify `refreshTooltips()` is called once (not twice)
4. Verify tooltips still work correctly
5. Remove temporary console.log
6. Run `cd frontend && npm run check` - no type errors

---

### Stage 6: Handle Empty `recognized_words` Array

**Goal:** Properly reset UI when `recognized_words` becomes an empty array

**Files:** `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`

**Problem Analysis:**
- Line 46-49: Only updates `recognized_words` if `length > 0`
- If backend returns empty array (e.g., no recognized words), state keeps old data
- Results in stale highlighting from previous processing

**Steps:**
1. Change condition to check for existence, not length
2. Allow empty array to reset the state

**Code Change:**
```typescript
// Before (lines 46-49):
if (newData.recognized_words && newData.recognized_words.length > 0) {
  recognized_words = newData.recognized_words;
  console.log(`Updated recognized_words with ${recognized_words.length} items`);
  dataUpdated = true;
}

// After:
if (newData.recognized_words) {
  recognized_words = newData.recognized_words;
  console.log(`Updated recognized_words with ${recognized_words.length} items`);
  dataUpdated = true;
}
```

**Verification:**
1. Process text that has recognized words - verify highlighting works
2. Simulate backend returning empty array (if possible) - verify old highlights are cleared
3. Verify no errors when `recognized_words` is empty
4. Run `cd frontend && npm run check` - no type errors

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing HTML mode tooltips | High | Stage 2 only modifies structured mode function |
| XSS fix breaks legitimate formatting | Medium | Test with various text inputs including special chars |
| Removing manual refresh breaks edge cases | Medium | Test thoroughly after Stage 5, reactive handles it |
| Touch handler detection fails on some devices | Low | Existing isTouchDevice() already handles edge cases |

## Out of Scope

**Tooltip HTML Content XSS:** The tooltips use `allowHTML: true` with interpolated fields (lemma, translation, etymology). These fields come from backend data, not user input, and are assumed to be sanitized. If user-controlled content can reach these fields, a separate sanitization task should be created.

## Dependencies

- Stages 1-4 are independent and can be done in any order
- Stage 5 depends on Stage 2 (ensures tooltips work before removing redundancy)
- Stage 6 is independent

## Implementation Notes

### Stage 1 Notes
- Decisions made: Implemented fallback pattern as specified - check `newData.sourcefile?.text_target` first, then `newData.text_target`
- Learnings: None - straightforward change
- Deviations from plan: None

### Stage 2 Notes
- Decisions made: Removed the Map entirely and iterated directly over all `.word-link` elements, attaching tippy to each one individually
- Learnings: The original Map-based approach was fundamentally flawed for handling duplicates since Maps use unique keys
- Deviations from plan: None

### Stage 3 Notes
- Decisions made: Used `data-touch-handler` attribute as a guard to prevent duplicate listener attachment
- Learnings: None - straightforward change
- Deviations from plan: None

### Stage 4 Notes
- Decisions made: Added `escapeHtml()` function that escapes all standard HTML entities (&, <, >, ", ')
- Learnings: None - standard XSS mitigation pattern
- Deviations from plan: None

### Stage 5 Notes
- Decisions made: Added `didMount` flag set to `true` AFTER initial tooltip initialization in `onMount()` to prevent reactive statement from triggering double initialization
- Learnings: The reactive statement now watches all three inputs (html, text, recognizedWords) instead of just recognizedWords
- Deviations from plan: None - followed plan exactly

### Stage 6 Notes
- Decisions made: Simply removed the `.length > 0` check, allowing empty arrays to update state
- Learnings: None - straightforward change
- Deviations from plan: None

**Implementation completed: 2026-01-03**
- All 6 stages implemented successfully
- Type checking passes for modified files (pre-existing errors in other files are unrelated)
