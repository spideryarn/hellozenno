<script lang="ts">
  /**
   * Email address to contact
   */
  import { CONTACT_EMAIL } from '$lib/config';
  export let email: string = CONTACT_EMAIL;
  
  /**
   * Subject line for the email
   * @default 'Hello Zenno Feedback'
   */
  export let subject: string = 'Hello Zenno Feedback';
  
  /**
   * Body content for the email
   * @default ''
   */
  export let body: string = '';
  
  /**
   * CSS class name(s) to apply to the button
   * @default ''
   */
  export let className: string = '';
  
  /**
   * Icon class to use (Phosphor icon)
   * @default 'ph-envelope'
   */
  export let icon: string = 'ph-envelope';
  
  /**
   * Button text
   * @default 'Contact Us'
   */
  export let text: string = 'Contact Us';
  
  /**
   * Show as a button (true) or a card with image (false)
   * @default true
   */
  export let asButton: boolean = true;
  
  /**
   * Image source for card mode
   * @default '/img/email_contact_envelope.png'
   */
  export let imageSrc: string = '/img/email_contact_envelope.png';
  
  /**
   * Image alt text for card mode
   * @default 'Report this issue via email'
   */
  export let imageAlt: string = 'Report this issue via email';
  
  /**
   * Caption text for card mode
   * @default 'Report via Email'
   */
  export let caption: string = 'Report via Email';
  
  /**
   * Generate the mailto URL with encoded subject and body
   */
  $: mailtoUrl = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
</script>

{#if asButton}
  <a href={mailtoUrl} class="btn {className}" target="_blank" rel="noopener noreferrer">
    <i class="{icon} me-2"></i>{text}
  </a>
{:else}
  <a 
    href={mailtoUrl}
    class="report-link"
    title="Email us"
  >
    <img 
      src={imageSrc} 
      alt={imageAlt} 
      class="report-image email-image" 
      width="150"
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
  
  .email-image {
    width: 150px;
  }
  
  .report-caption {
    font-size: 1rem;
    font-weight: 500;
  }
</style>