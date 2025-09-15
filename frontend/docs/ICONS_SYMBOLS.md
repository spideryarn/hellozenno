# Icons and Symbols

This document covers the iconography system used in the Hello Zenno application.

For general visual design and styling, see [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md).

## Phosphor Icons

The application uses Phosphor icons for a consistent iconography system.

### Installation and Setup

We use the `phosphor-svelte` package (version 3.0.1) for icons. The "fill" weight is preferred for homepage and marketing materials to create a more substantial, friendly look.

### Import Syntax

**Important Note for Svelte 5**: For best compatibility with Svelte 5, import icons using the path import syntax rather than named imports:

```svelte
<!-- RECOMMENDED: Use direct path imports like this -->
import PencilSimple from 'phosphor-svelte/lib/PencilSimple';

<!-- AVOID: Named imports can cause issues with Svelte 5 -->
import { PencilSimple } from 'phosphor-svelte';
```

### Common Icons Used

| Icon | Usage |
|------|-------|
| `PencilSimple` | Edit operations |
| `Trash` | Delete operations |
| `Download` | Download actions |
| `FolderOpen` | Folder/directory operations |
| `ChevronUp`/`ChevronDown` | Expand/collapse UI elements |
| `BookOpen` | Dictionary/reading features |
| `MagnifyingGlass` | Search functions |
| `Translate` | Translation features |
| `Globe` | Language selection |
| `SpeakerHigh` | Audio playback |
| `BrainCircuit` | AI-powered features |
| `Lightbulb` | Tips and insights |

### Icon Properties

Icons can be customized with various properties:

```svelte
<PencilSimple size={16} weight="bold" />
```

- **`size`**: Controls the icon size
  - 16px for small icons
  - 24px for navigation icons
  - Larger sizes for hero sections

- **`weight`**: Icon style variants
  - `"regular"` (default)
  - `"bold"`
  - `"fill"` (preferred for marketing)
  - `"duotone"`
  - `"thin"`
  - `"light"`

### Usage Examples

#### Basic Icon

```svelte
<script>
  import MagnifyingGlass from 'phosphor-svelte/lib/MagnifyingGlass';
</script>

<MagnifyingGlass size={20} />
```

#### Icon in Button

```svelte
<script>
  import Download from 'phosphor-svelte/lib/Download';
</script>

<button class="btn btn-primary">
  <Download size={16} weight="bold" />
  Download File
</button>
```

#### Icon with Tooltip

For icon usage in buttons with tooltips and accessibility best practices, see [USER_EXPERIENCE.md](./USER_EXPERIENCE.md#icons-and-buttons).

## Custom Icons and Images

### Logo

The Hello Zenno logo is stored at `/static/img/logo.png` and should be referenced as:

```svelte
<img src="/img/logo.png" alt="Hello Zenno" />
```

### Contact Icon

Email/contact envelope icon: `/static/img/email_contact_envelope.png`

### Marketing Images

Marketing and hero images are stored in `/static/img/marketing/`

## Icon Guidelines

1. **Consistency**: Use Phosphor icons throughout the application for consistency
2. **Weight Selection**: Use "fill" weight for marketing, "regular" or "bold" for app UI
3. **Size Standards**: Maintain consistent sizing across similar contexts
4. **Accessibility**: Always provide appropriate labels for icon-only buttons
5. **Color**: Icons inherit color from their parent element by default

## Related Documentation

- [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) - Main styling guide
- [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) - UX patterns for icons and buttons
- [ACCESSIBILITY.md](./ACCESSIBILITY.md) - Accessibility requirements for icons