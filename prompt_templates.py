# no inputs needed because the image is provided as a file
extract_text_from_image = """
Extract the text in {{ target_language_name }} from the image(s) exactly as it appears.

Only output the {{ target_language_name }} text, nothing else. Use "\n\n" to separate paragraphs.

Ignore page numbers, headers, footers, etc.

If you see a word spanning the end of one line to the beginning of another with a hyphen, just join it together as a single word.

If the text spans multiple pages in the image, return the text from all pages.

If there is no text in the image, return "-".
"""

translate_to_english = """
Translate the following {{ target_language_name }} text to English. Only output the English text, nothing else.

Provide a complete, unsummarised, and faithful translation that will be helpful for someone learning {{ target_language_name }} to understand it.

If there is no text, return "-".

<text>
{{ txt_tgt }}
</text>
"""

translate_from_english = """
Translate the following English text to {{ target_language_name }}. Only output the translated text, nothing else.

Provide a complete, unsummarised, and faithful translation that will be helpful for someone learning English to understand it.

If there is no text, return "-".

<text>
{{ txt_en }}
</text>
"""

extract_tricky_wordforms = """
I'm learning {{ target_language_name }}{% if language_level %}, at about {{ language_level }} student level{% endif %}. Please identify {% if max_new_words %}{{ max_new_words }}{% else %}a comprehensive list of{% endif %} difficult/uncommon wordforms (i.e. single words rather than multi-word phrases) from this text that will help me to understand it.

IMPORTANT: Never include slashes (/) in any lemmas or wordforms as they cause URL routing issues.

Return as JSON in the following schema:

<json_schema>
{
    "wordforms": [
        {
            "wordform": str,  # the form without punctuation as it appears in the text, e.g. "Ακολούθησε," in the text -> "ακολούθησε" as the wordform (i.e. lower-case, no punctuation), unless it's a proper noun or should be capitalised
            "lemma": str,  # the canonical form (e.g. for wordform "ακολούθησε", the lemma would be "ακολουθώ")
            "translations": list[str],  # list of English translations
            "part_of_speech": str,  # e.g. "verb", "noun", "adjective", etc.
            "inflection_type": str,  # e.g. "first-person singular present", "feminine plural genitive"
            "centrality": float,  # from 0-1, how central/important/frequent this wordform is to the meaning of the text
        },
    ]
}
</json_schema>
{% if ignore_words %}
Be thorough and try to find words that might have been missed in previous analysis. Consider:
- Less common words that might still be important
- Words with tricky grammar patterns
- Words that look simple but have special usage
- Cultural or contextual significance
- Words that are part of important collocations

Ignore these wordforms:
{% for ignore_word in ignore_words %}
- {{ ignore_word }}
{% endfor %}
{% endif %}

Only output the valid JSON, with no other commentary.

----

<text>
{{ txt_tgt }}
</text>
"""

