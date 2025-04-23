<script lang="ts">
  import { onMount } from 'svelte';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
  import { SITE_NAME } from '$lib/config';
  
  // For now, let's go back to the inline SVG approach since it works 
  // and fixes the SSR issue with phosphor-svelte
  
  let showTimeline = true;
  
  onMount(() => {
    // Add any onMount logic if needed
  });

  // Simple icon components using inline SVG
  const BrainCircuitIcon = () => `
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 256 256">
      <path d="M96,140a12,12,0,1,1-12-12A12,12,0,0,1,96,140Zm68-12a12,12,0,1,0,12,12A12,12,0,0,0,164,128Zm66.7-29.7-112-64a12,12,0,0,0-11.9,0l-112,64a12,12,0,0,0-6,10.4v56.6a12,12,0,0,0,6,10.4l112,64a12.1,12.1,0,0,0,11.9,0l112-64a12,12,0,0,0,6-10.4V108.7A12,12,0,0,0,230.7,98.3Zm-18,62.4L188,142.1a12,12,0,0,0-5.5-1.1,35.8,35.8,0,0,0-1.5-4.1A36,36,0,0,0,164,116a12,12,0,0,0-11.5-20,12.3,12.3,0,0,0-3.7.9,36.1,36.1,0,0,0-48,3.3A35.6,35.6,0,0,0,93,116a35.5,35.5,0,0,0,3,14.9,36,36,0,0,0-20,32.3V176a12,12,0,0,0-12,12v6.3l-28,16V113.8L122,58.2V76a12,12,0,0,0,10.4,11.9A44,44,0,0,1,173.2,96H196a12,12,0,0,0,12-12V64.8l4.7,2.7ZM161.1,108l.9.4a6.1,6.1,0,0,0,1.1.3,23.7,23.7,0,0,1,10.2,10.6A23.7,23.7,0,0,1,176,128a24,24,0,0,1-17.4,23A36.5,36.5,0,0,0,161.1,108Zm-73.9,32A24,24,0,0,1,80,116.3a24,24,0,0,1,48,0A24,24,0,0,1,87.2,140Zm21.6,18.9A35.8,35.8,0,0,0,120,164.1,35.2,35.2,0,0,0,128,188a36.7,36.7,0,0,0,.6-6,36,36,0,0,0-18.8-31.1ZM64,164.1a23.9,23.9,0,0,1,47.7-1,35.4,35.4,0,0,0-10.4-6.3A36.5,36.5,0,0,0,88,163.1,24.5,24.5,0,0,1,88,140a7.6,7.6,0,0,0-7.6-7.9H80a8,8,0,0,0-8,8.1,40.1,40.1,0,0,0,1.2,8.9A36,36,0,0,0,64,164.1ZM100,188a24,24,0,0,1-24-24,23.3,23.3,0,0,1,1.1-7.1,20.3,20.3,0,0,1,2.3.2,36.8,36.8,0,0,0,18.6,30.6,26.3,26.3,0,0,1,2,.3Zm28,17.8-48-27.4V176a12,12,0,0,0-12-12v-3.2a40.4,40.4,0,0,1,.4-5.8A36,36,0,0,0,92,188a37.9,37.9,0,0,0,4-.2,36,36,0,0,0,64,0,37.9,37.9,0,0,0,4,.2,35.9,35.9,0,0,0,23.2-8.5l3.5,2ZM160,188a24,24,0,0,1-24-24c0-.3,0-0.7,0-1a36,36,0,0,0,19.2-31.3,40.1,40.1,0,0,0,1.2-8.9,8,8,0,0,0-8-8.1,7.6,7.6,0,0,0-7.6,7.9,24.5,24.5,0,0,1-13.4,23.1,36,36,0,0,0-19.6,31.9,36.7,36.7,0,0,0,.6,6,36,36,0,0,0,68.7-15.9,25.8,25.8,0,0,1-8,3.8A23.8,23.8,0,0,1,160,188Zm36-24v-3.2a35.2,35.2,0,0,0-.6-5.9l6.8,3.9a11.9,11.9,0,0,0,5.8,1.5V176A12,12,0,0,0,196,164Zm-28-72a23.9,23.9,0,0,1,24,24a35.8,35.8,0,0,0-9.4,3.3,36.8,36.8,0,0,0-14.1-15.2A22.9,22.9,0,0,1,168,92Zm28-12H173.2A56.1,56.1,0,0,0,131,76.8,23.9,23.9,0,0,1,134,64V46.2L186,76.5V84Z"/>
    </svg>
  `;
  
  const BookOpenIcon = () => `
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 256 256">
      <path d="M224,48H168a28,28,0,0,0-28,28,8,8,0,0,1-16,0V76a28,28,0,0,0-28-28H40A16,16,0,0,0,24,64V192a16,16,0,0,0,16,16H96a28,28,0,0,1,28,28,8,8,0,0,0,16,0,28,28,0,0,1,28-28h56a16,16,0,0,0,16-16V64A16,16,0,0,0,224,48ZM96,176H40V64H96a12,12,0,0,1,12,12V192.4A44.3,44.3,0,0,0,96,176Zm120,0H168a44.3,44.3,0,0,0-12,16.4V76a12,12,0,0,1,12-12h48Z"/>
    </svg>
  `;
  
  const CodeIcon = () => `
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 256 256">
      <path d="M69.1,94.1,28.5,128l40.6,33.9a8,8,0,1,1-10.2,12.2l-48-40a8,8,0,0,1,0-12.2l48-40a8,8,0,0,1,10.2,12.2Zm176,27.8-48-40a8,8,0,0,0-10.2,12.2L227.5,128l-40.6,33.9a8,8,0,1,0,10.2,12.2l48-40a8,8,0,0,0,0-12.2ZM162.2,32.2a8,8,0,0,0-10.4,4.4l-64,176a8,8,0,0,0,4.4,10.4A8.2,8.2,0,0,0,96,224a8,8,0,0,0,7.6-5.5l64-176A8,8,0,0,0,162.2,32.2Z"/>
    </svg>
  `;
  
  const GithubLogoIcon = () => `
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 256 256">
      <path d="M136,184a8,8,0,0,1-16,0c0-24,16-36,16-36a8,8,0,0,1,0,12S136,169.1,136,184Zm88-56a76,76,0,1,1-76-76A76.1,76.1,0,0,1,224,128Zm-16,0a60,60,0,0,0-9.8-32.8c-2.9,2.2-8.9,7.5-11.7,10.4a41.7,41.7,0,0,0-5.8,8,24,24,0,0,1-8.9,8.9c-6.1,3.6-13.8,5.3-22.9,5.4,1.8,2.8,5.7,9.4,5.7,17.8,0,11.9-5.3,27.9-5.3,27.9a60,60,0,0,0,58.7-45.6ZM128,68a59.4,59.4,0,0,0-20,3.5,60,60,0,0,0-37.6,45.1q-.9,4.5-1,9.4a59.6,59.6,0,0,0,0,8,60.3,60.3,0,0,0,.6,8c0,.5.1,1,.2,1.4a60,60,0,0,0,117.6,0c.1-.5.1-1,.2-1.4a60.3,60.3,0,0,0,.6-8,59.6,59.6,0,0,0,0-8c-.1-1.2-.2-2.3-.3-3.5s-.3-2.3-.5-3.5c0-.6-.1-1.1-.2-1.7A60,60,0,0,0,128,68Zm-8,36c-8,0-14-4-14-12s6-16,14-16,14,8,14,16S128,104,120,104Z"/>
    </svg>
  `;
