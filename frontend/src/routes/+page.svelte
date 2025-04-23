<script lang="ts">
  // Home page component
</script>

<svelte:head>
  <title>Hello Zenno - AI Language Learning Assistant</title>
</svelte:head>

<!-- Hero section with nebula background -->
<section class="hero-section">
  <div class="container-fluid px-0">
    <div class="nebula-bg">
      <div class="container py-5">
        <div class="row justify-content-center">
          <div class="col-12 text-center">
            <!-- Animated logo -->
            <div class="logo-container mb-4">
              <img src="/logo.png" alt="Hello Zenno logo" class="logo animate-float" />
            </div>
            
            <!-- Main headline -->
            <h1 class="display-3 fw-bold mb-3 hero-title">
              Read, <span class="text-mint">hear</span> & <strong>remember</strong><br/>
              real‑world language without getting stuck
            </h1>
            
            <!-- Subheadline -->
            <p class="lead mb-5 subtitle">
              A friendly AI reading & listening toolkit for intermediate learners
            </p>
            
            <!-- CTA Button -->
            <a href="/languages" class="btn btn-primary btn-lg px-5 py-3 rounded-pill cta-button mb-5 fw-semibold">
              Try Hello Zenno
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Problem/Insight section -->
<section class="py-5 bg-dark">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8 text-center">
        <h2 class="section-title mb-4">Why so many of us stall at the intermediate plateau</h2>
        <div class="text-center mb-4">
          <img src="/img/marketing/lost in translation.png" alt="Lost in translation" class="problem-img img-fluid rounded mb-4" style="max-width: 70%;" />
        </div>
        <p class="section-text mb-5">
          Once the beginner courses end, native texts feel overwhelming and listening races ahead of our ears. 
          Hello Zenno gives you gentle "crutches" so you can glide through articles, novels or podcasts and keep the momentum.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- How it works section -->
<section class="py-5">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8 text-center">
        <h2 class="section-title mb-4">How it works</h2>
        
        <div class="row mb-5">
          <div class="col-md-4 mb-4">
            <div class="feature-card">
              <div class="feature-number">1</div>
              <img src="/img/marketing/import_text.png" alt="Import text" class="feature-img mb-3" />
              <h3 class="feature-title">Import any text or audio</h3>
              <p class="feature-description">Paste a URL, upload a photo/PDF or drop an MP3.</p>
            </div>
          </div>
          
          <div class="col-md-4 mb-4">
            <div class="feature-card">
              <div class="feature-number">2</div>
              <img src="/img/marketing/word_highlighting.png" alt="Word highlighting" class="feature-img mb-3" />
              <h3 class="feature-title">Zenno flags tricky words</h3>
              <p class="feature-description">An AI model predicts which words might trip you up and builds rich dictionary entries.</p>
            </div>
          </div>
          
          <div class="col-md-4 mb-4">
            <div class="feature-card">
              <div class="feature-number">3</div>
              <img src="/img/marketing/audio_training1.png" alt="Audio training" class="feature-img mb-3" />
              <h3 class="feature-title">Train your ears</h3>
              <p class="feature-description">Auto‑generated sentences and natural‑sounding audio help you recognise new words at speed.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Features section -->
