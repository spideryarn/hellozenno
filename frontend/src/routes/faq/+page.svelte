<script lang="ts">
  import { onMount } from 'svelte';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
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
  
  // Simplified FAQ data structure
  const faqs = [
    {
      id: "who-is-hello-zenno-for",
      question: "Who is Hello Zenno for?",
      answer: "Intermediate+ learners who can already parse simple sentences but need vocabulary depth & listening speed. Hello Zenno is designed for learners at roughly A2 level and above who want to expand their vocabulary and improve listening comprehension by working with authentic materials."
    },
    {
      id: "is-hello-zenno-really-free",
      question: "Is it really free?",
      answer: "Browsing & basic use are free. AI‑generated content (dictionary entries, audio) currently run on Greg's credits; heavy users may be asked to plug in their own API key to keep it sustainable."
    },
    {
      id: "does-hello-zenno-teach-grammar",
      question: "Does it teach grammar?",
      answer: "No. Think of Zenno as a reading/listening exoskeleton—pair it with your favourite grammar source. Hello Zenno is a supplementary tool focused specifically on vocabulary acquisition and listening practice."
    },
    {
      id: "which-languages-are-supported",
      question: "Which languages are supported?",
      answer: "Any language an LLM can handle confidently (30+ today). If your language isn't listed, open an issue or join the \"centaur‑sourcing\" experiment to help cover generation costs."
    },
    {
      id: "can-i-keep-my-texts-private",
      question: "Can I keep my texts private?",
      answer: "Right now everything you upload is visible to other users, so only use public‑domain or shareable texts. Private uploads are on the roadmap."
    },
    {
      id: "what-makes-the-dictionary-special",
      question: "What makes the dictionary special?",
      answer: "Instead of static definitions, Hello Zenno uses AI to generate rich dictionary entries dynamically as you encounter words. These include etymology (word origins, often a great memory aid!), example sentences showing context, comparisons with similar words, and difficulty indicators."
    },
    {
      id: "how-does-the-listening-practice-work",
      question: "How does the listening practice work?",
      answer: "We call it dynamic contextual dictation or \"audio flashcards.\" When you practice for a text you've added, the system generates audio snippets of example sentences using the challenging words from that text. You listen, try to understand, and can then reveal the transcription and translation."
    },
    {
      id: "is-hello-zenno-a-complete-language-course",
      question: "Is this a complete language course?",
      answer: "No. Hello Zenno is a supplementary tool focused specifically on vocabulary acquisition and listening practice within the context of reading authentic materials. It assumes you're learning grammar and other aspects of the language through other means (teachers, courses, textbooks). For a more complete solution, try <a href=\"https://www.memrise.com\" target=\"_blank\" rel=\"noopener\">Memrise</a>."
    }
  ];
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
          <div class="card toc-card mb-4 p-4">
            <h2 class="h4 mb-3">Table of Contents</h2>
            <ul class="toc-list">
              {#each faqs as faq}
                <li>
                  <a href="#{faq.id}" class="toc-link">
                    {faq.question}
                  </a>
                </li>
              {/each}
            </ul>
          </div>
          
          <!-- FAQ list - all visible -->
          <div class="faq-list">
            {#each faqs as faq}
              <div class="faq-item" id={faq.id}>
                <div class="faq-header">
                  <h2 class="h4 faq-question mb-1 text-primary-green">
                    <a href="#{faq.id}" class="anchor-link">#</a>
                    {faq.question}
                  </h2>
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
  
  /* Table of Contents styling */
  .toc-card {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 8px;
  }
  
  .toc-list {
    list-style-type: none;
    padding-left: 0;
    margin-bottom: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    grid-gap: 0.75rem;
  }
  
  .toc-list li {
    margin-bottom: 0;
  }
  
  .toc-link {
    color: var(--hz-color-primary-green);
    text-decoration: none;
    transition: all 0.2s ease;
    display: inline-block;
    padding: 0.25rem 0;
  }
  
  .toc-link:hover {
    text-decoration: underline;
    opacity: 0.8;
    transform: translateX(3px);
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
  }
</style>