<script lang="ts">
  /**
   * A reusable component for the nebula background that adds a space-themed backdrop 
   * to an entire page. Uses body::before and body::after pseudo-elements to create
   * a fixed background with a gradient overlay for a consistent cosmic effect.
   * 
   * The background is now standardised across the whole site.
   * No props are exported — every page gets the same nebula image,
   * fade‑to‑dark near the top, and 50 % overall visibility.
   */

  // Path to the single canonical nebula image
  const backgroundImageUrl = '/img/marketing/homepage_hero_background_nebula1.png';

  // Overall nebula visibility (0 = invisible, 1 = fully visible)
  const opacity = 0.6; // 60% visible, slightly fainter than before

  // Always fade to solid background colour at the very top (no configurables)
  const topGradient = `rgba(11, 11, 14, 1) 0%, rgba(11, 11, 14, 0.7) 5%`;

  // Derived overlay opacities
  const middleOpacity = 1 - opacity;
  const bottomOpacity = Math.min(middleOpacity + 0.1, 0.9);
</script>

<!-- Using a direct approach with local styles instead of global styles -->
<div class="nebula-wrapper">
  <!-- The background image layer -->
  <div
    class="nebula-bg-image"
    style:background-image={`url('${backgroundImageUrl}')`}
  ></div>
  
  <!-- The gradient overlay layer -->
  <div
    class="nebula-bg-overlay"
    style:background={`linear-gradient(
      to bottom,
      ${topGradient},
      rgba(11, 11, 14, ${middleOpacity}) 15%,
      rgba(11, 11, 14, ${middleOpacity}) 50%,
      rgba(11, 11, 14, ${bottomOpacity}) 100%
    )`}
  ></div>
  
  <!-- The content layer -->
  <div class="nebula-content">
    <slot />
  </div>
</div>

<style>
  .nebula-wrapper {
    position: relative;
    min-height: 100vh;
    width: 100%;
    overflow-x: hidden;
    /* Let the nebula image/overlay show; rely on overlay gradient + body background for base colour */
    background-color: transparent;
  }
  
  .nebula-bg-image {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-size: cover;
    background-position: center top;
    background-repeat: no-repeat;
    background-attachment: fixed;
    z-index: 0; /* Base layer */
  }
  
  .nebula-bg-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1; /* Between image and content */
  }
  
  .nebula-content {
    position: relative;
    z-index: 2; /* Above overlay */
    min-height: 100vh;
  }
</style>