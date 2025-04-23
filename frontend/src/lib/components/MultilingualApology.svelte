<script lang="ts">
  /**
   * CSS class name(s) to apply to the container
   * @default ''
   */
  export let className: string = '';
  
  /**
   * Number of apologies to display
   * @default 8
   */
  export let count: number = 8;
  
  // Collection of apologies in different languages
  const apologies = [
    { language: 'English', text: 'Sorry', code: 'en' },
    { language: 'Spanish', text: 'Lo siento', code: 'es' },
    { language: 'French', text: 'Désolé', code: 'fr' },
    { language: 'German', text: 'Entschuldigung', code: 'de' },
    { language: 'Japanese', text: 'すみません', code: 'ja' },
    { language: 'Arabic', text: 'آسف', code: 'ar' },
    { language: 'Chinese', text: '对不起', code: 'zh' },
    { language: 'Russian', text: 'Извините', code: 'ru' },
    { language: 'Hindi', text: 'क्षमा करें', code: 'hi' },
    { language: 'Greek', text: 'Συγνώμη', code: 'el' },
    { language: 'Korean', text: '죄송합니다', code: 'ko' },
    { language: 'Italian', text: 'Mi dispiace', code: 'it' },
    { language: 'Portuguese', text: 'Desculpe', code: 'pt' },
    { language: 'Turkish', text: 'Özür dilerim', code: 'tr' },
    { language: 'Dutch', text: 'Sorry', code: 'nl' },
    { language: 'Swedish', text: 'Förlåt', code: 'sv' },
    { language: 'Finnish', text: 'Anteeksi', code: 'fi' },
    { language: 'Ukrainian', text: 'Вибачте', code: 'uk' },
    { language: 'Polish', text: 'Przepraszam', code: 'pl' },
    { language: 'Thai', text: 'ขอโทษ', code: 'th' }
  ];
  
  // Always include English first, then randomly select the rest
  const english = apologies.find(a => a.code === 'en');
  const otherLanguages = apologies.filter(a => a.code !== 'en');
  
  // Randomly select count-1 languages (since English is always included)
  const randomLanguages = [...otherLanguages]
    .sort(() => 0.5 - Math.random())
    .slice(0, count - 1);
  
  // Combine English with random languages  
  const selectedApologies = [english, ...randomLanguages];
</script>

<div class={`multilingual-apology ${className}`}>
  {#each selectedApologies as apology, i}
    <span 
      class={`apology-item ${apology.code !== 'en' ? 'hz-foreign-text' : ''}`} 
      lang={apology.code} 
      title={apology.language}
    >
      {apology.text}
    </span>
    {#if i < selectedApologies.length - 1}
      <span class="apology-separator">·</span>
    {/if}
  {/each}
</div>

<style>
  .multilingual-apology {
    margin: 1rem 0;
    font-size: 1.1rem;
    text-align: center;
    color: var(--hz-color-text-secondary);
    line-height: 1.8;
  }
  
  .apology-item {
    display: inline-block;
    transition: all 0.2s ease;
  }
  
  .apology-item:hover {
    color: var(--hz-color-text-main);
    transform: scale(1.05);
  }
  
  .apology-separator {
    display: inline-block;
    margin: 0 0.6rem;
    opacity: 0.6;
  }
</style>