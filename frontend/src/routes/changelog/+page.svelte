<script lang="ts">
  import GithubIssueButton from '$lib/components/GithubIssueButton.svelte';
  import TableOfContents from '$lib/components/TableOfContents.svelte';
  import { changelog } from '$lib/generated/changelog_data';
  
  // Build data for TableOfContents from generated changelog
  const months = changelog.map((month) => ({
    id: month.id,
    title: month.title,
    faqs: month.themes.map((theme) => ({ id: `${month.id}-${theme.id}`, question: theme.title }))
  }));
  
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Update URL to remove the fragment
    history.replaceState(null, document.title, window.location.pathname + window.location.search);
  }
</script>

<svelte:head>
  <title>Changelog | HelloZenno</title>
  <meta name="description" content="Latest improvements to HelloZenno" />
</svelte:head>

<div class="container my-5">
  <h1>Changelog</h1>
  <p class="lead">Latest improvements to HelloZenno, in reverse chronological order.</p>
  
  <div class="mb-4">
    <GithubIssueButton 
      asButton={false}
      url="https://github.com/spideryarn/hellozenno/commits/main/"
      caption="View all commits on GitHub"
    ></GithubIssueButton>
  </div>
  
  <!-- Table of Contents -->
  <TableOfContents categories={months} title="Jump to Month" />

  {#each changelog as month (month.id)}
    <div id={month.id} class="category-section">
      <h3 class="mt-5">{month.title}</h3>

      {#each month.themes as theme (theme.id)}
        <div id={`${month.id}-${theme.id}`} class="subcategory-section">
          <h4 class="mt-4 mb-3 text-primary-green">{theme.title}</h4>
          <ul class="list-group">
            {#each theme.entries as entry (entry.sha)}
              <li class="list-group-item">
                <span class="me-2 text-muted">{entry.date}</span>
                {entry.text}
                <sup>
                  <a
                    href={`https://github.com/spideryarn/hellozenno/commit/${entry.sha}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={entry.sha}
                  >
                    {entry.sha.slice(0, 7)}
                  </a>
                </sup>
              </li>
            {/each}
          </ul>
        </div>
      {/each}
    </div>
  {/each}

  <!-- March 2025 Section -->
  <div id="march-2025" class="category-section">
    <h3 class="mt-5">March 2025</h3>
    
    <div id="march-2025-sveltekit" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">SvelteKit Migration</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-03-31</span>
          Deploy frontend to Vercel for improved performance
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/fa3ae8b" target="_blank" rel="noopener noreferrer" title="fa3ae8b">fa3ae8</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-03-30</span>
          Migrate frontend to SvelteKit
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/ed1c3c6" target="_blank" rel="noopener noreferrer" title="ed1c3c6">ed1c3c</a></sup>
        </li>
      </ul>
    </div>
    
    <div id="march-2025-auth" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">Authentication & API Structure</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-03-17</span>
          Add standardized API URL structure
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/f2c4b8b" target="_blank" rel="noopener noreferrer" title="f2c4b8b">f2c4b8</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-03-16</span>
          Integrate Supabase Authentication
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/dd50d4c" target="_blank" rel="noopener noreferrer" title="dd50d4c">dd50d4</a></sup>
        </li>
      </ul>
    </div>
    
    <div id="march-2025-features" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">Flashcards & Translations</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-03-15</span>
          Add sentence flashcards using Svelte components
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/eac15d5" target="_blank" rel="noopener noreferrer" title="eac15d5">eac15d</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-03-15</span>
          Add literal translations to phrases
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/c3fef98" target="_blank" rel="noopener noreferrer" title="c3fef98">c3fef9</a></sup>
        </li>
      </ul>
    </div>
  </div>

  <!-- February 2025 Section -->
  <div id="february-2025" class="category-section">
    <h3 class="mt-5">February 2025</h3>
    
    <div id="february-2025-database" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">Database & Project Initialization</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-02-24</span>
          Fix accent normalization and diacritic handling
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/e11f0f5" target="_blank" rel="noopener noreferrer" title="e11f0f5">e11f0f</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-02-16</span>
          Migrate database to Supabase
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/a8fdab1" target="_blank" rel="noopener noreferrer" title="a8fdab1">a8fdab</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-02-08</span>
          Project initialization with basic architecture and database schema
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/9ee7d82" target="_blank" rel="noopener noreferrer" title="9ee7d82">9ee7d8</a></sup>
        </li>
      </ul>
    </div>
  </div>
</div>

<style>
  .category-section {
    margin-bottom: 2rem;
    scroll-margin-top: 80px;
  }
  
  .subcategory-section {
    margin-bottom: 1.5rem;
    scroll-margin-top: 100px;
  }
  
  .text-primary-green {
    color: var(--hz-color-primary-green);
  }
  
  sup a {
    text-decoration: none;
    color: var(--bs-secondary);
    font-size: 0.7em;
    margin-left: 0.5em;
  }

  sup a:hover {
    text-decoration: underline;
  }
</style>