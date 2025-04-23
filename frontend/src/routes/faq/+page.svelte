<script lang="ts">
  import { onMount } from 'svelte';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
  import TableOfContents from '$lib/components/TableOfContents.svelte';
  import { SITE_NAME } from '$lib/config';
  import ArrowUp from 'phosphor-svelte/lib/ArrowUp';
  
  onMount(() => {
    // Handle any initialization on mount if needed
  });
  
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Update URL to remove the fragment
    history.replaceState(null, document.title, window.location.pathname + window.location.search);
  }
  
  // FAQ data grouped by categories
  const faqCategories = [
    {
      id: "general",
      title: "General Information",
      faqs: [
        {
          id: "what-is-hello-zenno",
          question: "What is Hello Zenno?",
          answer: "Hello Zenno is an open-source web application for intermediate and advanced language learners, designed to assist with vocabulary acquisition and listening practice through AI-generated content. It focuses on helping learners expand vocabulary and improve listening comprehension by working with authentic source materials and AI-generated audio."
        },
        {
          id: "who-is-hello-zenno-for",
          question: "Who is Hello Zenno for?",
          answer: "Intermediate-ish learners who can already parse simple sentences but need vocabulary depth & listening speed. Hello Zenno is designed for learners at roughly A2 level and above who want to expand their vocabulary and improve listening comprehension by working with authentic materials."
        },
        {
          id: "is-hello-zenno-a-complete-language-course",
          question: "Is this a complete language course?",
          answer: "No. Hello Zenno is a supplementary tool focused specifically on vocabulary acquisition and listening practice within the context of reading authentic source materials. It assumes you're learning grammar and other aspects of the language through other means (teachers, courses, textbooks). For a more complete solution, try <a href=\"https://www.memrise.com\" target=\"_blank\" rel=\"noopener\">Memrise</a>."
        },
        {
          id: "does-hello-zenno-teach-grammar",
          question: "Does it teach grammar?",
          answer: "No. Think of Zenno as a reading/listening exoskeleton—pair it with your favourite grammar source. Hello Zenno is a supplementary tool focused specifically on vocabulary acquisition and listening practice."
        },
        {
          id: "philosophy-behind-hello-zenno",
          question: "What's the philosophy behind Hello Zenno?",
          answer: "Hello Zenno is built on several key principles: authentic material-centered learning with real content, comprehension before production (influenced by Krashen's theories), rich contextual understanding of vocabulary, etymology as a memory aid, and progressive listening practice."
        }
      ]
    },
    {
      id: "features",
      title: "Features & Functionality",
      faqs: [
        {
          id: "what-makes-the-dictionary-special",
          question: "What makes the dictionary special?",
          answer: "Instead of static definitions, Hello Zenno uses AI to generate rich dictionary entries dynamically as you encounter words. These include etymology (word origins, often a great memory aid!), example sentences showing context, comparisons with similar words, and difficulty indicators. <br><br><a href='/languages?section=lemmas' class='btn btn-sm btn-outline-success rounded-pill'>Explore Dictionary →</a>"
        },
        {
          id: "how-does-hello-zenno-work-with-source-materials",
          question: "How does Hello Zenno work with source materials?",
          answer: "You can upload various types of content including text, photos of text, URLs, or audio files, and Hello Zenno will highlight words it thinks you'll struggle with because they're difficult. You can hover over these words to learn them in context, with rich dictionary entries that include etymology, mnemonics, example sentences, and comparisons with similar words. <br><br><a href='/languages?section=sources' class='btn btn-sm btn-outline-success rounded-pill'>Browse Source Materials →</a>"
        },
        {
          id: "how-does-hello-zenno-determine-difficult-words",
          question: "How does Hello Zenno determine which words might be difficult?",
          answer: "Hello Zenno uses large language models to make judgments based on word difficulty, frequency, how commonly it appears in the particular source file, and how easy the word would be to guess from context. You can press 'Process this file' to find more words if you need additional help."
        },
        {
          id: "how-does-search-work",
          question: "How does the search functionality work?",
          answer: "Hello Zenno features a flexible AI-generated search that's robust to spelling mistakes. You can search in English or in the target language, and it will present multiple results if there are multiple matches. This makes it slower but more flexible than traditional dictionaries. <br><br><a href='/languages?section=search' class='btn btn-sm btn-success rounded-pill'>Try Word Search →</a>"
        },
        {
          id: "how-does-the-listening-practice-work",
          question: "How does the audio flashcard / listening practice work?",
          answer: "We call it dynamic contextual dictation or \"audio flashcards.\" You can scope the practice to a language, folder, or individual source file. The system finds challenging words in that content and generates example sentences for each, along with audio. It plays the audio for a sentence, and you can listen repeatedly, reveal the transcription, and then the translation. Your task is to understand what's being said, though there are no scores or feedback mechanisms yet. This focused listening practice helps bridge the gap between reading comprehension and auditory understanding. <br><br><a href='/languages?section=flashcards' class='btn btn-sm btn-success rounded-pill'>Try Flashcards →</a>"
        }
      ]
    },
    {
      id: "technical",
      title: "Technical & Access",
      faqs: [
        {
          id: "which-languages-are-supported",
          question: "Which languages are supported?",
          answer: "Any language an LLM can handle confidently (30+ today). If your language isn't listed, open an issue or join the \"centaur-sourcing\" experiment to help cover generation costs. <br><br><a href='/languages' class='btn btn-sm btn-primary rounded-pill'>See Supported Languages →</a>"
        },
        {
          id: "is-hello-zenno-really-free",
          question: "Is it really free?",
          answer: "Browsing & basic use are free. AI‑generated content (dictionary entries, audio) currently run on Greg's credits; heavy users may be asked to plug in their own API key to keep it sustainable."
        },
        {
          id: "can-i-keep-my-source-files-private",
          question: "Can I keep my source files private?",
          answer: "Right now everything you upload is visible to other users, so only use public‑domain or shareable source materials. Private uploads are on the roadmap."
        },
        {
          id: "what-tech-stack-is-used",
          question: "What technology stack is Hello Zenno built on?",
          answer: "Hello Zenno uses Anthropic Claude Sonnet 3.7, a cutting-edge LLM, for generating content. It uses Eleven Labs for audio generation. The backend is built with Python Flask, and the frontend uses SvelteKit. The application is hosted on Vercel with Supabase for the database."
        },
        {
          id: "mobile-apps-offline",
          question: "Are there plans for mobile apps or offline functionality?",
          answer: "There are currently no immediate plans for mobile apps or offline functionality. The web app could potentially be accessed via mobile browsers, but a dedicated mobile app is not on the immediate roadmap. Offline functionality is challenging due to the AI-generation component of the application."
        },
        {
          id: "ai-reliability",
          question: "How reliable is the AI-generated content?",
          answer: "The AI-generated content is generally high quality, especially for well-supported languages. However, all dictionary content is AI-generated, so there is a small risk of inaccuracies. Users are encouraged to report any issues they find through GitHub issues."
        }
      ]
    },
    {
      id: "usage",
      title: "Using Hello Zenno",
      faqs: [
        {
          id: "getting-started",
          question: "How should I get started with Hello Zenno?",
          answer: "The best way to start is to select the language you're learning and check if there are already source materials at your desired difficulty level. Alternatively, you can add your own content by pasting a URL, uploading images, audio files, or typing in text directly. After processing, you can start reading with hover-enabled dictionary support or try the audio flashcards feature. <br><br><a href='/languages' class='btn btn-sm btn-primary rounded-pill'>Get Started Now →</a>"
        },
        {
          id: "user-journey",
          question: "What's the typical user journey?",
          answer: "First, select the language you're learning. Then, either browse existing source materials or add your own by creating a source folder and adding files to it. Hello Zenno will extract text (if necessary), translate it, and highlight potentially difficult words. You can hover over these words to see their meanings, and click for full dictionary entries. You can also practice with audio flashcards generated from the difficult words in your materials. <br><br><div class='d-flex gap-2 flex-wrap'><a href='/languages' class='btn btn-sm btn-primary rounded-pill'>Choose a Language →</a> <a href='/languages?section=sources' class='btn btn-sm btn-outline-success rounded-pill'>Browse Sources →</a> <a href='/languages?section=flashcards' class='btn btn-sm btn-outline-success rounded-pill'>Try Flashcards →</a></div>"
        },
        {
          id: "reporting-bugs",
          question: "How can I report bugs or give feedback?",
          answer: "The best way to report bugs or provide feedback is by opening an issue on GitHub at <a href=\"https://github.com/spideryarn/hellozenno/issues\" target=\"_blank\" rel=\"noopener\">github.com/spideryarn/hellozenno/issues</a>."
        },
        {
          id: "tracking-progress",
          question: "Does Hello Zenno track my learning progress?",
          answer: "No, Hello Zenno doesn't have progress tracking features. You can ignore words you've learned so they don't appear in your flashcards any more."
        }
      ]
    },
    {
      id: "community",
      title: "Community & Future",
      faqs: [
        {
          id: "what-is-centaur-sourcing",
          question: "What is 'centaur-sourcing'?",
          answer: "Centaur-sourcing is where humans and AI collaborate at scale to create things that would be very hard for either to create alone. Think of it by analogy with crowdsourcing, where a large groups of people have built the astonishing modern-day intellectual cathedral that is the Wikipedia. How could AI help with such efforts? In Hello Zenno, one potential idea would be for users to pool their API keys and resources to AI-generate rich dictionary entries and learning materials for languages they're interested in, making them available to the wider community. And then, of course, we'd need people to play the critical role of checking, confirming, improving and generally playing an editorial role."
        },
        {
          id: "how-participate-centaur-sourcing",
          question: "How can I participate in centaur-sourcing?",
          answer: "The main way to participate currently would be by contributing your API key to help cover the costs of AI generation for languages you're interested in. In the future, there may be more ways for language experts to review and improve AI-generated content."
        },
        {
          id: "open-api-plans",
          question: "Is there a plan for an open API?",
          answer: "There are plans to potentially make the read-only part of the API freely available for developers to build upon. This would allow other applications to leverage the rich dictionary entries and audio content generated through centaur-sourcing."
        },
        {
          id: "biggest-challenges",
          question: "What are the biggest challenges for Hello Zenno?",
          answer: "Besides AI costs, the current challenges include complexity of the interface, generation speed (especially for full metadata for words), and content sourcing considerations. The project is looking for collaborators to help address these challenges."
        },
        {
          id: "future-plans",
          question: "What future features are planned?",
          answer: "Future plans include generating sentences that use multiple words from a source file in novel combinations, private uploading options for copyrighted materials, and enhanced community features to support the centaur-sourcing concept."
        }
      ]
    },
    {
      id: "misconceptions",
      title: "Common Misconceptions",
      faqs: [
        {
          id: "not-for-beginners",
          question: "Is Hello Zenno suitable for beginners?",
          answer: "Hello Zenno is not designed for complete beginners. It works best for learners who already have basic grammar knowledge and vocabulary (roughly A2 level or above) and want to expand their skills using authentic materials."
        },
        {
          id: "not-complete-solution",
          question: "Is Hello Zenno a complete language learning solution?",
          answer: "No, Hello Zenno doesn't pretend to be a complete language learning solution. It focuses specifically on vocabulary acquisition in context and listening practice. You'll still need other resources for grammar, speaking practice, and beginner-level instruction."
        },
        {
          id: "not-offline",
          question: "Can I use Hello Zenno offline?",
          answer: "No, Hello Zenno requires an internet connection as it relies on AI generation for many of its features. There are currently no plans for offline functionality."
        },
        {
          id: "privacy-misconceptions",
          question: "Are my uploaded source files private?",
          answer: "No, currently all uploaded content is public and visible to all users. Only upload public domain or freely shareable source materials. There are plans to add private upload options in the future."
        }
      ]
    }
  ];
  
  // Flatten categories for the ToC and page rendering
  const allFaqs = faqCategories.flatMap(category => category.faqs);
