<script lang="ts">
  import { onMount } from 'svelte';
  import { marked } from 'marked';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
  import TableOfContents from '$lib/components/TableOfContents.svelte';
  import { SITE_NAME } from '$lib/config';
  import type { PageData } from './$types';
  
  // Import Phosphor icons
  import Calendar from 'phosphor-svelte/lib/Calendar';
  import User from 'phosphor-svelte/lib/User';
  import ArrowLeft from 'phosphor-svelte/lib/ArrowLeft';
  
  export let data: PageData;
  
  // Format date for display (e.g., "April 23, 2024")
  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  // Extract headings from markdown content for table of contents
  function extractHeadings(content: string) {
    if (!content || typeof content !== 'string') {
      return [];
    }
    
    const headings = [];
    const headingRegex = /^##\s+(.+)$/gm;
    let match;
    
    while ((match = headingRegex.exec(content)) !== null) {
      const title = match[1].trim();
      const id = title.toLowerCase().replace(/[^\w\s-]/g, '')
                       .replace(/\s+/g, '-');
      headings.push({ id, title });
    }
    
    return headings;
  }
  
  // Configure marked options
  const renderer = new marked.Renderer();
  
  // Override the heading renderer to add IDs for TOC linking
  renderer.heading = function(text, level) {
    // Ensure text is a string and handle case where text is an object
    const textStr = typeof text === 'object' ? (text.title || String(text)) : String(text);
    const id = textStr.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
    return `<h${level} id="${id}">${textStr}</h${level}>`;
  };
  
  // Override link renderer to add proper styling
  renderer.link = function(href, title, text) {
    // Apply appropriate styling for links based on your design system
    const titleAttr = title ? ` title="${title}"` : '';
    return `<a href="${href}"${titleAttr} class="text-primary-green">${text}</a>`;
  };
  
  marked.setOptions({
    renderer: renderer,
    breaks: true, // Convert '\n' to <br>
    gfm: true     // Enable GitHub flavored markdown
  });
  
  // Safely extract TOC items
  const tocItems = data.post?.content ? extractHeadings(data.post.content) : [];
  
  onMount(() => {
    // Add any initialization on mount if needed
  });
</script>

<svelte:head>
  <title>{data.post.title} | Blog | {SITE_NAME}</title>
  <meta name="description" content={data.post.excerpt} />
</svelte:head>

