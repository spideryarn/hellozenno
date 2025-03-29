<script lang="ts">
  // Import any common components or global styles here
</script>

<div class="app">
  <header>
    <nav>
      <a href="/">Hello Zenno</a>
      <div class="nav-links">
        <a href="/languages">Languages</a>
      </div>
    </nav>
  </header>
  
  <main>
    <slot />
  </main>
  
  <footer>
    <p>Hello Zenno - Learn foreign words with a magical AI dictionary</p>
  </footer>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: #f9f9f9;
    color: #333;
  }
  
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  
  header {
    background-color: #4a4a4a;
    color: white;
    padding: 1rem;
  }
  
  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }
  
  nav a {
    color: white;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.2rem;
  }
  
  .nav-links a {
    margin-left: 1rem;
    font-size: 1rem;
  }
  
  main {
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    width: 100%;
    box-sizing: border-box;
  }
  
  footer {
    background-color: #4a4a4a;
    color: white;
    text-align: center;
    padding: 1rem;
    font-size: 0.8rem;
  }
</style> 