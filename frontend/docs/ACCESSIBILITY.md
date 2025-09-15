# Accessibility Guidelines

This document outlines accessibility requirements and best practices for the Hello Zenno application.

For visual design and styling, see [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md).

## Core Principles

1. **Perceivable**: Information must be presentable in ways users can perceive
2. **Operable**: Interface components must be operable by keyboard
3. **Understandable**: Information and UI operation must be understandable
4. **Robust**: Content must be robust enough for assistive technologies

## ARIA Attributes

### Elements with Event Handlers

Add appropriate ARIA roles to non-interactive elements that have event handlers:

```svelte
<!-- Clickable div needs role -->
<div role="button" on:click={handler} tabindex="0">
  Click me
</div>

<!-- Keyboard handler on non-interactive element -->
<div role="dialog" on:keydown={handler}>
  Dialog content
</div>
```

### Icon-Only Buttons

Always add an aria-label to buttons without visible text:

```svelte
<!-- Close button -->
<button class="btn-close" aria-label="Close"></button>

<!-- Icon button -->
<button aria-label="Delete item">
  <Trash size={16} />
</button>
```

### Modal Dialogs

Proper modal accessibility requires several attributes:

```svelte
<div
  role="dialog"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
  aria-modal="true">

  <h5 id="modal-title">Modal Title</h5>
  <p id="modal-description">Modal description text</p>

  <!-- Modal content -->
</div>
```

For modal keyboard shortcuts and user interaction patterns, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md#modal-dialogs).

## Focus Management

### Autofocus

When using autofocus, follow these guidelines:

1. Add a svelte-ignore comment to avoid accessibility warnings
2. Make autofocus configurable via props rather than hardcoded
3. Only use on the main content area, not in modals or popups

```svelte
<script>
  export let autoFocus = false;
</script>

<!-- svelte-ignore a11y-autofocus -->
<input
  type="text"
  autofocus={autoFocus}
  placeholder="Search..." />
```

For implementation patterns and best practices for autofocus, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md#input-focus).

### Focus Trapping

In modals and dropdowns, implement focus trapping to keep keyboard navigation within the component:

```svelte
<script>
  function handleKeydown(event) {
    if (event.key === 'Tab') {
      // Trap focus within modal
      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      // Handle tab cycling logic
    }
  }
</script>
```

## Color Contrast

### Text on Backgrounds

Ensure sufficient contrast ratios:
- Normal text: 4.5:1 minimum
- Large text (18pt+): 3:1 minimum
- Use `.text-on-light` class for dark text on light backgrounds

```svelte
<!-- Dark text on lavender background -->
<button class="btn btn-secondary text-on-light">
  Secondary Button
</button>
```

### Theme Variables

All colors are defined as CSS variables to support theming and ensure consistency. See [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md#theming) for the complete color palette.

## Keyboard Navigation

### Tab Order

Ensure logical tab order through the page:
- Use semantic HTML elements that are naturally focusable
- Add `tabindex="0"` to make elements focusable
- Use `tabindex="-1"` to remove from tab order
- Never use positive tabindex values

### Keyboard Shortcuts

Common keyboard patterns:
- `Escape`: Close modals, cancel operations
- `Enter`: Activate buttons, submit forms
- `Space`: Toggle checkboxes, activate buttons
- `Arrow keys`: Navigate lists and menus

## Screen Reader Support

### Alternative Text

Provide meaningful alt text for images:

```svelte
<!-- Descriptive alt text -->
<img src="/img/logo.png" alt="Hello Zenno logo" />

<!-- Decorative images -->
<img src="/img/decoration.png" alt="" role="presentation" />
```

### Live Regions

Use ARIA live regions for dynamic content updates:

```svelte
<!-- Status messages -->
<div role="status" aria-live="polite">
  {statusMessage}
</div>

<!-- Error messages -->
<div role="alert" aria-live="assertive">
  {errorMessage}
</div>
```

### Visually Hidden Content

Provide screen reader-only content when needed:

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## Form Accessibility

### Labels

Always associate labels with form controls:

```svelte
<!-- Explicit label -->
<label for="email">Email Address</label>
<input type="email" id="email" />

<!-- Implicit label -->
<label>
  Email Address
  <input type="email" />
</label>
```

### Error Messages

Connect error messages to form fields:

```svelte
<input
  type="email"
  id="email"
  aria-invalid={hasError}
  aria-describedby="email-error" />

{#if hasError}
  <span id="email-error" role="alert">
    Please enter a valid email address
  </span>
{/if}
```

### Required Fields

Indicate required fields clearly:

```svelte
<label for="name">
  Name <span aria-label="required">*</span>
</label>
<input
  type="text"
  id="name"
  required
  aria-required="true" />
```

## Testing Accessibility

### Manual Testing

1. **Keyboard Navigation**: Navigate using only keyboard
2. **Screen Reader**: Test with NVDA (Windows) or VoiceOver (Mac)
3. **Color Contrast**: Use browser DevTools or contrast checkers
4. **Focus Indicators**: Ensure visible focus states

### Automated Testing

Consider using:
- axe DevTools browser extension
- Lighthouse in Chrome DevTools
- eslint-plugin-jsx-a11y for development

## Related Documentation

- [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) - Visual design and theming
- [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) - UX patterns and interactions
- [ICONS_SYMBOLS.md](./ICONS_SYMBOLS.md) - Icon usage and accessibility