<script lang="ts">
  // Accept either categories-based structure (for FAQ) or flat items (for blog posts)
  export let categories = null;
  export let items = null;
  export let title = "";
</script>

<div class="card toc-card mb-4 p-4">
  <h2 class="h4 mb-3">{title}</h2>
  <div class="categories-toc">
    {#if categories}
      <!-- FAQ-style categories -->
      {#each categories as category}
        <div class="category-section mb-3">
          <h3 class="h5 mb-2">{category.title}</h3>
          <ul class="toc-list">
            {#each category.faqs as item}
              <li>
                <a href="#{item.id}" class="toc-link">
                  {item.question || item.title}
                </a>
              </li>
            {/each}
          </ul>
        </div>
      {/each}
    {:else if items}
      <!-- Flat items (for blog posts) -->
      <div class="category-section mb-3">
        <ul class="toc-list">
          {#each items as item}
            <li>
              <a href="#{item.id}" class="toc-link">
                {item.title}
              </a>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
</div>

<style>
  /* Table of Contents styling */
  .toc-card {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 8px;
  }

  .categories-toc {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    grid-gap: 1.5rem;
  }

  .category-section h3 {
    color: var(--hz-color-primary-green);
    border-bottom: 1px solid var(--hz-color-border);
    padding-bottom: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .toc-list {
    list-style-type: none;
    padding-left: 0;
    margin-bottom: 0;
  }

  .toc-list li {
    margin-bottom: 0.5rem;
  }

  .toc-link {
    color: var(--hz-color-text);
    text-decoration: none;
    transition: all 0.2s ease;
    display: inline-block;
    padding: 0.25rem 0;
    font-size: 0.9rem;
  }

  .toc-link:hover {
    color: var(--hz-color-primary-green);
    text-decoration: underline;
    opacity: 0.8;
    transform: translateX(3px);
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .categories-toc {
      grid-template-columns: 1fr;
      grid-gap: 1rem;
    }
  }
</style>