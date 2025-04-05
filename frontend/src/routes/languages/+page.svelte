<script lang="ts">
  import { onMount } from 'svelte';
  import type { PageData } from './$types';
  import Card from '$lib/components/Card.svelte';
  
  /** @type {import('./$types').PageData} */
  export let data: PageData;
  
  interface Language {
    name: string;
    code: string;
  }
  
  let languages: Language[] = data.languages;
  let searchQuery = '';
  let searchInput: HTMLInputElement;
  
  onMount(() => {
    // Focus on the search input when component mounts
    if (searchInput) {
      searchInput.focus();
    }
  });
  
  // Computed filtered languages based on searchQuery
  $: filteredLanguages = searchQuery.trim() 
    ? languages.filter(lang => 
        lang.name.toLowerCase().includes(searchQuery.toLowerCase().trim()) || 
        lang.code.toLowerCase().includes(searchQuery.toLowerCase().trim())
      )
    : languages;
  
  // Group languages alphabetically
  const alphabet = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'];
  
  // Computed language groups based on filtered languages
  $: languageGroups = (() => {
    const groups: Record<string, Language[]> = {};
    
    alphabet.forEach(letter => {
      const matches = filteredLanguages.filter(lang => 
        lang.name.toUpperCase().startsWith(letter)
      );
      if (matches.length > 0) {
        groups[letter] = matches;
      }
    });
    
    return groups;
  })();
  
  // Function to handle search form submission - the reactivity will automatically
  // update filteredLanguages and languageGroups
  function handleSearch() {}
  
  // Function to get a color for a language card based on the language code (deterministic)
  function getColorForLanguage(code: string): string {
    const colors = [
      '#4CAD53', // Primary green
      '#D97A27', // Secondary orange
      '#3F88C5', // Blue
      '#8C4799', // Purple
      '#E94F37', // Red
      '#44BBA4', // Teal
      '#F6AE2D'  // Yellow
    ];
    
    // Simple hash function to get a consistent color for each language
    const hashCode = code.split('').reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0);
    return colors[hashCode % colors.length];
  }
</script>

<svelte:head>
  <title>Available Languages | Hello Zenno</title>
</svelte:head>

