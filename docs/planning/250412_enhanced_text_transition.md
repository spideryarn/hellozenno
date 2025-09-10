# Enhanced Text Transition: From HTML to Structured Data

## Goal, context

Fully transition the enhanced text system from the legacy HTML-generating approach to the newer structured data approach. This will improve separation of concerns (backend focuses on data, frontend on rendering) and provide a more maintainable and flexible system.

Currently, the codebase is in a transitional state:
- The backend has both implementations: `create_interactive_word_links()` (HTML generation, deprecated) and `create_interactive_word_data()` (structured data)
- Some backend routes return both formats simultaneously for compatibility
- `EnhancedText.svelte` component supports both approaches
- Some frontend components (e.g., `SourcefileText.svelte`) use the new approach, while others (e.g., `Sentence.svelte`) still use the legacy approach
- Documentation is outdated, describing only the legacy approach

## Principles, key decisions

- Complete the transition to the structured data approach across all components
- Remove legacy HTML generation from the backend once all frontend components are updated
- Update documentation to reflect the new architecture
- Maintain the same user experience during and after the transition
- Avoid breaking changes by performing the transition gradually

## Useful references

- `frontend/src/lib/components/EnhancedText.svelte` - The central component that can handle both approaches. HIGH
- `backend/utils/vocab_llm_utils.py` - Contains both the legacy and new backend functions. HIGH
- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte` - Example of a component using the new approach. MEDIUM
- `frontend/src/lib/components/Sentence.svelte` - Example of a component still using the legacy approach. MEDIUM
- `backend/utils/sourcefile_utils.py` - Shows how the backend is providing both formats. MEDIUM
- `frontend/docs/ENHANCED_TEXT.md` - Current documentation (outdated). HIGH

## Actions

- [ ] Audit all frontend components that use enhanced text
  - [ ] Search the codebase for components using `{@html enhanced_sentence_text}` or similar
  - [ ] Search for components importing or instantiating `EnhancedText`
  - [ ] Create a comprehensive list of components that need to be updated

- [ ] Update `Sentence.svelte` to use the new structured approach
  - [ ] Modify the component to use `EnhancedText` instead of `{@html enhanced_sentence_text}`
  - [ ] Update the backend route that serves sentence data to include the structured format
  - [ ] Test that the component works correctly with the updated approach
  - [ ] Ensure that tooltips and word links function properly

- [ ] Identify and update any other components still using the legacy approach
  - [ ] For each component identified in the audit, follow the same approach as with `Sentence.svelte`
  - [ ] Test each component after updates

- [ ] Update backend routes to prioritize structured data
  - [ ] Ensure all relevant API endpoints return the structured data format
  - [ ] Continue to include legacy HTML format temporarily for safety
  - [ ] Add deprecation warnings to legacy HTML format in API responses

- [ ] Test the entire application
  - [ ] Ensure all enhanced text functionality works correctly with the new approach
  - [ ] Verify tooltips, word links, and other interactive features function properly
  - [ ] Check for any missed components or edge cases

- [ ] Phase out the legacy HTML format
  - [ ] After confirming all frontend components are using the structured approach, remove HTML generation from backend responses
  - [ ] Update documentation to indicate the HTML format is no longer supported
  - [ ] Run thorough tests to ensure nothing breaks

- [ ] Update `ENHANCED_TEXT.md` documentation
  - [ ] Update document to reflect the new architecture
  - [ ] Explain the transition from HTML to structured data
  - [ ] Provide examples of the structured data format
  - [ ] Update code examples to show the current approach
  - [ ] Include guidance for developers implementing new features

- [ ] Clean up the codebase (no need to keep legacy code around)
  - [ ] Remove `create_interactive_word_links()`
  - [ ] Remove legacy code in `EnhancedText.svelte` that supports the HTML approach
  - [ ] Update comments throughout the codebase to reflect the new architecture


## Appendix

Sample structured data format:
```json
{
  "recognized_words": [
    {
      "word": "μπορείς",
      "start": 0,
      "end": 7,
      "lemma": "μπορώ",
      "translations": ["can", "be able to"],
      "part_of_speech": "verb",
      "inflection_type": "present tense, second person singular"
    },
    // More words...
  ]
}
```

vs. Legacy HTML format:
```html
<p>
 <a href="/language/el/wordform/μπορείς" class="word-link">Μπορείς</a> να <a href="/language/el/wordform/μεταφέρεις" class="word-link">μεταφέρεις</a> τις...
</p>
``` 