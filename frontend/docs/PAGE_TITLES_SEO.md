# Page Titles and SEO

This document outlines the page title structure and SEO best practices for the Hello Zenno application.

For general visual design, see [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md).

## Page Title Structure

Page titles should follow a consistent structure for better SEO and user experience.

### Title Patterns

#### Language-Specific Pages

Pattern: `[Specific Content] | [Page Type] | [Language Name] | [Site Name]`

Examples:
- `καλημέρα | Lemma | Greek | Hello Zenno`
- `Sources | Greek | Hello Zenno`
- `Sentences | Greek | Hello Zenno`

#### General Pages

Pattern: `[Page Name] | [Site Name]`

Examples:
- `Languages | Hello Zenno`
- `FAQ | Hello Zenno`
- `About | Hello Zenno`

#### Home Page

Pattern: `[Site Name] - [Tagline]`

Example:
- `Hello Zenno - AI-powered dictionary & listening practice`

## Implementation

### Configuration

Use the constants from `frontend/src/lib/config.ts` for consistency:

```typescript
export const SITE_NAME = 'Hello Zenno';
export const TAGLINE = 'AI-powered dictionary & listening practice';
```

### Setting Titles in Svelte

Set titles within a `<svelte:head>` tag in your component:

```svelte
<script>
  import { SITE_NAME, TAGLINE } from '$lib/config';

  // For dynamic content
  export let lemmaText = '';
  export let languageName = '';
</script>

<svelte:head>
  <title>{lemmaText} | Lemma | {languageName} | {SITE_NAME}</title>
</svelte:head>
```

### Truncating Long Titles

For long content titles (like sentences), use the `truncate()` utility function:

```svelte
<script>
  import { truncate } from '$lib/utils';
  import { SITE_NAME } from '$lib/config';

  export let sentence = '';
  export let languageName = '';

  $: pageTitle = `${truncate(sentence, 50)} | Sentence | ${languageName} | ${SITE_NAME}`;
</script>

<svelte:head>
  <title>{pageTitle}</title>
</svelte:head>
```

### Server-Side Rendering

Pass title information from server to client components as needed:

```typescript
// +page.server.ts
export async function load({ params }) {
  const lemma = await fetchLemma(params.id);

  return {
    lemma,
    title: `${lemma.text} | Lemma | ${lemma.language} | Hello Zenno`
  };
}
```

```svelte
<!-- +page.svelte -->
<script>
  export let data;
</script>

<svelte:head>
  <title>{data.title}</title>
</svelte:head>
```

## Meta Tags

### Essential Meta Tags

Include these meta tags on all pages:

```svelte
<svelte:head>
  <title>{pageTitle}</title>
  <meta name="description" content={pageDescription} />

  <!-- Open Graph -->
  <meta property="og:title" content={pageTitle} />
  <meta property="og:description" content={pageDescription} />
  <meta property="og:type" content="website" />
  <meta property="og:url" content={pageUrl} />
  <meta property="og:image" content="/img/og-image.png" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={pageTitle} />
  <meta name="twitter:description" content={pageDescription} />
  <meta name="twitter:image" content="/img/twitter-card.png" />
</svelte:head>
```

### Description Guidelines

- Keep descriptions between 150-160 characters
- Include relevant keywords naturally
- Make them compelling to encourage clicks
- Be specific about the page content

Example descriptions:
- Home: "Learn languages with AI-powered dictionary and listening practice. Master Greek, Spanish, and more with contextual examples and audio."
- Language page: "Explore Greek vocabulary with definitions, audio pronunciation, and real-world sentence examples. AI-powered language learning."
- Lemma page: "Definition and usage of 'καλημέρα' (good morning) in Greek. Includes pronunciation, examples, and related words."

## URL Structure

### Clean URLs

URL trailing slashes are set to `never` so canonical URLs don't have trailing slashes:

```
Good:
- /languages
- /greek
- /greek/lemmas/καλημέρα

Avoid:
- /languages/
- /greek/
- /greek/lemmas/καλημέρα/
```

### Canonical URLs

Always include a canonical URL to prevent duplicate content issues:

```svelte
<svelte:head>
  <link rel="canonical" href={canonicalUrl} />
</svelte:head>
```

### URL Patterns

| Page Type | URL Pattern | Example |
|-----------|------------|---------|
| Home | `/` | `/` |
| Languages | `/languages` | `/languages` |
| Language Home | `/[language]` | `/greek` |
| Sources | `/[language]/sources` | `/greek/sources` |
| Lemmas | `/[language]/lemmas` | `/greek/lemmas` |
| Lemma Detail | `/[language]/lemmas/[id]` | `/greek/lemmas/καλημέρα` |
| Sentences | `/[language]/sentences` | `/greek/sentences` |
| Sentence Detail | `/[language]/sentences/[id]` | `/greek/sentences/123` |

## Structured Data

Add JSON-LD structured data for better search engine understanding:

```svelte
<script>
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": pageTitle,
    "description": pageDescription,
    "url": pageUrl,
    "inLanguage": "en",
    "isPartOf": {
      "@type": "WebSite",
      "name": "Hello Zenno",
      "url": "https://hellozenno.com"
    }
  };
</script>

<svelte:head>
  {@html `<script type="application/ld+json">${JSON.stringify(structuredData)}</script>`}
</svelte:head>
```

## Sitemap

Generate a sitemap.xml file for search engines:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://hellozenno.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://hellozenno.com/languages</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <!-- Additional URLs -->
</urlset>
```

## robots.txt

Configure robots.txt for search engine crawlers:

```
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: https://hellozenno.com/sitemap.xml
```

## Performance Considerations

### Core Web Vitals

Optimize for Google's Core Web Vitals:

1. **Largest Contentful Paint (LCP)**: < 2.5s
2. **First Input Delay (FID)**: < 100ms
3. **Cumulative Layout Shift (CLS)**: < 0.1

### Page Speed

- Optimize images (WebP format, lazy loading)
- Minimize JavaScript bundle size
- Use efficient caching strategies
- Enable compression (gzip/brotli)

## Internationalization (i18n)

For multi-language support:

```svelte
<svelte:head>
  <!-- Language declaration -->
  <html lang={currentLanguageCode} />

  <!-- Alternate language versions -->
  <link rel="alternate" hreflang="en" href="https://hellozenno.com/en/page" />
  <link rel="alternate" hreflang="el" href="https://hellozenno.com/el/page" />
  <link rel="alternate" hreflang="x-default" href="https://hellozenno.com/page" />
</svelte:head>
```

## Related Documentation

- [VISUAL_DESIGN_STYLING.md](./VISUAL_DESIGN_STYLING.md) - Visual design guidelines
- [USER_EXPERIENCE.md](./USER_EXPERIENCE.md) - UX patterns
- [FRONTEND_SVELTEKIT_ARCHITECTURE.md](./FRONTEND_SVELTEKIT_ARCHITECTURE.md) - Frontend architecture