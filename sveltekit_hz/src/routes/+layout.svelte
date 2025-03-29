<script lang="ts">
  // Import any common components or global styles here
</script>

<div class="d-flex flex-column min-vh-100">
  <header class="bg-dark py-3">
    <nav class="container">
      <div class="d-flex justify-content-between align-items-center">
        <a href="/" class="text-decoration-none text-white fs-4 fw-bold">Hello Zenno</a>
        <div>
          <a href="/languages" class="text-decoration-none text-white ms-3">Languages</a>
        </div>
      </div>
    </nav>
  </header>
  
  <main class="flex-grow-1 py-4">
    <div class="container">
      <slot />
    </div>
  </main>
  
  <footer class="bg-dark py-3 text-center text-white-50">
    <div class="container">
      <p class="mb-0">Hello Zenno - Learn foreign words with a magical AI dictionary</p>
    </div>
  </footer>
</div>

<!-- Remove the global style as it's now in our CSS files --> 