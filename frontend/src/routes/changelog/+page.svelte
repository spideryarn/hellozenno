<script lang="ts">
  import { page } from '$app/stores';
  import GithubIssueButton from '$lib/components/GithubIssueButton.svelte';
  import TableOfContents from '$lib/components/TableOfContents.svelte';
  import { onMount } from 'svelte';
  
  // Define the changelog data structure for Table of Contents
  const months = [
    {
      id: "april-2025",
      title: "April 2025",
      faqs: [
        { id: "april-2025-data-grid", question: "DataGrid & UI Improvements" },
        { id: "april-2025-profile", question: "User Profile Features" },
        { id: "april-2025-seo", question: "SEO & Analytics" }
      ]
    },
    {
      id: "march-2025",
      title: "March 2025",
      faqs: [
        { id: "march-2025-sveltekit", question: "SvelteKit Migration" },
        { id: "march-2025-auth", question: "Authentication & API Structure" },
        { id: "march-2025-features", question: "Flashcards & Translations" }
      ]
    },
    {
      id: "february-2025",
      title: "February 2025",
      faqs: [
        { id: "february-2025-database", question: "Database & Project Initialization" }
      ]
    }
  ];
  
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

  <!-- April 2025 Section -->
  <div id="april-2025" class="category-section">
    <h3 class="mt-5">April 2025</h3>
    
    <div id="april-2025-data-grid" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">DataGrid & UI Improvements</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Fix DataGrid sourcefile count display
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/948480c992bdc0ca2d58738a26f96dd0a6aa4520" target="_blank" rel="noopener noreferrer" title="948480c992bdc0ca2d58738a26f96dd0a6aa4520">948480</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Add changelog links throughout the application
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/75c2623f8b0e51c4a9c8d1234ebb4c52e0a56789" target="_blank" rel="noopener noreferrer" title="75c2623f8b0e51c4a9c8d1234ebb4c52e0a56789">75c262</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Update changelog page with GitHub issue button
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/8f28671d34b9f5ac82e6c7b9c3456a8f17b2e6c4" target="_blank" rel="noopener noreferrer" title="8f28671d34b9f5ac82e6c7b9c3456a8f17b2e6c4">8f2867</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Improve DataGrid with loading spinner on initial load
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/f3e6773b16f5d134bbb6289ed5befd9f58660568" target="_blank" rel="noopener noreferrer" title="f3e6773b16f5d134bbb6289ed5befd9f58660568">f3e677</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Improve DataGrid for sourcedirs page with better column naming
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/f906f880b1e9b0fc43d5926d4794486260e973e4" target="_blank" rel="noopener noreferrer" title="f906f880b1e9b0fc43d5926d4794486260e973e4">f906f8</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Show default sort with an arrow in column headers
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/9107a8588a2721fcfaa3748c09438ef2299679b6" target="_blank" rel="noopener noreferrer" title="9107a8588a2721fcfaa3748c09438ef2299679b6">9107a8</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Implement DataGrid for sourcedirs page
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/3bbe8a8516ae4ec6e25ca79113d704bc71b64fec" target="_blank" rel="noopener noreferrer" title="3bbe8a8516ae4ec6e25ca79113d704bc71b64fec">3bbe8a</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Add default sort to lemmas and phrases pages
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/50f3a1a" target="_blank" rel="noopener noreferrer" title="50f3a1a">50f3a1</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Add configurable default sorting options to DataGrid
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/5c31498" target="_blank" rel="noopener noreferrer" title="5c31498">5c3149</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Update sentences list to use DataGrid with newest sentences first
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/9ae1da3" target="_blank" rel="noopener noreferrer" title="9ae1da3">9ae1da</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Update phrases list to use DataGrid with hover tooltips
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/e732ffd" target="_blank" rel="noopener noreferrer" title="e732ffd">e732ff</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Add tooltip support to DataGrid with etymology information
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/2149d29" target="_blank" rel="noopener noreferrer" title="2149d29">2149d2</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Implement DataGrid for lemmas page with sorting and pagination
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/2065556" target="_blank" rel="noopener noreferrer" title="2065556">206555</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Make DataGrid headers less obtrusive
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/5fa4828" target="_blank" rel="noopener noreferrer" title="5fa4828">5fa482</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-23</span>
          Redesign DataGrid component with improved sorting
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/9c22fdd" target="_blank" rel="noopener noreferrer" title="9c22fdd">9c22fd</a></sup>
        </li>
      </ul>
    </div>
    
    <div id="april-2025-profile" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">User Profile Features</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Fix profile page URL error
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/05fc099b00f1257ac329ea30fd31799c4570ffdb" target="_blank" rel="noopener noreferrer" title="05fc099b00f1257ac329ea30fd31799c4570ffdb">05fc09</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Fix user email lookup for profiles
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/b2d7200" target="_blank" rel="noopener noreferrer" title="b2d7200">b2d720</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Improve user profile page layout
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/a94d57c" target="_blank" rel="noopener noreferrer" title="a94d57c">a94d57</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Add reusable DropdownButton component
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/3bcb67c" target="_blank" rel="noopener noreferrer" title="3bcb67c">3bcb67</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Add language-specific back button to profile page
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/c1484ae" target="_blank" rel="noopener noreferrer" title="c1484ae">c1484a</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Add user reference fields to database models
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/04632bd" target="_blank" rel="noopener noreferrer" title="04632bd">04632b</a></sup>
        </li>
      </ul>
    </div>
    
    <div id="april-2025-seo" class="subcategory-section">
      <h4 class="mt-4 mb-3 text-primary-green">SEO & Analytics</h4>
      <ul class="list-group">
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-27</span>
          Add Terms and Privacy policies
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/86f1f7e" target="_blank" rel="noopener noreferrer" title="86f1f7e">86f1f7</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Improve sitemap generation system
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/b82a037" target="_blank" rel="noopener noreferrer" title="b82a037">b82a03</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Add comprehensive sitemap generation
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/3852978" target="_blank" rel="noopener noreferrer" title="3852978">385297</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Add text-on-light class for better styling consistency
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/b30618d" target="_blank" rel="noopener noreferrer" title="b30618d">b30618</a></sup>
        </li>
        <li class="list-group-item">
          <span class="me-2 text-muted">2025-04-26</span>
          Add Google Analytics tracking
          <sup><a href="https://github.com/spideryarn/hellozenno/commit/51c7117" target="_blank" rel="noopener noreferrer" title="51c7117">51c711</a></sup>
        </li>
      </ul>
    </div>
  </div>

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