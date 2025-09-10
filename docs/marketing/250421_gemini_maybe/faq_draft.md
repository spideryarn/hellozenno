# Frequently Asked Questions (Draft)

## Getting Started

**Q: Who is Hello Zenno for?**
A: Hello Zenno is primarily designed for intermediate to advanced language learners (roughly A2 level and above) who want to expand their vocabulary and improve listening comprehension by working with authentic texts. It's great if you can already read a bit but struggle with unknown words or understanding spoken language.

**Q: Do I need an account?**
A: Yes, to use the core features like uploading texts and generating AI content, you'll need to sign up for a free account. This helps manage resources and prevent misuse.

**Q: How do I start learning?**
A: The best way is to choose the language you're learning, then either explore existing sample texts (if available) or add your own content. You can paste text, provide a URL to an article, or upload images of text (like book pages). Once processed, you can read the text with interactive highlights or practice the audio flashcards generated from it. Alternatively, just try searching for a word!

**Q: Is it free?**
A: Creating an account and using the basic features is currently free. The AI generation (dictionary entries, audio) incurs costs, so while free for now, we might explore community funding models like "centaur sourcing" in the future to keep it sustainable and accessible.

## Features & Functionality

**Q: What makes the dictionary special?**
A: Instead of static definitions, Hello Zenno uses AI (currently Claude Sonnet 3.5) to generate rich dictionary entries *dynamically* as you encounter words. These include etymology (word origins, often a great memory aid!), example sentences showing context, comparisons with similar words, and difficulty indicators.

**Q: How does the listening practice work?**
A: We call it dynamic contextual dictation or "audio flashcards." When you practice for a text you've added, the system generates audio snippets (using Eleven Labs AI voices) of example sentences using the challenging words from *that text*. You listen, try to understand, and can then reveal the transcription and translation. It's focused practice directly related to what you're reading.

**Q: How does Hello Zenno know which words are difficult?**
A: It uses an AI model to assess words based on factors like general frequency, frequency within the specific text, and estimated ease of guessing the meaning from context. You can often ask it to find more tricky words if the initial pass isn't enough.

**Q: What languages are supported?**
A: We currently offer around 30 languages where modern AI performs reasonably well. The core requirement is English as the base language (you're learning *from* English). Support for other languages depends on the AI's capabilities.

**Q: Can I use it on my phone?**
A: Hello Zenno is currently a web application, best used on a desktop or laptop. There are no immediate plans for a dedicated mobile app, though the website might work reasonably well on mobile browsers for some tasks.

**Q: Does it work offline?**
A: No, offline functionality isn't supported. Key features rely on real-time AI generation and database access.

## AI & Reliability

**Q: Is the AI-generated content always correct?**
A: While we use cutting-edge AI models (like Claude Sonnet 3.5) that perform very well, especially in languages like Greek where we've done checks, AI is not infallible. There's always a small risk of errors in definitions, translations, or generated sentences. We encourage users to report any issues they find (via GitHub Issues) so we can improve.

**Q: How do you handle different writing systems?**
A: In theory, the AI should handle various scripts. However, we haven't extensively tested this with non-alphabetic languages. There might be edge cases or specific challenges (e.g., multiple words spelled identically but with different meanings) that need further development.

## Content & Privacy

**Q: Can I upload copyrighted material?**
A: We strongly encourage users to only upload public domain texts or materials they have the rights to use. Currently, all uploaded content and generated dictionary entries are publicly visible. We are considering adding options for private sources in the future, but the default is open access.

**Q: What happens to the content I upload?**
A: Text you upload is processed to extract vocabulary, generate translations, and create dictionary entries/sentences. This generated data becomes part of the shared resource for the language, visible to all users. The original source file (text or image) is stored associated with your account.

## Future & Community

**Q: What is "centaur sourcing"?**
A: It's our term for human-AI collaboration, like crowdsourcing but leveraging AI. The idea is that the community could collectively guide and fund the AI generation of rich language resources (like dictionaries and sentence banks) that benefit everyone. This might involve users pooling API keys or contributing corrections.

**Q: How can I give feedback or report bugs?**
A: The best way is to open an issue on our GitHub repository: [https://github.com/spideryarn/hellozenno/issues](https://github.com/spideryarn/hellozenno/issues)

**Q: Are you planning to add feature X?**
A: Hello Zenno is an open-source project. While the founder has a vision, future development often depends on community interest and contributions. Check the GitHub issues or consider contributing if you have ideas!

**Q: Is this a complete language course?**
A: No. Hello Zenno is a *supplementary* tool focused specifically on vocabulary acquisition and listening practice within the context of reading authentic materials. It assumes you're learning grammar and other aspects of the language through other means (teachers, courses, textbooks). 