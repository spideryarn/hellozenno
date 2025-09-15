<script lang="ts">
  import { SITE_NAME } from '$lib/config';
</script>

<svelte:head>
  <title>Admin · {SITE_NAME}</title>
  <meta name="robots" content="noindex,nofollow" />
  <meta name="description" content="Administration area" />
</svelte:head>

<div class="container">
  <h1 class="h3 mb-4">Admin</h1>
  <div class="list-group">
    <a href="/admin/users" class="list-group-item list-group-item-action">Users</a>
  </div>
</div>


