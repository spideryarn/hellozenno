# Sitemap Implementation

## Overview

This document outlines the sitemap implementation for HelloZenno to help search engines efficiently crawl our content and reduce unwanted bot traffic to unauthorized pages.

## Architecture

Our sitemap system consists of:

1. **Sitemap reference in robots.txt**
2. **Sitemap index** that references all individual sitemaps
3. **Static pages sitemap** for main site pages
4. **Dynamic content sitemaps** generated during build/deployment

## Implementation Details

### 1. Sitemap Structure

```
sitemap.xml (index file)
├── sitemap-static.xml (homepage, about, faq, etc.)
├── sitemap-{language_code}.xml (if not further divided)
├── sitemap-{language_code}-lemmas.xml
├── sitemap-{language_code}-wordforms.xml
├── sitemap-{language_code}-sentences.xml
├── sitemap-{language_code}-phrases.xml
├── sitemap-{language_code}-sourcedirs.xml
└── sitemap-{language_code}-sourcefiles.xml
```

### 2. Build-time Generation

We generate sitemaps during the deployment process to avoid serverless execution issues:

1. A Python script queries the database during deployment
2. Generates sitemap files as static XML
3. Updates the sitemap index with current timestamps
4. Deploys these static files to Vercel

Benefits:
- No runtime performance impact
- No caching concerns
- Accurate `lastmod` timestamps
- No execution during serverless warm-up

### 3. Implementation Plan

#### 3.1 Script Location and Structure

Create a script at `frontend/scripts/generate_sitemaps.py` that:

1. Connects to the database using existing utilities
2. Queries for public content across all supported languages
3. Generates XML sitemap files in `frontend/static/` directory
4. Updates the sitemap index with current timestamp

#### 3.2 Deployment Integration

Modify `scripts/prod/deploy_frontend.sh` to:

1. Run the sitemap generation script before building the frontend
2. Example:
   ```bash
   # Generate sitemaps
   python frontend/scripts/generate_sitemaps.py
   
   # Continue with normal build process
   cd frontend && npm run build
   ```

#### 3.3 XML Structure Examples

**Sitemap Index (sitemap.xml):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://hellozenno.com/sitemap-static.xml</loc>
    <lastmod>2025-04-26</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://hellozenno.com/sitemap-el-lemmas.xml</loc>
    <lastmod>2025-04-26</lastmod>
  </sitemap>
  <!-- Additional sitemaps -->
</sitemapindex>
```

**Content Sitemap Example (sitemap-el-lemmas.xml):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://hellozenno.com/language/el/lemma/γεια</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <!-- Additional URLs -->
</urlset>
```

### 4. Script Implementation Details

The generation script will:

1. Use the same database connection utilities as the backend
2. For each language and content type:
   - Query public content (e.g., all public lemmas for Greek)
   - Use URL registry to generate canonical URLs
   - Create appropriate XML structure
   - Set reasonable priority and change frequency values
   - Save to static XML files
3. Update the sitemap index with current timestamp

### 5. Pagination Strategy

If any content type exceeds 50,000 URLs (the sitemap standard limit):
- Split into multiple files with numerical suffixes
- Example: `sitemap-el-lemmas-1.xml`, `sitemap-el-lemmas-2.xml`
- Update sitemap index to reference all parts

### 6. Priority Settings

Priority values by content type:
- Homepage: 1.0
- Language pages: 0.9
- About/FAQ: 0.8
- Lemmas: 0.7
- Sentences: 0.7
- Phrases: 0.7
- Wordforms: 0.6
- Sourcedirs: 0.6
- Sourcefiles: 0.5

## Maintenance

Generate new sitemaps on each deployment to keep content fresh. If deployment frequency decreases in the future, consider:

1. Creating a scheduled job to regenerate sitemaps
2. Moving to a more dynamic approach if deployment-based generation becomes insufficient

## Future Considerations

- Automated tests to verify sitemap validity
- Analytics to track crawler behavior before/after implementation
- Potential optimization based on observed search engine behavior