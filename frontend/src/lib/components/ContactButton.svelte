<script lang="ts">
  /**
   * Email address to contact
   */
  export let email: string = 'hellozenno@gregdetre.com';
  
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
   * Generate the mailto URL with encoded subject and body
   */
  $: mailtoUrl = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
</script>

<a href={mailtoUrl} class="btn {className}" target="_blank" rel="noopener noreferrer">
  <i class="{icon} me-2"></i>{text}
</a>