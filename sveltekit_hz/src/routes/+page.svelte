<script lang="ts">
  // Home page component
</script>

<div class="home-container">
  <h1>Hello Zenno</h1>
  <p class="tagline">Learn foreign words with a magical AI dictionary</p>
  
  <div class="features">
    <div class="feature-card">
      <h2>Explore Languages</h2>
      <p>Browse our collection of languages and start learning vocabulary today.</p>
      <a href="/languages" class="button">View Languages</a>
    </div>
    
    {#if false /* This feature will be implemented later */}
    <div class="feature-card">
      <h2>Flashcards</h2>
      <p>Practice vocabulary with our flashcard system.</p>
      <a href="#" class="button disabled">Coming Soon</a>
    </div>
    {/if}
  </div>
  
  <div class="status-info">
    <h3>SvelteKit Port Status</h3>
    <ul>
      <li>✅ Languages list page</li>
      <li>✅ Sentence viewer component</li>
      <li>⏳ More components coming soon</li>
    </ul>
  </div>
</div>

<style>
  .home-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    text-align: center;
  }
  
  h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
  }
  
  .tagline {
    font-size: 1.25rem;
    color: #666;
    margin-bottom: 3rem;
  }
  
  .features {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    margin-top: 2rem;
  }
  
  .feature-card {
    background-color: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    max-width: 400px;
    width: 100%;
  }
  
  .button {
    display: inline-block;
    margin-top: 1.5rem;
    padding: 0.75rem 1.5rem;
    background-color: #4a4a4a;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-weight: bold;
    transition: background-color 0.2s;
  }
  
  .button:hover {
    background-color: #333;
  }
  
  .button.disabled {
    background-color: #999;
    cursor: not-allowed;
  }
  
  .status-info {
    margin-top: 4rem;
    padding: 1.5rem;
    background-color: #f0f0f0;
    border-radius: 8px;
    text-align: left;
  }
  
  .status-info h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .status-info ul {
    list-style-type: none;
    padding-left: 0.5rem;
  }
  
  .status-info li {
    margin-bottom: 0.5rem;
  }
</style>