</script>

<svelte:head>
  <title>FAQ | {SITE_NAME}</title>
  <meta name="description" content="Frequently asked questions about Hello Zenno, the AI-powered language learning assistant focusing on vocabulary acquisition and listening practice." />
</svelte:head>

<NebulaBackground>
  <!-- FAQ Hero Section -->
  <section class="hero-section">
    <div class="container-fluid px-0">
      <div class="faq-header">
        <div class="container py-4">
          <div class="row justify-content-center">
            <div class="col-12 text-center">
              <h1 class="display-4 fw-bold mb-3 hero-title">
                Frequently Asked <span class="text-primary-green">Questions</span>
              </h1>
              <!-- <p class="lead mb-3 subtitle">
                Everything you need to know about Hello Zenno
              </p> -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ Content -->
  <section class="py-4">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          
          <!-- Table of Contents -->
          <TableOfContents categories={faqCategories} />
          
          <!-- FAQ list - all visible and categorized -->
          <div class="faq-list">
            {#each faqCategories as category}
              <div id={category.id} class="category-container mb-4">
                <h2 class="h3 category-title mb-3 text-primary-green">{category.title}</h2>
                
                {#each category.faqs as faq}
                  <div class="faq-item" id={faq.id}>
                    <div class="faq-header">
                      <h3 class="h4 faq-question mb-1 text-primary-green">
                        <a href="#{faq.id}" class="anchor-link">#</a>
                        {faq.question}
                      </h3>
                      <button 
                        class="btn-back-to-top" 
                        on:click={scrollToTop} 
                        aria-label="Back to top"
                      >
                        <ArrowUp size={20} weight="fill" />
                      </button>
                    </div>
                    <div class="faq-answer">
                      {@html faq.answer}
                    </div>
                  </div>
                {/each}
              </div>
            {/each}
          </div>
          
          <!-- Contact section -->
          <div class="card contact-card p-4 text-center mt-4">
            <h3 class="mb-3">Still have questions?</h3>
            <p class="mb-4">
              If you can't find the answer you're looking for, please reach out to us directly.
            </p>
            <div class="d-flex justify-content-center gap-3">
              <a 
                href="mailto:hellozenno@gregdetre.com" 
                class="btn btn-primary rounded-pill"
              >
                Email Us
              </a>
              <a 
                href="https://github.com/spideryarn/hellozenno/issues" 
                target="_blank" 
                rel="noopener" 
                class="btn btn-outline-primary rounded-pill"
              >
                GitHub Issues
              </a>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </section>
</NebulaBackground>

<style>
  /* Hero section styling - modified to start at the top */
  .hero-section {
    position: relative;
    padding-top: 0;
    z-index: 1;
    margin-top: 0;
  }
  
  .faq-header {
    padding: 0px 0 20px;
  }
  
  .hero-title {
    position: relative;
    z-index: 2;
    color: #f8f9fa;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  }
  
  .subtitle {
    position: relative;
    z-index: 2;
    color: #d7dadd;
  }
  
  .text-primary-green {
    color: var(--hz-color-primary-green);
  }
  
  /* Table of Contents styling moved to TableOfContents.svelte component */
  
  /* Category styling */
  .category-container {
    padding-top: 1.5rem;
    border-top: 2px solid var(--hz-color-border);
  }
  
  .category-title {
    margin-bottom: 1.5rem;
    position: relative;
    display: inline-block;
  }
  
  .category-title::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 50px;
    height: 3px;
    background-color: var(--hz-color-primary-green);
    border-radius: 3px;
  }
  
  /* FAQ styling */
  .faq-item {
    padding: 1.5rem;
    background-color: var(--hz-color-surface);
    border-radius: 8px;
    position: relative;
    border: 1px solid var(--hz-color-border);
    margin-bottom: 1.25rem;
    transition: all 0.2s ease;
  }
  
  .faq-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-color: var(--hz-color-primary-green-dark);
  }
  
  .faq-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.15rem;
  }
  
  .faq-question {
    font-weight: 600;
    position: relative;
    margin: 0;
    padding-right: 2rem;
    font-size: 1.25rem;
  }
  
  .anchor-link {
    color: var(--hz-color-border);
    position: absolute;
    left: -1.5rem;
    text-decoration: none;
    font-weight: normal;
    opacity: 0.5;
    transition: opacity 0.2s ease;
  }
  
  .anchor-link:hover {
    opacity: 1;
    color: var(--hz-color-primary-green);
  }
  
  .btn-back-to-top {
    background-color: rgba(102, 154, 115, 0.05);
    border: 1px solid var(--hz-color-border);
    color: var(--hz-color-text-secondary);
    padding: 0.35rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0.9;
    transition: all 0.2s ease;
    margin-top: -0.35rem;
  }
  
  .btn-back-to-top:hover {
    opacity: 1;
    color: var(--hz-color-primary-green);
    background-color: rgba(102, 154, 115, 0.15);
    border-color: var(--hz-color-primary-green);
    transform: translateY(-2px);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }
  
  .faq-answer {
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }
  
  /* Contact card */
  .contact-card {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 12px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  }
  
  /* Add responsive adjustments */
  @media (max-width: 768px) {
    .faq-header {
      padding: 30px 0;
    }
    
    .anchor-link {
      opacity: 0.8;
      position: relative;
      left: 0;
      margin-right: 0.5rem;
    }
    /* categories-toc styles moved to TableOfContents.svelte */
  }
</style>