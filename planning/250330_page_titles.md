# Page Titles Analysis and Recommendations

This document analyzes current page titles across the Hello Zenno application and provides SEO-friendly alternatives that better reflect our open-source, approachable language learning tool for intermediate and advanced learners.

## Base Template

**Current Title:**
```
Hello Zenno - AI-assisted language learning
```

**Alternatives:**
- Hello Zenno - Interactive Language Learning for Intermediate Readers
- Hello Zenno - AI Dictionary & Contextual Language Learning
- Enhance Your Reading in Foreign Languages | Hello Zenno
- **RECOMMENDED:** Hello Zenno - Contextual Language Learning with AI Dictionary

## Languages Page

**Current Title:**
```
Hello Zenno - learn foreign words, with a magical AI dictionary
```

**Alternatives:**
- Language Selection | Hello Zenno Language Learning
- Explore Languages with AI-Generated Dictionaries | Hello Zenno
- Choose Your Language for Reading & Listening Practice | Hello Zenno
- **RECOMMENDED:** Hello Zenno - Choose a Language to Practice Reading & Listening

## Lemma Page

**Current Title:**
```
{{ lemma_metadata.lemma }} in {{ target_language_name }} (lemma) - Hello Zenno
```

**Alternatives:**
- {{ lemma_metadata.lemma }} | {{ target_language_name }} Dictionary & Examples
- Learn '{{ lemma_metadata.lemma }}' in {{ target_language_name }} | Hello Zenno
- {{ lemma_metadata.lemma }} - {{ target_language_name }} Word with Audio Examples
- **RECOMMENDED:** {{ lemma_metadata.lemma }} in {{ target_language_name }} - Context & Audio | Hello Zenno

## Wordform Page

**Current Title:**
```
{{ wordform_metadata.wordform }} in {{ target_language_name }} (wordform) - Hello Zenno
```

**Alternatives:**
- {{ wordform_metadata.wordform }} | {{ target_language_name }} Word Form & Usage
- {{ wordform_metadata.wordform }} - {{ target_language_name }} Grammar & Examples
- Learn to Use '{{ wordform_metadata.wordform }}' in {{ target_language_name }}
- **RECOMMENDED:** {{ wordform_metadata.wordform }} in {{ target_language_name }} - Usage & Examples | Hello Zenno

## Search Page

**Current Title:**
```
Search - {{ target_language_name }}
```

**Alternatives:**
- Search {{ target_language_name }} Words & Phrases | Hello Zenno
- {{ target_language_name }} Dictionary Search | Hello Zenno
- Find Words to Learn in {{ target_language_name }} | Hello Zenno
- **RECOMMENDED:** {{ target_language_name }} Word Search & Dictionary | Hello Zenno

## Sourcefile Text Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- Reading: {{ sourcefile }} in {{ target_language_name }} | Hello Zenno
- {{ sourcefile }} - Interactive {{ target_language_name }} Reading
- Practice {{ target_language_name }} with {{ sourcefile }} | Hello Zenno
- **RECOMMENDED:** {{ sourcefile }} - Interactive {{ target_language_name }} Reading | Hello Zenno

## Sourcefile Words Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- Vocabulary from {{ sourcefile }} | {{ target_language_name }} Learning
- {{ sourcefile }} - Key {{ target_language_name }} Words to Learn
- {{ target_language_name }} Vocabulary from {{ sourcefile }} | Hello Zenno
- **RECOMMENDED:** {{ sourcefile }} Vocabulary - Interactive {{ target_language_name }} Learning | Hello Zenno

## Phrases Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- {{ target_language_name }} Phrases & Expressions | Hello Zenno
- Common Phrases in {{ target_language_name }} | Hello Zenno
- Learn Useful {{ target_language_name }} Phrases | Hello Zenno
- **RECOMMENDED:** {{ target_language_name }} Phrases with Audio Examples | Hello Zenno

## Sentence Flashcards Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- {{ target_language_name }} Listening Practice | Hello Zenno
- Audio Flashcards for {{ target_language_name }} | Hello Zenno
- Practice {{ target_language_name }} Listening with Dictation | Hello Zenno
- **RECOMMENDED:** {{ target_language_name }} Listening Flashcards & Dictation | Hello Zenno

## Authentication Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- Sign In to Hello Zenno | Language Learning
- Hello Zenno Account - Access Your Language Learning
- Join Hello Zenno | AI-Enhanced Language Practice
- **RECOMMENDED:** Hello Zenno Login - Continue Your Language Learning Journey

## 404 Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- Page Not Found | Hello Zenno Language Learning
- 404 - Continue Exploring Languages on Hello Zenno
- Oops! Page Not Found | Hello Zenno
- **RECOMMENDED:** Page Not Found | Return to Language Learning | Hello Zenno

## Profile Page

**Current Title:**
```
Hello Zenno - AI-assisted language learning (default from base template)
```

**Alternatives:**
- Your Language Learning Profile | Hello Zenno
- Hello Zenno Profile - Track Your Language Progress
- Your Account & Learning Stats | Hello Zenno
- **RECOMMENDED:** Hello Zenno Profile - Your Language Learning Journey

## Implementation Notes

When implementing these title changes:

1. Ensure that dynamic values (like `{{ sourcefile }}`) are properly escaped for HTML
2. Keep titles under 60 characters when possible for optimal search display
3. Maintain the friendly, approachable tone while clearly conveying the purpose of each page
4. Include the Hello Zenno brand name consistently, typically at the end of the title
5. Focus on the value proposition for intermediate/advanced language learners
6. Emphasize key features like contextual learning, AI dictionary, and audio examples
