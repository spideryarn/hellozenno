<script lang="ts">
  import { page } from '$app/stores';
  import GithubIssueButton from '$lib/components/GithubIssueButton.svelte';
</script>

<svelte:head>
  <title>Changelog | HelloZenno</title>
  <meta name="description" content="Latest improvements to HelloZenno" />
</svelte:head>

<div class="container my-5">
  <h1>Changelog</h1>
  <p class="lead">Latest improvements to HelloZenno, in reverse chronological order.</p>
  
  <div class="mb-4">
    <GithubIssueButton 
      asButton={false}
      url="https://github.com/spideryarn/hellozenno/issues"
      caption="Report an issue on GitHub"
    ></GithubIssueButton>
  </div>

  <ul class="list-group mt-4">
    <li class="list-group-item">
      <span class="me-2 text-muted">2025-04-27</span>
      Fix profile page URL error by using correct profile API route name
      <sup><a href="https://github.com/spideryarn/hellozenno/commit/05fc099b00f1257ac329ea30fd31799c4570ffdb" target="_blank" rel="noopener noreferrer" title="05fc099b00f1257ac329ea30fd31799c4570ffdb">05fc09</a></sup>
    </li>
    <li class="list-group-item">
      <span class="me-2 text-muted">2025-04-27</span>
      Improve DataGrid with loading spinner on initial load
      <sup><a href="https://github.com/spideryarn/hellozenno/commit/f3e6773b16f5d134bbb6289ed5befd9f58660568" target="_blank" rel="noopener noreferrer" title="f3e6773b16f5d134bbb6289ed5befd9f58660568">f3e677</a></sup>
    </li>
    <li class="list-group-item">
      <span class="me-2 text-muted">2025-04-27</span>
      Improve DataGrid for sourcedirs page
      <sup><a href="https://github.com/spideryarn/hellozenno/commit/f906f880b1e9b0fc43d5926d4794486260e973e4" target="_blank" rel="noopener noreferrer" title="f906f880b1e9b0fc43d5926d4794486260e973e4">f906f8</a></sup>
    </li>
    <li class="list-group-item">
      <span class="me-2 text-muted">2025-04-27</span>
      Show the default sort with an arrow in the column
      <sup><a href="https://github.com/spideryarn/hellozenno/commit/9107a8588a2721fcfaa3748c09438ef2299679b6" target="_blank" rel="noopener noreferrer" title="9107a8588a2721fcfaa3748c09438ef2299679b6">9107a8</a></sup>
    </li>
    <li class="list-group-item">
      <span class="me-2 text-muted">2025-04-27</span>
      Implement DataGrid for sourcedirs page
      <sup><a href="https://github.com/spideryarn/hellozenno/commit/3bbe8a8516ae4ec6e25ca79113d704bc71b64fec" target="_blank" rel="noopener noreferrer" title="3bbe8a8516ae4ec6e25ca79113d704bc71b64fec">3bbe8a</a></sup>
    </li>
    <li class="list-group-item">
      <span class="me-2 text-muted">2025-04-26</span>
      Terms and privacy policies
      <sup><a href="https://github.com/spideryarn/hellozenno/commit/86f1f7" target="_blank" rel="noopener noreferrer" title="86f1f7">86f1f7</a></sup>
    </li>
  </ul>
</div>

<style>
  sup a {
    text-decoration: none;
    color: var(--bs-secondary);
    font-size: 0.7em;
    margin-left: 0.5em;
  }

  sup a:hover {
    text-decoration: underline;
  }
</style> 