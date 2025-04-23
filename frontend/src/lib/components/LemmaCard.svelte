<script lang="ts">
  import { Card } from '$lib';
  import type { Lemma } from '$lib/types';
  
  export let lemma: Lemma;
  export let target_language_code: string;
  export let showDetails: boolean = false;
</script>

<Card>
  <div class="lemma-card">
    <h3 class="fs-5 mb-1">
      <a href="/language/{target_language_code}/lemma/{lemma.lemma}" class="hz-foreign-text text-decoration-none">
        {lemma.lemma}
      </a>
    </h3>
    <p class="text-muted small mb-1">{lemma.part_of_speech || 'Unknown'}</p>
    <p class="mb-2">{lemma.translations?.join(', ') || 'No translation'}</p>
    
    {#if lemma.commonality !== null && lemma.commonality !== undefined}
      <div class="progress mb-2" style="height: 6px;">
        <div class="progress-bar" role="progressbar" 
          style="width: {Math.round(lemma.commonality * 100)}%;" 
          aria-valuenow={Math.round(lemma.commonality * 100)} 
          aria-valuemin="0" 
          aria-valuemax="100">
        </div>
      </div>
      <p class="small text-muted mb-0">Commonality: {Math.round(lemma.commonality * 100)}%</p>
    {/if}
    
    {#if showDetails}
      {#if lemma.guessability !== null && lemma.guessability !== undefined}
        <p class="small text-muted mb-0">Guessability: {Math.round(lemma.guessability * 100)}%</p>
      {/if}
      
      {#if lemma.etymology}
        <div class="mt-2">
          <p class="small mb-0"><strong>Etymology:</strong> {lemma.etymology}</p>
        </div>
      {/if}
      
      {#if lemma.register}
        <div class="mt-2">
          <p class="small mb-0"><strong>Register:</strong> {lemma.register}</p>
        </div>
      {/if}
    {/if}
  </div>
</Card>

<style>
  .lemma-card {
    padding: 0.25rem;
  }
</style> 