<NebulaBackground>
  <article class="blog-post">
    <div class="container py-4">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <!-- Back to blog link -->
          <div class="mb-4">
            <a href="/blog" class="btn btn-outline-primary rounded-pill btn-sm back-button">
              <ArrowLeft size={16} weight="fill" class="me-1" /> Back to all posts
            </a>
          </div>
          
          <!-- Post header -->
          <header class="post-header mb-4">
            <h1 class="post-title display-4 fw-bold mb-3 text-primary-green">
              {data.post.title}
            </h1>
            
            <div class="post-meta mb-4">
              <div class="post-meta-content">
                <span class="post-date">
                  <Calendar size={16} weight="fill" class="me-1" />
                  {formatDate(data.post.date)}
                </span>
                <span class="post-meta-divider"></span>
                <span class="post-author">
                  <User size={16} weight="fill" class="me-1" />
                  {data.post.author}
                </span>
              </div>
            </div>
            
            {#if data.post.coverImage}
              <div class="post-cover-image-container mb-4">
                <a href="/language/el/source/250421-odyssea-4/1000012167-jpg/text">
                  <img src={data.post.coverImage} alt={data.post.title} class="post-cover-image img-fluid rounded" />
                </a>
              </div>
            {/if}
          </header>
          
          <!-- Table of Contents (only if we have headings) -->
          {#if tocItems.length > 0}
            <TableOfContents items={tocItems} title="In this article" />
          {/if}
          
          <!-- Post content -->
          <div class="post-content">
            <h2 id="breaking-through-the-intermediate-plateau">Breaking through the intermediate plateau</h2>
            <p>Learning a language can feel like climbing a mountain. The initial ascent is steep but clear - learn basic greetings, master simple present tense, memorize 500 common words. But many learners reach what linguists call the "intermediate plateau" - where progress slows dramatically.</p>
            <p>It's not that you've stopped learning. It's that you need <em>thousands</em> more words before native content feels comfortable. And worse - listening comprehension often lags far behind reading ability.</p>
            
            <h2 id="the-hello-zenno-approach">The Hello Zenno approach</h2>
            <p>Hello Zenno takes a different approach:</p>
            <ol>
              <li><strong>Import any text you care about</strong> - articles, stories, or transcripts that genuinely interest you</li>
              <li><strong>Highlight tricky words with AI assistance</strong> - we predict which words might trip you up</li>
              <li><strong>Generate rich dictionary entries on demand</strong> - including etymology, similar words, and example usage</li>
              <li><strong>Train your ears with audio flashcards</strong> - hear the same words in new contexts</li>
            </ol>
            <p>The most powerful feature is our <strong>enhanced text view</strong> where you can hover over any word to instantly see its meaning without disrupting your reading flow.</p>
            
            <h2 id="try-it-today">Try it today</h2>
            <p>Hello Zenno is completely free to use. Sign up and import your first text to experience a new way of tackling intermediate language learning.</p>

          </div>
          
          <!-- Post footer -->
          <footer class="post-footer mt-5">
            <div class="card p-5 call-to-action">
              <h3 class="text-primary-green mb-3">Ready to try Hello Zenno?</h3>
              <p class="mb-4">
                Start your language learning journey today with our AI-powered tools.
              </p>
              <div class="cta-buttons">
                <a href="/languages" class="btn btn-primary rounded-pill px-4 py-2">Get Started</a>
                <a href="/faq" class="btn btn-outline-secondary rounded-pill px-4 py-2">Learn More</a>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  </article>
</NebulaBackground>


<style>
  /* Post header styling */
  .post-title {
    line-height: 1.2;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .post-meta {
    font-size: 0.9rem;
  }
  
  .post-meta-content {
    display: inline-flex;
    align-items: center;
    background-color: rgba(var(--hz-color-background-rgb), 0.7);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    backdrop-filter: blur(4px);
    border: 1px solid var(--hz-color-border);
  }
  
  .post-date, .post-author {
    display: inline-flex;
    align-items: center;
    color: var(--hz-color-text-secondary);
  }
  
  .post-meta-divider {
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: var(--hz-color-border);
    margin: 0 0.8rem;
  }
  
  .post-cover-image-container {
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  }
  
  .post-cover-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
  }
  
  /* Post content styling */
  .post-content {
    font-size: 1.1rem;
    line-height: 1.7;
    color: var(--hz-color-text-main);
    margin-bottom: 2rem;
  }
  
  .post-content :global(h2) {
    color: var(--hz-color-primary-green);
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-weight: 600;
  }
  
  .post-content :global(h3) {
    color: var(--hz-color-primary-green-light);
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  .post-content :global(p) {
    margin-bottom: 1.5rem;
  }
  
  .post-content :global(ul), .post-content :global(ol) {
    margin-bottom: 1.5rem;
    padding-left: 1.75rem;
  }
  
  .post-content :global(li) {
    margin-bottom: 0.5rem;
  }
  
  .post-content :global(a) {
    color: var(--hz-color-primary-green);
    text-decoration: none;
    transition: all 0.2s ease;
  }
  
  .post-content :global(a:hover) {
    color: var(--hz-color-primary-green-light);
    text-decoration: underline;
  }
  
  .post-content :global(blockquote) {
    border-left: 4px solid var(--hz-color-primary-green);
    padding-left: 1rem;
    font-style: italic;
    color: var(--hz-color-text-secondary);
    margin: 1.5rem 0;
  }
  
  .post-content :global(code) {
    background-color: rgba(0, 0, 0, 0.2);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: var(--hz-font-monospace);
    font-size: 0.9em;
  }
  
  .post-content :global(pre) {
    background-color: rgba(0, 0, 0, 0.2);
    padding: 1rem;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 1.5rem;
  }
  
  .post-content :global(pre code) {
    background-color: transparent;
    padding: 0;
  }
  
  .post-content :global(img) {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    margin: 1.5rem 0;
  }
  
  .post-content :global(hr) {
    border: 0;
    height: 1px;
    background-color: var(--hz-color-border);
    margin: 2rem 0;
  }
  
  /* Back button styling */
  .back-button {
    display: inline-flex;
    align-items: center;
    font-size: 0.9rem;
    transition: transform 0.2s ease;
    border-color: var(--hz-color-primary-green);
    color: var(--hz-color-primary-green);
    padding: 0.5rem 1rem;
  }
  
  .back-button:hover {
    transform: translateX(-3px);
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1);
    border-color: var(--hz-color-primary-green);
    color: var(--hz-color-primary-green-light);
  }
  
  /* Call to action card styling */
  .call-to-action {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-primary-green-dark);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(var(--hz-color-primary-green-rgb), 0.2);
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  
  .call-to-action::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--hz-color-primary-green);
    background: linear-gradient(90deg, var(--hz-color-primary-green-dark) 0%, var(--hz-color-primary-green) 50%, var(--hz-color-primary-green-light) 100%);
  }
  
  .text-primary-green {
    color: var(--hz-color-primary-green);
  }
  
  .cta-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }
  
  @media (max-width: 576px) {
    .cta-buttons {
      flex-direction: column;
    }
  }
</style>