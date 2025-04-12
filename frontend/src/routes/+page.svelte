<script lang="ts">
  // Home page component
</script>

<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-lg-8 text-center">
      <h1 class="display-4 fw-bold mb-3">Hello Zenno</h1>
      <p class="lead mb-5 text-white-50">Learn foreign words with a magical AI dictionary</p>
      
      <div class="card bg-gradient p-4 mb-5 border-0 shadow">
        <section>
          <h2 class="hz-section-header fw-bold">Explore Languages</h2>
          <p class="mb-4">Browse our collection of languages and start learning vocabulary today.</p>
          <a href="/languages" class="btn btn-primary btn-lg px-4 shadow-sm">View Languages</a>
        </section>
      </div>
      
      <div class="card p-4 mt-4 bg-dark border-secondary">
        <section>
          <h3 class="hz-section-header mb-4">Key Benefits</h3>
          <ul class="list-group list-group-flush text-start">
            <li class="list-group-item bg-transparent border-secondary d-flex align-items-center">
              <span class="text-success me-2">✓</span> 
              <span>AI-generated dictionary entries with rich metadata</span>
            </li>
            <li class="list-group-item bg-transparent border-secondary d-flex align-items-center">
              <span class="text-success me-2">✓</span> 
              <span>Interactive hover explanations for unfamiliar words</span>
            </li>
            <li class="list-group-item bg-transparent border-secondary d-flex align-items-center">
              <span class="text-success me-2">✓</span> 
              <span>Audio dictation exercises with words in different contexts</span>
            </li>
            <li class="list-group-item bg-transparent border-secondary d-flex align-items-center">
              <span class="text-success me-2">✓</span> 
              <span>Support for vocabulary acquisition through contextual learning</span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</div>

<style>
  .bg-gradient {
    background: linear-gradient(145deg, var(--bs-card-bg) 0%, #252525 100%);
  }
  
  .card {
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
  }
  
  .btn-primary {
    background-color: var(--bs-primary);
    border-color: var(--bs-primary);
    transition: all 0.2s;
  }
  
  .btn-primary:hover {
    background-color: #3d8c42;
    border-color: #3d8c42;
    transform: translateY(-1px);
  }
</style>
