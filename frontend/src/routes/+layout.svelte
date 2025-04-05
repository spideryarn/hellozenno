<script lang="ts">
  // Import any common components or global styles here
</script>

<style>
  .logo-image {
    height: 40px;
    transform: rotate(0deg) scale(1);
    transform-origin: center bottom;
  }
  
  @keyframes waggle {
    0% { transform: rotate(0deg) scale(1); }
    15% { transform: rotate(-8deg) scale(1.1); }
    30% { transform: rotate(8deg) scale(1.1); }
    45% { transform: rotate(-8deg) scale(1.1); }
    60% { transform: rotate(8deg) scale(1.1); }
    75% { transform: rotate(-5deg) scale(1.08); }
    90% { transform: rotate(3deg) scale(1.05); }
    100% { transform: rotate(0deg) scale(1.05); }
  }
  
  .logo-image:hover {
    animation: waggle 0.9s ease-in-out forwards;
    transform-origin: center bottom;
  }
  
  @media (max-width: 576px) {
    .logo-image {
      height: 36px;
    }
  }
</style>

<div class="d-flex flex-column min-vh-100">
  <header class="bg-dark py-3">
    <nav class="container">
      <div class="d-flex justify-content-between align-items-center">
        <a href="/" class="text-decoration-none" title="Hello Zenno">
          <img src="/logo.png" alt="Hello Zenno" class="logo-image" />
        </a>
        <div>
          <a href="/languages" class="text-decoration-none text-white ms-3">Languages</a>
        </div>
      </div>
    </nav>
  </header>
  
  <main class="flex-grow-1 py-4">
    <slot />
  </main>
  
  <footer class="bg-dark py-3 text-center text-white-50">
    <div class="container">
      <p class="mb-0">Hello Zenno - Learn foreign words with a magical AI dictionary</p>
    </div>
  </footer>
</div>

<!-- Remove the global style as it's now in our CSS files --> 