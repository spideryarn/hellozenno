# Animation Guidelines

This document outlines animation patterns and best practices for the Hello Zenno application.

For general visual design, see [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md).

## Core Principles

Use subtle animations to enhance user experience without being distracting:

1. **Purpose**: Every animation should have a clear purpose
2. **Performance**: Animations should be smooth and performant
3. **Accessibility**: Provide options to reduce motion
4. **Consistency**: Use consistent timing and easing functions

## Standard Animations

### Floating Animation

Used for logo and key branding elements:

```css
.animate-float {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
```

Usage:
```svelte
<img src="/img/logo.png" alt="Hello Zenno" class="animate-float" />
```

### Hover Effects

#### Cards

Small scale and shadow changes on hover:

```css
.feature-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--hz-shadow-primary-green-lg);
}
```

#### Buttons

Color change, slight translation, and shadow enlargement:

```css
.btn-primary {
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: var(--hz-color-primary-green-light);
  transform: translateY(-1px);
  box-shadow: var(--hz-shadow-primary-green-lg);
}
```

## Transition Timing

Standard durations for different UI elements:

| Element Type | Duration | Easing Function |
|-------------|----------|----------------|
| Hover states | 0.2s | ease |
| Button interactions | 0.3s | ease |
| Modal/dropdown opening | 0.3s | ease-out |
| Page transitions | 0.4s | ease-in-out |
| Loading spinners | 1s | linear (infinite) |

## CSS Transitions

### Basic Transition

```css
.element {
  transition: property duration easing;
  /* Example: */
  transition: opacity 0.2s ease;
}
```

### Multiple Properties

```css
.element {
  transition: transform 0.2s ease, opacity 0.3s ease;
}
```

### All Properties

```css
.element {
  transition: all 0.3s ease;
}
```

## Svelte Transitions

### Built-in Transitions

```svelte
<script>
  import { fade, fly, slide } from 'svelte/transition';
  let visible = true;
</script>

<!-- Fade -->
{#if visible}
  <div transition:fade={{ duration: 300 }}>
    Fading content
  </div>
{/if}

<!-- Fly -->
{#if visible}
  <div transition:fly={{ x: -100, duration: 300 }}>
    Flying content
  </div>
{/if}

<!-- Slide -->
{#if visible}
  <div transition:slide={{ duration: 300 }}>
    Sliding content
  </div>
{/if}
```

### Custom Transitions

```svelte
<script>
  import { cubicOut } from 'svelte/easing';

  function customTransition(node, { duration = 300 }) {
    return {
      duration,
      css: (t) => {
        const eased = cubicOut(t);
        return `
          transform: scale(${eased});
          opacity: ${eased};
        `;
      }
    };
  }
</script>

{#if visible}
  <div transition:customTransition>
    Custom animation
  </div>
{/if}
```

## Loading States

### Loading Spinner

```svelte
<script>
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
</script>

<LoadingSpinner />
```

The spinner uses a continuous rotation animation:

```css
.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### Skeleton Screens

For content loading, consider skeleton screens with shimmer effects:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--hz-color-surface) 25%,
    var(--hz-color-border) 50%,
    var(--hz-color-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## Performance Considerations

### Hardware Acceleration

Use transform and opacity for smooth animations:

```css
/* Good - uses GPU acceleration */
.element {
  transform: translateX(100px);
  opacity: 0.5;
}

/* Avoid - causes reflow/repaint */
.element {
  left: 100px;
  width: 200px;
}
```

### will-change Property

Hint to the browser about properties that will animate:

```css
.element {
  will-change: transform, opacity;
}

/* Remove after animation */
.element:hover {
  will-change: auto;
}
```

## Accessibility

### Respecting User Preferences

Honor the prefers-reduced-motion media query:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### In Svelte Components

```svelte
<script>
  import { onMount } from 'svelte';

  let prefersReducedMotion = false;

  onMount(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    prefersReducedMotion = mediaQuery.matches;

    mediaQuery.addEventListener('change', (e) => {
      prefersReducedMotion = e.matches;
    });
  });
</script>

{#if !prefersReducedMotion}
  <div class="animate-float">Animated content</div>
{:else}
  <div>Static content</div>
{/if}
```

## Common Animation Patterns

### Expand/Collapse

For collapsible content:

```svelte
<script>
  import { slide } from 'svelte/transition';
  let isExpanded = false;
</script>

<button on:click={() => isExpanded = !isExpanded}>
  Toggle
</button>

{#if isExpanded}
  <div transition:slide={{ duration: 300 }}>
    Collapsible content
  </div>
{/if}
```

### Modal Entry/Exit

For modal dialogs:

```svelte
<script>
  import { fade, scale } from 'svelte/transition';
</script>

{#if showModal}
  <!-- Backdrop -->
  <div
    class="modal-backdrop"
    transition:fade={{ duration: 200 }}>
  </div>

  <!-- Modal -->
  <div
    class="modal"
    transition:scale={{ duration: 300, start: 0.9 }}>
    Modal content
  </div>
{/if}
```

### List Item Animations

For dynamic lists:

```svelte
<script>
  import { flip } from 'svelte/animate';
  import { fade } from 'svelte/transition';
</script>

{#each items as item (item.id)}
  <div
    animate:flip={{ duration: 300 }}
    transition:fade={{ duration: 200 }}>
    {item.name}
  </div>
{/each}
```

## Related Documentation

- [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) - Main styling guide
- [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) - UX patterns and interactions
- [ACCESSIBILITY.md](./ACCESSIBILITY.md) - Accessibility requirements for animations