<main class="container">
  <div class="hero-section">
    <div class="hero-content">
      <h1>Explore Languages</h1>
      <p class="subtitle">Discover and learn new languages with Hello Zenno's interactive tools</p>
      
      <div class="search-container">
        <form on:submit|preventDefault={handleSearch}>
          <input 
            type="text" 
            placeholder="Search languages..." 
            bind:value={searchQuery}
            bind:this={searchInput}
            class="search-input"
          />
          <button type="submit" class="search-icon" aria-label="Search">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </button>
        </form>
      </div>
      
      <div class="stats">
        <div class="stat-item">
          <span class="stat-number">{languages.length}</span>
          <span class="stat-label">Languages</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">1000+</span>
          <span class="stat-label">Sentences</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">24/7</span>
          <span class="stat-label">Learning</span>
        </div>
      </div>
    </div>
    <div class="hero-bg"></div>
  </div>
  
  {#if filteredLanguages.length === 0}
    <div class="no-results">
      <p>No languages found matching "{searchQuery}"</p>
      <button class="reset-search" on:click={() => searchQuery = ''}>Reset Search</button>
    </div>
  {:else}
    <div class="alphabet-nav">
      {#each Object.keys(languageGroups) as letter}
        <a href="#{letter}" class="letter-link">{letter}</a>
      {/each}
    </div>
    
    {#each Object.entries(languageGroups) as [letter, langs]}
      <div class="letter-group" id={letter}>
        <h2 class="letter-heading">
          <span class="letter-badge" style="background: linear-gradient(135deg, {getColorForLanguage(letter)}, {getColorForLanguage(letter+'1')})">
            {letter}
          </span>
        </h2>
        <div class="languages-grid">
          {#each langs as language}
            <Card 
              title={language.name}
              subtitle={language.code}
              linkUrl="/language/{language.code}/sources"
              className="language-card"
            >
              <div class="card-background-letter" style="color: {getColorForLanguage(language.code)};">
                {language.name.charAt(0)}
              </div>
            </Card>
          {/each}
        </div>
      </div>
    {/each}
  {/if}
</main>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }
  
  .hero-section {
    text-align: center;
    margin-bottom: 3rem;
    padding: 3rem 2rem;
    border-radius: 16px;
    position: relative;
    overflow: hidden;
    min-height: 300px;
  }
  
  .hero-content {
    position: relative;
    z-index: 2;
  }
  
  .hero-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(76, 173, 83, 0.15) 0%, rgba(217, 122, 39, 0.15) 100%);
    z-index: 1;
    overflow: hidden;
  }
  
  .hero-bg::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background-image: 
      radial-gradient(circle at 30% 30%, rgba(76, 173, 83, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 70% 70%, rgba(217, 122, 39, 0.08) 0%, transparent 50%);
    animation: rotate 60s linear infinite;
    z-index: -1;
  }
  
  @keyframes rotate {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  
  .hero-section h1 {
    font-size: 3.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    position: relative;
    z-index: 1;
    background: linear-gradient(135deg, #4CAD53 0%, #D97A27 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-fill-color: transparent;
    letter-spacing: -0.03em;
  }
  
  .subtitle {
    font-size: 1.3rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    position: relative;
    z-index: 1;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }
  
  .search-container {
    margin-bottom: 2rem;
    position: relative;
    z-index: 1;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
  }
  
  .search-input {
    width: 100%;
    padding: 1rem 3rem 1rem 1.5rem;
    border-radius: 50px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    background: rgba(18, 18, 18, 0.3);
    font-size: 1.1rem;
    color: var(--bs-body-color);
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  }
  
  .search-input:focus {
    outline: none;
    border-color: #4CAD53;
    box-shadow: 0 0 0 3px rgba(76, 173, 83, 0.3);
  }
  
  .search-icon {
    position: absolute;
    right: 1.2rem;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255, 255, 255, 0.5);
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }
  
  .search-icon:hover {
    color: rgba(255, 255, 255, 0.8);
  }
  
  form {
    position: relative;
    width: 100%;
  }
  
  .stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 2rem;
    position: relative;
    z-index: 1;
  }
  
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: rgba(0, 0, 0, 0.2);
    padding: 1rem 1.5rem;
    border-radius: 12px;
    min-width: 120px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    transition: transform 0.3s ease;
  }
  
  .stat-item:hover {
    transform: translateY(-5px);
  }
  
  .stat-number {
    font-size: 2.2rem;
    font-weight: bold;
    background: linear-gradient(135deg, #4CAD53 0%, #D97A27 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .stat-label {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-top: 0.3rem;
  }
  
  .alphabet-nav {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }
  
  .letter-link {
    display: inline-block;
    width: 2rem;
    height: 2rem;
    line-height: 2rem;
    text-align: center;
    border-radius: 6px;
    font-weight: 600;
    color: var(--bs-body-color);
    text-decoration: none;
    transition: all 0.2s ease;
    background: rgba(255, 255, 255, 0.05);
  }
  
  .letter-link:hover {
    background: rgba(76, 173, 83, 0.3);
    transform: scale(1.1);
    color: white;
  }
  
  .letter-group {
    margin-bottom: 3rem;
    scroll-margin-top: 2rem;
  }
  
  .letter-heading {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
  }
  
  .letter-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    height: 3rem;
    border-radius: 12px;
    color: white;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    margin-right: 1rem;
  }
  
  .languages-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
  }
  
  /* Card styling is managed in the Card component */
  
  .card-background-letter {
    position: absolute;
    right: -10px;
    bottom: -25px;
    font-size: 7rem;
    font-weight: bold;
    opacity: 0.2;
    z-index: 0;
    line-height: 0.8;
    transition: opacity 0.3s ease, transform 0.3s ease;
  }
  
  :global(.card:hover) .card-background-letter {
    opacity: 0.3;
    transform: scale(1.1);
  }
  
  .no-results {
    text-align: center;
    padding: 3rem;
    font-size: 1.2rem;
    opacity: 0.7;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    margin-top: 2rem;
  }
  
  .reset-search {
    background: linear-gradient(135deg, #4CAD53 0%, #D97A27 100%);
    color: white;
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 50px;
    font-weight: 600;
    margin-top: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .reset-search:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(76, 173, 83, 0.3);
  }
  
  @media (max-width: 768px) {
    .hero-section {
      padding: 2rem 1rem;
    }
    
    .hero-section h1 {
      font-size: 2.5rem;
    }
    
    .subtitle {
      font-size: 1.1rem;
    }
    
    .search-input {
      padding: 0.8rem 2.5rem 0.8rem 1.2rem;
      font-size: 1rem;
    }
    
    .search-icon {
      right: 1rem;
    }
    
    .stats {
      flex-wrap: wrap;
      gap: 1rem;
    }
    
    .stat-item {
      min-width: 100px;
      padding: 0.8rem 1rem;
    }
    
    .stat-number {
      font-size: 1.8rem;
    }
    
    .languages-grid {
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    }
    
    :global(.languages-grid .card) {
      height: 110px;
    }
    
    .card-background-letter {
      font-size: 6rem;
      right: -10px;
      bottom: -20px;
    }
    
    .letter-badge {
      width: 2.5rem;
      height: 2.5rem;
    }
  }
  
  @media (max-width: 480px) {
    .hero-section h1 {
      font-size: 2rem;
    }
    
    .languages-grid {
      grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      gap: 0.8rem;
    }
    
    :global(.languages-grid .card) {
      height: 100px;
    }
    
    .stat-item {
      flex: 1 0 calc(50% - 1rem);
    }
  }
</style> 