<section class="py-5 bg-dark">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-10 text-center">
        <h2 class="section-title mb-4">Built for curious polyglots</h2>
        
        <div class="row align-items-center mb-5">
          <div class="col-md-6">
            <div class="language-globe-wrapper mb-4 mb-md-0">
              <img src="/img/marketing/language_selection_hero_globe.png" alt="Language selection globe" class="img-fluid rounded" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="row text-start">
              <div class="col-12 mb-4">
                <div class="feature-item">
                  <i class="ph-fill ph-book-open me-2 text-mint"></i>
                  <span class="feature-text">Context‑aware dictionary with etymology and mnemonics</span>
                </div>
              </div>
              
              <div class="col-12 mb-4">
                <div class="feature-item">
                  <i class="ph-fill ph-magnifying-glass me-2 text-mint"></i>
                  <span class="feature-text">Fuzzy bilingual search (typos welcome)</span>
                </div>
              </div>
              
              <div class="col-12 mb-4">
                <div class="feature-item">
                  <i class="ph-fill ph-translate me-2 text-mint"></i>
                  <span class="feature-text">30+ languages supported</span>
                </div>
              </div>
              
              <div class="col-12 mb-4">
                <div class="feature-item">
                  <i class="ph-fill ph-code me-2 text-mint"></i>
                  <span class="feature-text">Open‑source & free (login required for AI content)</span>
                </div>
              </div>
              
              <div class="col-12 mb-4">
                <div class="feature-item">
                  <i class="ph-fill ph-globe me-2 text-mint"></i>
                  <span class="feature-text">Web first – works on laptop or mobile browser</span>
                </div>
              </div>
              
              <div class="col-12 mb-4">
                <div class="feature-item">
                  <i class="ph-fill ph-brain me-2 text-mint"></i>
                  <span class="feature-text">Powered by Claude Sonnet 3.7 AI</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="alien-avatars-container text-center mt-5">
          <img src="/img/marketing/alien_avatars1.png" alt="Alien avatars" class="img-fluid rounded" style="max-width: 350px;" />
        </div>
        
        <p class="small text-white-50 mt-3">
          Missing your language? Drop us a line at <a href="mailto:hellozenno@gregdetre.com">hellozenno@gregdetre.com</a>
        </p>
      </div>
    </div>
  </div>
</section>

<!-- Getting started section -->
<section class="py-5">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-10 text-center">
        <h2 class="section-title mb-4">Get started in three minutes</h2>
        
        <div class="row align-items-center mb-5">
          <div class="col-lg-6 mb-4 mb-lg-0">
            <div class="card p-4 mb-4 getting-started-card">
              <div class="row">
                <div class="col-md-4 mb-3 mb-md-0 d-flex align-items-center justify-content-center">
                  <div class="getting-started-step">
                    <div class="step-number">1</div>
                    <div class="step-text">Sign up<br/>(completely free)</div>
                  </div>
                </div>
                
                <div class="col-md-4 mb-3 mb-md-0 d-flex align-items-center justify-content-center">
                  <div class="getting-started-step">
                    <div class="step-number">2</div>
                    <div class="step-text">Add a text or<br/>audio clip</div>
                  </div>
                </div>
                
                <div class="col-md-4 d-flex align-items-center justify-content-center">
                  <div class="getting-started-step">
                    <div class="step-number">3</div>
                    <div class="step-text">Hover, listen,<br/>keep reading</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-4">
              <a href="/auth" class="btn btn-primary btn-lg px-4 rounded-pill">Sign up now</a>
            </div>
          </div>
          
          <div class="col-lg-6">
            <div class="flashcard-screenshot-wrapper">
              <img src="/img/marketing/flashcard_screenshot.png" alt="Flashcard interface" class="img-fluid rounded shadow-lg" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Final note -->
<section class="py-5 bg-dark">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8 text-center">
        <div class="card p-4 mb-4 border-0 final-note-card">
          <h3 class="section-title mb-3">Looking for a full course?</h3>
          <p class="mb-0">
            Hello Zenno focuses on reading and listening in context. If you'd like a fuller language learning experience, 
            check out <a href="https://www.memrise.com" target="_blank" rel="noopener">Memrise</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="py-4">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8 text-center">
        <div class="footer-links">
          <a href="https://github.com/spideryarn/hellozenno" target="_blank" rel="noopener" class="footer-link">GitHub</a>
          <span class="footer-divider">·</span>
          <a href="/blog" class="footer-link">Blog</a>
          <span class="footer-divider">·</span>
          <a href="/privacy" class="footer-link">Privacy</a>
          <span class="footer-divider">·</span>
          <a href="/faq" class="footer-link">FAQ</a>
          <span class="footer-divider">·</span>
          <a href="mailto:hellozenno@gregdetre.com" class="footer-link">Contact</a>
        </div>
      </div>
    </div>
  </div>