metadata_for_lemma = """
We're building a rich, machine-readable dictionary of {{ target_language_name }} for English learners. Provide only the JSON output with no commentary and no other text. The JSON schema should be as follows.

IMPORTANT: Never include slashes (/) in any lemmas or wordforms as they cause URL routing issues.

{{ target_language_name }} lemma:
<lemma>
{{ lemma }}
</lemma>

<json_schema>
{
    "lemma": str,  # the dictionary form (i.e. canonical, headform) of the word
    "part_of_speech": str,  # e.g. "verb", "adjective", "noun", "idiom", "phrase", "pronoun", "preposition", "adverb", "conjunction", etc...
    "translations": list[str],  # one or more English translations, e.g. ["to pay", "to settle", "to fulfill"]
    "etymology": str,  # Detailed origins of the word, paying especial attention to English cognates and examples. If the word is a loanword, explain the etymology. Don't include transliteration. Pay close attention to what's less obvious/more specific to this particular word that will help learn/remember/understand this particular word relative to other similar words. Try and make it rich, interesting, and memorable.
    "synonyms": [
        {
            "lemma": str,  # e.g. "εξοφλώ"
            "translation": str,  # to English
        }
    ],
    "antonyms": [
        {
            "lemma": str,  # e.g. "λαμβάνω"
            "translation": str,  # to English
        }
    ],
    "related_words_phrases_idioms": [
        {
            "lemma": str,  # e.g. ["πληρώνομαι", "πληρωμή", ...]
            "translation": str,  # to English
        },
    ],
    "example_wordforms": list[str],  # inflected forms of this lemma that a learner might encounter, e.g. ["πληρώνει", "πλήρωσα", "πληρώνοντας", "πληρωμένος", ...]
    "register": str,  # e.g. "neutral", "formal", "informal", "vulgar", "archaic", "medical", etc
    "commonality": float,  # from 0-1, how common in regular use this lemma is
    "guessability": float,  # from 0-1, how easy this lemma is to guess for an English speaker
    "cultural_context": str,  # notes about usage in target language cultural context
    "mnemonics": list[str],  # memory aids for sound/spelling/meaning
    "example_usage": [
        {
            "phrase": str,  # e.g. "Πληρώνω το λογαριασμό."
            "translation": str,  # e.g. "I pay the bill."
        }
    ],
    "easily_confused_with": [
        {
            "lemma": str,  # another lemma that might be confused with this one
            "explanation": str,  # how they are distinct
            "example_usage_this_target": str,  # example using this lemma, in {{ target_language_name }}
            "example_usage_this_source": str,  # example using this lemma, in English
            "example_usage_other_target": str,  # example using the other lemma, in {{ target_language_name }}
            "example_usage_other_source": str,  # example using the other lemma, in English
            "mnemonic": str,  # memory aid for distinguishing
            "notes": str,  # any other useful notes
        }
    ]
}
</json_schema>
"""

