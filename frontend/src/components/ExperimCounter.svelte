<!-- Define the props -->
<script lang="ts">
  export let initialCount: number = 0;
  export let buttonText: string = "Increment";
  
  let count = initialCount;
  
  function increment() {
    count += 1;
  }
</script>

<!-- Component template -->
<div class="experim-counter">
  <h2>Interactive Counter</h2>
  <p>Current count: <span class="count">{count}</span></p>
  <button on:click={increment} class="counter-button">{buttonText}</button>
</div>

<!-- Component styles -->
<style>
  .experim-counter {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  h2 {
    color: #4a6ee0;
    margin-top: 0;
    margin-bottom: 1rem;
  }

  p {
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
  }

  .count {
    font-weight: bold;
    font-size: 1.5rem;
    color: #4a6ee0;
  }

  .counter-button {
    background-color: #4a6ee0;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .counter-button:hover {
    background-color: #3a5bbf;
  }
</style> 