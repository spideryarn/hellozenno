<script lang="ts">
  /**
   * GitHub Issues URL
   */
  import { GITHUB_ISSUES_URL } from '$lib/config';
  export let url: string = GITHUB_ISSUES_URL;
  
  /**
   * Button text
   * @default 'Open GitHub Issue'
   */
  export let text: string = 'Open GitHub Issue';
  
  /**
   * CSS class name(s) to apply to the button
   * @default ''
   */
  export let className: string = '';
  
  /**
   * Icon class to use (Phosphor icon)
   * @default 'ph-github-logo'
   */
  export let icon: string = 'ph-github-logo';
  
  /**
   * Show as a button (true) or a card with image (false)
   * @default true
   */
  export let asButton: boolean = true;
  
  /**
   * Image source for card mode
   * @default '/img/extern/GitHub-logo.png'
   */
  export let imageSrc: string = '/img/extern/GitHub-logo.png';
  
  /**
   * Image alt text for card mode
   * @default 'Create a GitHub issue'
   */
  export let imageAlt: string = 'Create a GitHub issue';
  
  /**
   * Caption text for card mode
   * @default 'Open GitHub Issue'
   */
  export let caption: string = 'Open GitHub Issue';
</script>

{#if asButton}
  <a href={url} class="btn {className}" target="_blank" rel="noopener noreferrer">
    <i class="{icon} me-2"></i>{text}
  </a>
{:else}
  <a 
    href={url} 
    target="_blank" 
    rel="noopener noreferrer" 
    class="report-link"
    title="Create an issue on GitHub"
  >
    <img 
      src={imageSrc} 
      alt={imageAlt} 
      class="report-image github-image" 
      width="97"
      height="auto"
    />
    <span class="report-caption">{caption}</span>
  </a>
{/if}

<style>
  /* Card style (only applied when asButton=false) */
  .report-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: var(--hz-color-text-secondary);
    transition: all 0.3s ease;
    padding: 0.5rem;
    border-radius: 10px;
  }
  
  .report-link:hover {
    transform: translateY(-5px);
    color: var(--hz-color-text-main);
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  .report-image {
    max-width: 150px;
    border-radius: 8px;
    transition: all 0.3s ease;
    margin-bottom: 0.75rem;
  }
  
  .github-image {
    width: 80px;
    background-color: transparent;
    padding: 0;
    border-radius: 0;
  }
  
  .report-caption {
    font-size: 1rem;
    font-weight: 500;
  }
</style>