quick_search_for_wordform = """
This is a quick search for a wordform typed directly by the user, as the first stage of a dictionary lookup.

The input is probably a {{ target_language_name }} word, but it might be a word in English, or it might be invalid.

We will respond with a JSON data structure (see below) that contains zero/one/more {{ target_language_name }} results and zero/one/more English results. The ideal case is when we return exactly one result across both languages, because then we can redirect to that page, otherwise we'll have to show a results page for the user to select from.

Note: even if the input is an English word, the wordform(s) that we return will be in {{ target_language_name }},i.e. translation(s) of the English word.

Your task is to analyze the input and return appropriate metadata based on these cases:

1. If the input is a {{ target_language_name }} lemma (dictionary form):
   - Return all fields with appropriate values
   - Set inflection_type to describe the lemma form (e.g. "first-person singular present" for verbs)
   - Set possible_misspellings to None
   - For modern languages, use modern forms only (e.g. "έπειτα" not "ἔπειτα")
   - Missing accents are ok (e.g. "επειτα" -> "έπειτα")
   - Case variations are ok (e.g. "ΕΠΕΙΤΑ" -> "έπειτα")

2. If the input is a valid {{ target_language_name }} wordform but not a lemma:
   - Return all fields with appropriate values
   - Set lemma to the dictionary form this wordform belongs to
   - Set inflection_type to describe this specific form
   - Set possible_misspellings to None
   - For modern languages, use modern forms only
   - Missing accents are ok (e.g. "ανθρωπος" -> "άνθρωπος")
   - Case variations are ok (e.g. "ΚΑΛΟΣ" -> "καλός")
   - The translations should reflect the INFLECTED form, not the lemma, e.g. "προσγειώθηκαν" -> "they landed" rather than just "land"
   - For ambiguous cases, always prefer the interpretation that has a different lemma. For example:
     * "μόνο" -> lemma="μόνος" (adjective) not lemma="μόνο" (adverb)
     * "καλά" -> lemma="καλός" (adjective) not lemma="καλά" (adverb)
     * "πολύ" -> lemma="πολύς" (adjective) not lemma="πολύ" (adverb)

3. If the input is an English word:
   - Return results in the `english_results` section, not target_language_results
   - Return all fields with appropriate values
   - Set inflection_type to describe the {{ target_language_name }} word form
   - Set possible_misspellings to None

4. If the input looks like a typo or misspelling:
   - Set all fields to None except possible_misspellings
   - For modern languages, set possible_misspellings to a list of closest correct modern forms, ordered by similarity
   - When deciding between typo vs valid word:
     * Missing accents are NOT typos (e.g. "επειτα" is valid, just needs accent)
     * Case variations are NOT typos (e.g. "ΚΑΛΟΣ" is valid, just needs case normalization)
     * These ARE typos:
       - Double letters that should be single (e.g. "καλλός" -> "καλός")
       - Missing letters (e.g. "έπιτα" -> "έπειτα")
       - Similar-looking letters (e.g. "μηλώ" -> "μιλώ")
       - Extra accents (e.g. "καί" -> "και")
       - Mixed Greek/Latin letters (e.g. "καλoς" -> "καλός")
       - Extra letters (e.g. "καλόςς" -> "καλός")
       - Wrong letter order (e.g. "καλσς" -> "καλός")
       - Double initial consonants (e.g. "κκαι" -> "και")

5. If the input is definitely invalid (wrong language, nonsense, etc.):
   - Set all fields to None

Notes:
- For any input, first sanitize by removing extra whitespace, punctuation, down-casing appropriately, etc.
- The sanitized form should be returned in the wordform field
- For lemmas and valid wordforms, possible_misspellings should be None
- Raise an error if the input is empty or invalid
- For modern languages, only use modern forms, not ancient/archaic forms
- IMPORTANT: Never include slashes (/) in lemmas or wordforms as they cause URL routing issues
- Format the JSON response carefully to ensure it is valid
- Make sure all strings in lists are properly quoted
- Do not include any trailing commas in lists or objects

Example valid JSON responses using Greek (modern) as the target language:

1. For a {{ target_language_name }} lemma (with missing accent) "επειτα":
<json_example>
{
    "target_language_results": {
        "matches": [
            {
                "target_language_wordform": "έπειτα",
                "target_language_lemma": "έπειτα",
                "part_of_speech": "adverb",
                "english": ["then", "afterwards", "later"],
                "inflection_type": "adverb",
            }
        ],
        "possible_misspellings": null
    },
    "english_results": {
        "matches": [],
        "possible_misspellings": null
    }
}
</json_example>

2. For a {{ target_language_name }} inflected noun wordform "άνθρωποι":
<json_example>
{
    "target_language_results": {
        "matches": [
            {
                "target_language_wordform": "άνθρωποι",
                "target_language_lemma": "άνθρωπος",
                "part_of_speech": "noun",
                "english": ["people", "mankind", "humankind", "humanity"],
                "inflection_type": "masculine plural nominative",
            },
        ],
        "possible_misspellings": null
    },
    "english_results": {
        "matches": [],
        "possible_misspellings": null
    }
}
</json_example>

2b. For a {{ target_language_name }} inflected verb form (with missing accent) "προσγειωθηκαν":
<json_example>
{
    "target_language_results": {
        "matches": [
            {
                "target_language_wordform": "προσγειώθηκαν",
                "target_language_lemma": "προσγειώνομαι",
                "part_of_speech": "verb",
                "english": ["they landed", "they touched down"],
                "inflection_type": "third-person plural passive aorist",
            },
        ],
        "possible_misspellings": null
    },
    "english_results": {
        "matches": [],
        "possible_misspellings": null
    }
}
</json_example>

3. For an English word (e.g. "examples"):
<json_example>
{
    "target_language_results": {
        "matches": [],
        "possible_misspellings": null
    },
    "english_results": {
        "matches": [
            {
                "target_language_wordform": "παραδείγματα",
                "target_language_lemma": "παράδειγμα",
                "part_of_speech": "noun",
                "english": ["example", "illustration", "instance"],
                "inflection_type": "neuter plural nominative"
            }
        ],
        "possible_misspellings": null
    }
}
</json_example>

4. For a {{ target_language_name }} typo "μηλώ":
<json_example>
{
    "target_language_results": {
        "matches": [],
        "possible_misspellings": ["μιλώ"]
    },
    "english_results": {
        "matches": [],
        "possible_misspellings": ["μιλώ"]
    }
}
</json_example>

5. For an invalid word, e.g. "asdf" or "bonjour":
<json_example>
{
    "target_language_results": {
        "matches": [],
        "possible_misspellings": null
    },
    "english_results": {
        "matches": [],
        "possible_misspellings": null
    }
}
</json_example>

Provide only the JSON output with no commentary:

<json_schema>
{
    "target_language_results": {
        "matches": [
            {
                "target_language_wordform": "...", # the sanitized form if valid
                "target_language_lemma": "...", # the dictionary form this belongs to
                "part_of_speech": "...", # e.g. "verb", "adjective", "noun", etc.
                "english": ["..."], # English translations
                "inflection_type": "..." # e.g. "first-person singular present", "feminine plural genitive"
            }
        ],
        "possible_misspellings": ["..."] or null # ordered list of suggested corrections, or None if valid
    },
    "english_results": {
        "matches": [
            {
                "target_language_wordform": "...",
                "target_language_lemma": "...",
                "part_of_speech": "...",
                "english": ["..."], # English input word
                "inflection_type": "..."
            }
        ],
        "possible_misspellings": ["..."] or null
    }
}
</json_schema>

----

{{ target_language_name }} input:
<wordform>
{{ wordform }}
</wordform>
"""

