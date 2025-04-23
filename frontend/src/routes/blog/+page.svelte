<script lang="ts">
  import { onMount } from 'svelte';
  import NebulaBackground from '$lib/components/NebulaBackground.svelte';
  import { SITE_NAME } from '$lib/config';
  import type { PageData } from './$types';
  
  // Import Phosphor icons
  import Calendar from 'phosphor-svelte/lib/Calendar';
  import User from 'phosphor-svelte/lib/User';
  
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
  
  onMount(() => {
    // Add any initialization on mount if needed
  });
</script>

<svelte:head>
  <title>Blog | {SITE_NAME}</title>
  <meta name="description" content="The Hello Zenno blog - articles and updates about language learning, AI, and the Hello Zenno application." />
</svelte:head>

<NebulaBackground>
  <!-- Blog Header Section -->
  <section class="hero-section">
    <div class="container-fluid px-0">
      <div class="blog-header">
        <div class="container py-4">
          <div class="row justify-content-center">
            <div class="col-12 text-center">
              <h1 class="display-4 fw-bold mb-3 hero-title">
                Hello Zenno <span class="text-primary-green">Blog</span>
              </h1>
              <p class="lead mb-3 subtitle">
                Insights and updates on language learning with AI
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Blog Listing Section -->
  <section class="py-4">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          
          {#if data.posts.length > 0}
            <div class="blog-posts">
              {#each data.posts as post}
                <div class="blog-post-card">
                  <div class="row">
                    {#if post.coverImage}
                      <div class="col-md-4 mb-3 mb-md-0">
                        <a href="/blog/{post.slug}" class="blog-image-link">
                          <img src={post.coverImage} alt={post.title} class="blog-post-image img-fluid rounded" />
                        </a>
                      </div>
                    {/if}
                    
                    <div class="col-md-{post.coverImage ? '8' : '12'}">
                      <div class="post-meta mb-2">
                        <div class="post-meta-pills">
                          <span class="post-date">
                            <Calendar size={14} weight="fill" class="me-1" />
                            {formatDate(post.date)}
                          </span>
                          <span class="post-author">
                            <User size={14} weight="fill" class="me-1" />
                            {post.author}
                          </span>
                        </div>
                      </div>
                      
                      <h2 class="blog-post-title">
                        <a href="/blog/{post.slug}">{post.title}</a>
                      </h2>
                      
                      <p class="blog-post-excerpt">
                        {post.excerpt}
                      </p>
                      
                      <a href="/blog/{post.slug}" class="btn btn-outline-primary rounded-pill btn-sm px-3 py-2">
                        Read More
                      </a>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="card empty-state-card text-center p-5">
              <p class="mb-0">No blog posts available yet. Check back soon!</p>
            </div>
          {/if}
          
        </div>
      </div>
    </div>
  </section>
</NebulaBackground>

<style>
  /* Hero section styling */
  .hero-section {
    position: relative;
    padding-top: 0;
    z-index: 1;
    margin-top: 0;
  }
  
  .blog-header {
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
  
  /* Blog post card styling */
  .blog-posts {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .blog-post-card {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 12px;
    padding: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .blog-post-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    border-color: var(--hz-color-primary-green-dark);
  }
  
  .blog-post-title {
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  .blog-post-title a {
    color: var(--hz-color-text-main);
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .blog-post-title a:hover {
    color: var(--hz-color-primary-green);
  }
  
  .blog-post-excerpt {
    color: var(--hz-color-text-secondary);
    margin-bottom: 1rem;
    line-height: 1.6;
  }
  
  .post-meta {
    font-size: 0.85rem;
  }
  
  .post-meta-pills {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  
  .post-date, .post-author {
    display: inline-flex;
    align-items: center;
    color: var(--hz-color-text-secondary);
    background-color: rgba(var(--hz-color-background-rgb), 0.7);
    padding: 0.3rem 0.75rem;
    border-radius: 16px;
    border: 1px solid var(--hz-color-border);
    font-size: 0.8rem;
  }
  
  .blog-post-image {
    object-fit: cover;
    height: 100%;
    max-height: 180px;
    border-radius: 8px;
    transition: transform 0.3s ease;
  }
  
  .blog-image-link {
    display: block;
    overflow: hidden;
    border-radius: 8px;
    height: 100%;
  }
  
  .blog-image-link:hover .blog-post-image {
    transform: scale(1.05);
  }
  
  /* Empty state styling */
  .empty-state-card {
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 12px;
  }
  
  /* Media query for smaller screens */
  @media (max-width: 768px) {
    .blog-post-image {
      max-height: 200px;
      width: 100%;
    }
  }
</style>