</script>

<svelte:head>
  <title>About | {SITE_NAME}</title>
  <meta name="description" content="Learn about Hello Zenno, an open-source project providing AI-powered dictionary and listening practice for language learners." />
</svelte:head>

<NebulaBackground>
  <!-- Hero section -->
  <section class="hero-section">
    <div class="container-fluid px-0">
      <div class="container py-4">
        <div class="row justify-content-center">
          <div class="col-12 text-center">
            <h1 class="display-4 fw-bold mb-2 hero-title">
              About <span class="text-primary-green">Hello Zenno</span>
            </h1>
            <p class="lead mb-3 subtitle">
              Meet the human (& friendly alien) behind our language learning assistant
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Founder section -->
  <section class="py-4">
    <div class="container">
      <div class="row justify-content-center align-items-center">
        <div class="col-lg-4 text-center mb-4 mb-lg-0">
          <div class="alien-avatars-container">
            <img src="/img/marketing/alien_avatars1.png" alt="Hello Zenno alien avatars" class="img-fluid rounded" style="max-width: 300px;" />
          </div>
        </div>
        <div class="col-lg-8">
          <div class="card p-4 founder-card shadow">
            <h2 class="mb-3">The Story Behind Hello Zenno</h2>
            <p class="founder-intro">
              Hello Zenno began as a personal quest to crack intermediate Greek.
          </p>
            
            <blockquote class="blockquote mt-4 p-3">
              <p class="mb-0">
                "I've always dreamed of a tool that would help me <em>read stories in another language</em> with the help of a magic dictionary, 
                then hammer the same words into my ears."
              </p>
            </blockquote>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Philosophy section -->
  <section class="py-5 content-section">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <h2 class="section-title text-center mb-4">Our Philosophy</h2>
          
          <div class="row">
            <div class="col-md-4 mb-4">
              <div class="feature-card h-100">
                <div class="text-center mb-3">
                  <div class="text-primary-green">
                    {@html BrainCircuitIcon()}
                  </div>
                </div>
                <h3 class="feature-title text-center">Comprehension before production</h3>
                <p class="feature-description">
                  Inspired by Krashen's theories, we emphasize understanding before speaking. 
                  This allows you to build a strong foundation by absorbing language naturally.
                </p>
              </div>
            </div>
            
            <div class="col-md-4 mb-4">
              <div class="feature-card h-100">
                <div class="text-center mb-3">
                  <div class="text-primary-green">
                    {@html BookOpenIcon()}
                  </div>
                </div>
                <h3 class="feature-title text-center">Etymology sticks</h3>
                <p class="feature-description">
                  Stories of word origins forge powerful memory hooks. By understanding how words evolved,
                  you create lasting connections between languages and concepts.
                </p>
              </div>
            </div>
            
            <div class="col-md-4 mb-4">
              <div class="feature-card h-100">
                <div class="text-center mb-3">
                  <div class="text-primary-green">
                    {@html CodeIcon()}
                  </div>
                </div>
                <h3 class="feature-title text-center">Open knowledge</h3>
                <p class="feature-description">
                  Our code and (where licensing allows) data are public. We believe in sharing resources
                  to enable community-driven language learning innovation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Timeline section -->
  <section class="py-5 content-section">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="section-title mb-0">The Road So Far</h2>
            <button 
              class="btn btn-sm btn-outline-secondary" 
              on:click={() => showTimeline = !showTimeline}
              aria-label={showTimeline ? "Hide timeline" : "Show timeline"}
            >
              {showTimeline ? "Hide" : "Show"}
            </button>
          </div>
          
          {#if showTimeline}
            <div class="timeline-container">
              <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                  <div class="timeline-date">2024</div>
                  <div class="timeline-title">First MVP open‑sourced on GitHub</div>
                  <div class="timeline-description">
                    The first public release of Hello Zenno, making AI-assisted language learning
                    available to everyone.
                  </div>
                </div>
              </div>
              
              <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                  <div class="timeline-date">2025</div>
                  <div class="timeline-title">30 languages live; dynamic dictation v2</div>
                  <div class="timeline-description">
                    Expanded language support and improved audio training features for a more
                    comprehensive learning experience.
                  </div>
                </div>
              </div>
              
              <div class="timeline-item future">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                  <div class="timeline-date">2025</div>
                  <div class="timeline-title">Community "centaur‑sourcing" pilot</div>
                  <div class="timeline-description">
                    Launching collaborative human+AI content creation to build richer,
                    more accurate language resources together.
                  </div>
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </section>

  <!-- Contribute section -->
  <section class="py-5 content-section">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-8 text-center">
          <div class="card p-4 contribute-card border-0 shadow">
            <div class="text-center mb-3">
              <div class="text-primary-green">
                {@html GithubLogoIcon()}
              </div>
            </div>
            <h3 class="section-title mb-3">Want to co‑build?</h3>
            <p class="mb-4">
              Hello Zenno is an open-source project and welcomes contributions from developers, language
              enthusiasts, and anyone passionate about improving language learning.
            </p>
            <a 
              href="https://github.com/spideryarn/hellozenno" 
              target="_blank" 
              rel="noopener noreferrer"
              class="btn btn-primary btn-lg px-4 rounded-pill"
            >
              Contribute on GitHub
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>
</NebulaBackground>

<!-- Footer is in the layout -->

<style>
  /* Removed full viewport nebula background - now using NebulaBackground component */
  
  /* Hero section styling */
  .hero-section {
    position: relative;
    padding-top: 0;
    z-index: 1;
    margin-top: 0;
  }
  
  /* Content section styling - make these sections stand out against the nebula */
  .content-section {
    position: relative;
    z-index: 1;
  }
  
  /* Remove bg-dark from sections since we have the nebula background */
  :global(.bg-dark) {
    background-color: transparent !important;
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
  
  /* Founder section */
  .founder-card {
    background-color: var(--hz-color-surface);
    border-radius: 12px;
    border: 1px solid var(--hz-color-border);
  }
  
  .founder-intro {
    font-size: 1.1rem;
    line-height: 1.6;
  }
  
  blockquote {
    border-left: 4px solid var(--hz-color-primary-green);
    background-color: rgba(102, 154, 115, 0.1);
    border-radius: 8px;
  }
  
  /* Feature cards */
  .feature-card {
    background-color: var(--hz-color-surface);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid var(--hz-color-border);
  }
  
  .feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  }
  
  .feature-title {
    font-weight: 600;
    font-size: 1.25rem;
    color: #f8f9fa;
    margin-bottom: 1rem;
  }
  
  .feature-description {
    color: #d7dadd;
  }
  
  /* Timeline section */
  .timeline-container {
    position: relative;
    padding: 2rem 0;
  }
  
  .timeline-container::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 80px;
    width: 2px;
    background-color: var(--hz-color-border);
  }
  
  .timeline-item {
    position: relative;
    margin-bottom: 2rem;
    padding-left: 120px;
  }
  
  .timeline-item:last-child {
    margin-bottom: 0;
  }
  
  .timeline-marker {
    position: absolute;
    left: 73px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: var(--hz-color-primary-green);
    box-shadow: 0 0 0 4px rgba(102, 154, 115, 0.3);
    transform: translateX(-50%);
    z-index: 1;
  }
  
  .timeline-content {
    background-color: var(--hz-color-surface);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid var(--hz-color-border);
  }
  
  .timeline-date {
    display: inline-block;
    font-weight: 600;
    color: var(--hz-color-primary-green);
    margin-bottom: 0.5rem;
  }
  
  .timeline-title {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }
  
  .timeline-description {
    color: var(--hz-color-text-secondary);
  }
  
  .timeline-item.future .timeline-marker {
    background-color: var(--hz-color-accent-lavender);
    box-shadow: 0 0 0 4px rgba(208, 192, 232, 0.3);
  }
  
  /* Contribute section */
  .contribute-card {
    background-color: var(--hz-color-surface);
    border-radius: 12px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
  
  /* Alien avatars styling */
  .alien-avatars-container {
    margin: 1rem auto;
    position: relative;
  }
  
  .alien-avatars-container img {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .alien-avatars-container img:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 32px rgba(208, 192, 232, 0.4);
  }
  
  /* Footer styles moved to layout */

  /* Media queries for responsive design */
  @media (max-width: 768px) {
    .timeline-container::before {
      left: 40px;
    }
    
    .timeline-item {
      padding-left: 80px;
    }
    
    .timeline-marker {
      left: 33px;
    }
  }
</style>