extract_phrases_from_text = """
You are a {{ target_language_name }} language expert. For the following text, identify and analyze {% if max_new_phrases %}{{ max_new_phrases }}{% else %}a comprehensive list of{% endif %} tricky, idiomatic phrases and expressions that are likely to be difficult for a {% if language_level %}{{ language_level }} student level{% endif %} learner of {{ target_language_name }} to understand.

Only include *multiple*-word expressions that are idiomatic, common, and where the meaning isn't at all obvious from the individual words. In other words, don't include single words, simple word combinations, or literal phrases.

<text>
{{ txt_tgt }}
</text>

Return a JSON object with this structure:
<json_schema>
{
    "phrases": [
        {
            "canonical_form": str,  # standard/abstracted form using lemmas or variables like (X, Y)
            "raw_forms": list[str],  # forms found in text and other common variations
            "translations": list[str],  # one or more English translations
            "literal_translation": str,  # word-for-word translation showing grammatical structure
            "part_of_speech": str,  # "verbal phrase", "prepositional phrase", "idiom", etc.
            "register": str,  # "neutral", "formal", "informal", "vulgar", "archaic", etc.
            "commonality": float,  # from 0-1, how frequently used this phrase is
            "guessability": float,  # from 0-1, how intuitive the meaning is for English speakers
            "etymology": str,  # origins and development of the phrase
            "cultural_context": str,  # cultural background and usage notes
            "mnemonics": list[str],  # one or more memory aids for remembering the phrase, based on sound/spelling/meaning/etymology
            "example_usage": [
                {
                    "phrase": str,  # example in target language
                    "translation": str,  # translation to English
                    "context": str,  # optional situational context
                }
            ],
            "related_phrases": [
                {
                    "canonical_form": str,  # related phrase
                    "translation": str,  # its translation
                    "relationship": str,  # e.g. "similar meaning", "opposite", "variation"
                }
            ],
            "component_words": [
                {
                    "lemma": str,  # dictionary form of each key word
                    "translation": str,  # individual word translation
                    "notes": str  # usage notes specific to this context
                }
            ],
            "usage_notes": str,  # grammatical patterns, restrictions, or special cases
            "difficulty_level": str,  # "beginner", "intermediate", "advanced"
        }
    ]
}
</json_schema>
Return only the JSON output, with no commentary or other text.
"""


generate_sentence_flashcards = """
Generate simple, idiomatic sentences {{ target_language_name }} that use at least one (and ideally more) of the following lemma words. You can slightly inflect the lemma words (e.g. modify them slightly to agree in number, gender, tense, etc.) but not change the part of speech or meaning.

Respond with pure JSON, with no commentary or other text, in the following schema:

<json_schema>
{
    "sentences": [
        {
            "sentence": str,  # the sentence
            "translation": str,  # the translation to English
            "lemma_words": list[str],  # the lemma words from the list below used in this sentence
        }
    ]
}
</json_schema>

<words>
{{ already_words }}
</words>
"""