</footer>

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
    padding: 100px 0;
    position: relative;
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
  
  .logo-container {
    position: relative;
    z-index: 2;
  }
  
  .logo {
    width: 80px;
    height: auto;
  }
  
  .animate-float {
    animation: float 3s ease-in-out infinite;
  }
  
  @keyframes float {
    0% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-10px);
    }
    100% {
      transform: translateY(0px);
    }
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
  
  .text-mint {
    color: #45C187;
  }
  
  .cta-button {
    position: relative;
    z-index: 2;
    background-color: #45C187;
    border-color: #45C187;
    box-shadow: 0 4px 12px rgba(69, 193, 135, 0.25);
    transition: all 0.3s ease;
  }
  
  .cta-button:hover {
    background-color: #60D3A0;
    border-color: #60D3A0;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(69, 193, 135, 0.35);
  }
  
  /* Section styling */
  .section-title {
    color: #45C187;
    font-weight: 700;
    margin-bottom: 1.5rem;
  }
  
  .section-text {
    font-size: 1.2rem;
    line-height: 1.6;
  }
  
  /* Feature cards */
  .feature-card {
    background-color: var(--bs-card-bg);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  }
  
  .feature-number {
    position: absolute;
    top: -10px;
    left: -10px;
    background-color: #45C187;
    color: white;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    box-shadow: 0 2px 8px rgba(69, 193, 135, 0.35);
  }
  
  .feature-img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }
  
  .feature-icon {
    color: #45C187;
  }
  
  .feature-title {
    font-weight: 600;
    font-size: 1.25rem;
    color: #f8f9fa;
  }
  
  .feature-description {
    color: #d7dadd;
  }
  
  /* Feature list */
  .feature-item {
    background-color: var(--bs-card-bg);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: transform 0.2s ease;
  }
  
  .feature-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }
  
  .feature-text {
    font-size: 1rem;
  }
  
  /* Getting started section */
  .getting-started-card {
    background-color: var(--bs-card-bg);
    border-radius: 12px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
  
  .getting-started-step {
    text-align: center;
  }
  
  .step-number {
    background-color: #45C187;
    color: white;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.5rem;
    margin: 0 auto 1rem;
    box-shadow: 0 2px 8px rgba(69, 193, 135, 0.35);
  }
  
  .step-text {
    font-weight: 500;
    line-height: 1.4;
  }
  
  /* Final note */
  .final-note-card {
    background-color: var(--bs-card-bg);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  
  /* Problem section */
  .problem-img {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(69, 193, 135, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .problem-img:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 24px rgba(69, 193, 135, 0.25);
  }
  
  /* Language globe styling */
  .language-globe-wrapper {
    position: relative;
  }
  
  .language-globe-wrapper img {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease;
  }
  
  .language-globe-wrapper img:hover {
    transform: rotate(5deg) scale(1.05);
  }
  
  /* Alien avatars styling */
  .alien-avatars-container {
    margin: 2rem auto;
    position: relative;
  }
  
  .alien-avatars-container img {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .alien-avatars-container img:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 32px rgba(198, 169, 240, 0.4);
  }
  
  /* Flashcard screenshot styling */
  .flashcard-screenshot-wrapper {
    position: relative;
    padding: 1rem;
  }
  
  .flashcard-screenshot-wrapper img {
    border: 1px solid rgba(69, 193, 135, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .flashcard-screenshot-wrapper img:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.3);
  }
  
  /* Footer */
  .footer-links {
    color: #6c757d;
    font-size: 0.9rem;
  }
  
  .footer-link {
    color: #6c757d;
    text-decoration: none;
    transition: color 0.2s;
    padding: 0 0.5rem;
  }
  
  .footer-link:hover {
    color: #45C187;
    text-decoration: underline;
  }
  
  .footer-divider {
    color: #6c757d;
  }
</style>