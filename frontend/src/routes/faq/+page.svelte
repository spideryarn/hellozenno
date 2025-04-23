<script lang="ts">
  import { onMount } from 'svelte';
  
  // Define record to track open questions
  let openQuestions: Record<string, boolean> = {};
  
  function toggleQuestion(questionId: string) {
    openQuestions[questionId] = !openQuestions[questionId];
  }
  
  onMount(() => {
    // Handle any initialization on mount if needed
  });
  
  // Simplified FAQ data structure
  const faqs = [
    {
      id: "who-for",
      question: "Who is Hello Zenno for?",
      answer: "Intermediate+ learners who can already parse simple sentences but need vocabulary depth & listening speed. Hello Zenno is designed for learners at roughly A2 level and above who want to expand their vocabulary and improve listening comprehension by working with authentic materials."
    },
    {
      id: "free",
      question: "Is it really free?",
      answer: "Browsing & basic use are free. AI‑generated content (dictionary entries, audio) currently run on Greg's credits; heavy users may be asked to plug in their own API key to keep it sustainable."
    },
    {
      id: "teach-grammar",
      question: "Does it teach grammar?",
      answer: "No. Think of Zenno as a reading/listening exoskeleton—pair it with your favourite grammar source. Hello Zenno is a supplementary tool focused specifically on vocabulary acquisition and listening practice."
    },
    {
      id: "languages",
      question: "Which languages are supported?",
      answer: "Any language an LLM can handle confidently (30+ today). If your language isn't listed, open an issue or join the \"centaur‑sourcing\" experiment to help cover generation costs."
    },
    {
      id: "private",
      question: "Can I keep my texts private?",
      answer: "Right now everything you upload is visible to other users, so only use public‑domain or shareable texts. Private uploads are on the roadmap."
    },
    {
      id: "dictionary",
      question: "What makes the dictionary special?",
      answer: "Instead of static definitions, Hello Zenno uses AI to generate rich dictionary entries dynamically as you encounter words. These include etymology (word origins, often a great memory aid!), example sentences showing context, comparisons with similar words, and difficulty indicators."
    },
    {
      id: "listening",
      question: "How does the listening practice work?",
      answer: "We call it dynamic contextual dictation or \"audio flashcards.\" When you practice for a text you've added, the system generates audio snippets of example sentences using the challenging words from that text. You listen, try to understand, and can then reveal the transcription and translation."
    },
    {
      id: "complete-course",
      question: "Is this a complete language course?",
      answer: "No. Hello Zenno is a supplementary tool focused specifically on vocabulary acquisition and listening practice within the context of reading authentic materials. It assumes you're learning grammar and other aspects of the language through other means (teachers, courses, textbooks). For a more complete solution, try <a href=\"https://www.memrise.com\" target=\"_blank\" rel=\"noopener\">Memrise</a>."
    }
  ];
</script>

<svelte:head>
  <title>Frequently Asked Questions - Hello Zenno</title>
</svelte:head>

<!-- FAQ Hero Section -->
<section class="hero-section">
  <div class="container-fluid px-0">
    <div class="nebula-bg faq-header">
      <div class="container py-5">
        <div class="row justify-content-center">
          <div class="col-12 text-center">
            <h1 class="display-4 fw-bold mb-3 hero-title">
              Frequently Asked <span class="text-primary-green">Questions</span>
            </h1>
            <p class="lead mb-4 subtitle">
              Everything you need to know about Hello Zenno
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- FAQ Content -->
<section class="py-5">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-10">
        
        <!-- Simple FAQ list -->
        <div class="accordion" id="faqAccordion">
          {#each faqs as faq}
            <div class="accordion-item faq-item mb-3">
              <h2 class="accordion-header">
                <button 
                  class="accordion-button faq-button {openQuestions[faq.id] ? '' : 'collapsed'}" 
                  type="button"
                  on:click={() => toggleQuestion(faq.id)}
                  aria-expanded={openQuestions[faq.id] ? 'true' : 'false'}
                  aria-controls="collapse-{faq.id}"
                >
                  {faq.question}
                </button>
              </h2>
              <div 
                id="collapse-{faq.id}" 
                class="accordion-collapse collapse {openQuestions[faq.id] ? 'show' : ''}"
              >
                <div class="accordion-body faq-answer">
                  {@html faq.answer}
                </div>
              </div>
            </div>
          {/each}
        </div>
        
        <!-- Contact section -->
        <div class="card contact-card p-4 text-center mt-5">
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

<style>
  /* Hero section styling */
  .hero-section {
    position: relative;
  }
  
  .nebula-bg {
    background-image: url('/img/marketing/homepage_hero_background_nebula2.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    position: relative;
  }
  
  .faq-header {
    padding: 80px 0;
  }
  
  .nebula-bg::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(11, 11, 14, 0.75);
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
  
  /* Accordion styling */
  .faq-item {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    margin-bottom: 1rem;
  }
  
  .faq-item:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }
  
  .faq-button {
    padding: 1.25rem;
    font-weight: 600;
    font-size: 1.1rem;
    color: var(--bs-body-color);
    background-color: var(--hz-color-surface);
  }
  
  .faq-button:not(.collapsed) {
    color: var(--hz-color-primary-green);
    background-color: rgba(69, 193, 135, 0.05);
  }
  
  .faq-button::after {
    background-image: none !important;
    content: '+';
    font-size: 1.5rem;
    font-weight: 300;
    color: var(--hz-color-primary-green);
    transition: transform 0.2s ease;
  }
  
  .faq-button:not(.collapsed)::after {
    content: '−';
    transform: rotate(0deg);
  }
  
  .faq-answer {
    padding: 1.25rem;
    line-height: 1.6;
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
      padding: 60px 0;
    }
    
    .faq-button {
      padding: 1rem;
      font-size: 1rem;
    }
    
    .faq-answer {
      padding: 1rem;
    }
  }
</style>