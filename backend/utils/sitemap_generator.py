#!/usr/bin/env python
"""Generate XML sitemaps for HelloZenno, including a sitemap index and content-specific sitemaps."""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
from gjdutils.strings import jinja_render

# Import Peewee models and database connection
from db_models import Phrase, Sourcefile, Sourcedir
from utils.db_connection import db
from utils.env_config import VITE_FRONTEND_URL as SITE_URL

# Constants
FRONTEND_STATIC_DIR = Path(__file__).parent.parent.parent / "frontend" / "static"
MAX_URLS_PER_SITEMAP = 50000

# Jinja templates for sitemap generation
SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for item in items %}
  <url>
    <loc>{{ site_url }}/language/{{ lang_code }}/{{ content_type }}/{{ item.url_param }}</loc>
    {% if item.lastmod %}
    <lastmod>{{ item.lastmod }}</lastmod>
    {% endif %}
    <changefreq>{{ changefreq }}</changefreq>
    <priority>{{ priority }}</priority>
  </url>
{% endfor %}
</urlset>"""

SITEMAP_INDEX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{{ site_url }}/sitemap-static.xml</loc>
    <lastmod>{{ today }}</lastmod>
  </sitemap>
{% for sitemap in sitemaps %}
  <sitemap>
    <loc>{{ site_url }}/{{ sitemap }}</loc>
    <lastmod>{{ today }}</lastmod>
  </sitemap>
{% endfor %}
</sitemapindex>"""


def fetch_available_languages() -> list[dict]:
    """Fetch list of available languages from the configuration."""
    try:
        from utils.lang_utils import get_all_languages
        return get_all_languages()
    except Exception as e:
        logger.error(f"Error fetching languages: {e}")
        return []


def fetch_phrases_for_language(lang_code: str) -> list[dict]:
    """Fetch phrases for a specific language."""
    try:
        phrases = []
        query = (
            Phrase.select(Phrase.slug, Phrase.updated_at)
            .join(Sourcefile)
            .join(Sourcedir)
            .where(Sourcedir.target_language_code == lang_code)
            .order_by(Phrase.updated_at.desc())
        )

        for phrase in query:
            phrases.append({"slug": phrase.slug, "updated_at": phrase.updated_at})
        return phrases
    except Exception as e:
        logger.error(f"Error fetching phrases for language {lang_code}: {e}")
        return []


def fetch_lemmas_for_language(lang_code: str) -> list[dict]:
    """Fetch lemmas for a specific language."""
    try:
        from db_models import Lemma

        lemmas = []
        query = (
            Lemma.select(Lemma.lemma, Lemma.updated_at)
            .where(Lemma.target_language_code == lang_code)
            .order_by(Lemma.updated_at.desc())
        )

        for lemma in query:
            lemmas.append({"lemma": lemma.lemma, "updated_at": lemma.updated_at})
        return lemmas
    except Exception as e:
        logger.error(f"Error fetching lemmas for language {lang_code}: {e}")
        return []


def fetch_sentences_for_language(lang_code: str) -> list[dict]:
    """Fetch sentences for a specific language."""
    try:
        from db_models import Sentence

        sentences = []
        query = (
            Sentence.select(Sentence.slug, Sentence.updated_at)
            .where(Sentence.target_language_code == lang_code)
            .order_by(Sentence.updated_at.desc())
        )

        for sentence in query:
            sentences.append({"slug": sentence.slug, "updated_at": sentence.updated_at})
        return sentences
    except Exception as e:
        logger.error(f"Error fetching sentences for language {lang_code}: {e}")
        return []


def generate_phrase_sitemap(language: dict) -> str:
    """Generate a phrases sitemap for a specific language."""
    lang_code = language["code"]
    filename = f"sitemap-{lang_code}-phrases.xml"
    filepath = FRONTEND_STATIC_DIR / filename

    phrases = fetch_phrases_for_language(lang_code)

    if not phrases:
        logger.warning(f"No phrases found for language: {lang_code}")
        return ""

    logger.info(
        f"Generating phrases sitemap for {lang_code} with {len(phrases)} phrases"
    )

    try:
        # Prepare data for template rendering
        items = []
        for phrase in phrases:
            items.append({
                "url_param": phrase["slug"],
                "lastmod": phrase["updated_at"].strftime("%Y-%m-%d") if phrase["updated_at"] else ""
            })
        
        # Render the template
        sitemap_content = jinja_render(
            SITEMAP_TEMPLATE,
            {
                "items": items,
                "site_url": SITE_URL,
                "lang_code": lang_code,
                "content_type": "phrase",
                "changefreq": "monthly",
                "priority": "0.6"
            }
        )
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(sitemap_content)

        return filename
    except Exception as e:
        logger.error(f"Error writing phrases sitemap for {lang_code}: {e}")
        return ""


def generate_lemma_sitemap(language: dict) -> list[str]:
    """Generate lemma sitemaps for a specific language, paginating if necessary."""
    lang_code = language["code"]
    lemmas = fetch_lemmas_for_language(lang_code)

    if not lemmas:
        logger.warning(f"No lemmas found for language: {lang_code}")
        return []

    # Determine if we need to paginate
    total_lemmas = len(lemmas)
    page_count = (total_lemmas + MAX_URLS_PER_SITEMAP - 1) // MAX_URLS_PER_SITEMAP

    logger.info(
        f"Generating lemmas sitemap for {lang_code} with {total_lemmas} lemmas across {page_count} pages"
    )

    generated_filenames = []

    for page in range(page_count):
        page_suffix = f"-{page+1}" if page_count > 1 else ""
        filename = f"sitemap-{lang_code}-lemmas{page_suffix}.xml"
        filepath = FRONTEND_STATIC_DIR / filename

        start_idx = page * MAX_URLS_PER_SITEMAP
        end_idx = min(start_idx + MAX_URLS_PER_SITEMAP, total_lemmas)
        page_lemmas = lemmas[start_idx:end_idx]

        try:
            # Prepare data for template rendering
            items = []
            for lemma in page_lemmas:
                items.append({
                    "url_param": lemma["lemma"],
                    "lastmod": lemma["updated_at"].strftime("%Y-%m-%d") if lemma["updated_at"] else ""
                })
            
            # Render the template
            sitemap_content = jinja_render(
                SITEMAP_TEMPLATE,
                {
                    "items": items,
                    "site_url": SITE_URL,
                    "lang_code": lang_code,
                    "content_type": "lemma",
                    "changefreq": "monthly",
                    "priority": "0.7"
                }
            )
            
            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(sitemap_content)

            generated_filenames.append(filename)
            logger.info(
                f"Generated lemma sitemap page {page+1}/{page_count} with {len(page_lemmas)} lemmas"
            )

        except Exception as e:
            logger.error(
                f"Error writing lemmas sitemap page {page+1} for {lang_code}: {e}"
            )

    return generated_filenames


def generate_sentence_sitemap(language: dict) -> str:
    """Generate a sentences sitemap for a specific language."""
    lang_code = language["code"]
    filename = f"sitemap-{lang_code}-sentences.xml"
    filepath = FRONTEND_STATIC_DIR / filename

    sentences = fetch_sentences_for_language(lang_code)

    if not sentences:
        logger.warning(f"No sentences found for language: {lang_code}")
        return ""

    logger.info(
        f"Generating sentences sitemap for {lang_code} with {len(sentences)} sentences"
    )

    try:
        # Prepare data for template rendering
        items = []
        for sentence in sentences:
            items.append({
                "url_param": sentence["slug"],
                "lastmod": sentence["updated_at"].strftime("%Y-%m-%d") if sentence["updated_at"] else ""
            })
        
        # Render the template
        sitemap_content = jinja_render(
            SITEMAP_TEMPLATE,
            {
                "items": items,
                "site_url": SITE_URL,
                "lang_code": lang_code,
                "content_type": "sentence",
                "changefreq": "monthly",
                "priority": "0.5"
            }
        )
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(sitemap_content)

        return filename
    except Exception as e:
        logger.error(f"Error writing sentences sitemap for {lang_code}: {e}")
        return ""


def update_sitemap_index(sitemap_files: list[str]) -> None:
    """Update the sitemap index file with references to all sitemaps."""
    today = datetime.now().strftime("%Y-%m-%d")
    index_path = FRONTEND_STATIC_DIR / "sitemap.xml"

    try:
        # Filter out empty filenames
        valid_sitemaps = [sitemap for sitemap in sitemap_files if sitemap]
        
        # Render the index template
        sitemap_index_content = jinja_render(
            SITEMAP_INDEX_TEMPLATE,
            {
                "sitemaps": valid_sitemaps,
                "site_url": SITE_URL,
                "today": today
            }
        )
        
        # Write to file
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(sitemap_index_content)
            
        logger.info(f"Updated sitemap index with {len(valid_sitemaps)} sitemaps")
    except Exception as e:
        logger.error(f"Error updating sitemap index: {e}")


def generate_sitemaps():
    """Main function to generate all sitemaps."""
    logger.info("Starting sitemap generation")

    # Initialize database connection
    db.connect(reuse_if_open=True)

    try:
        languages = fetch_available_languages()
        sitemap_files = []

        # Generate all sitemap types for each language
        for language in languages:
            # Generate phrase sitemap
            phrase_sitemap = generate_phrase_sitemap(language)
            if phrase_sitemap:
                sitemap_files.append(phrase_sitemap)

            # Generate lemma sitemaps (returns list of filenames for pagination)
            lemma_sitemaps = generate_lemma_sitemap(language)
            if lemma_sitemaps:
                sitemap_files.extend(lemma_sitemaps)

            # Generate sentence sitemap
            sentence_sitemap = generate_sentence_sitemap(language)
            if sentence_sitemap:
                sitemap_files.append(sentence_sitemap)

        # Update the sitemap index
        update_sitemap_index(sitemap_files)

        logger.info(
            f"Sitemap generation complete. Generated {len(sitemap_files)} sitemaps in {FRONTEND_STATIC_DIR}"
        )
    except Exception as e:
        logger.error(f"Error generating sitemaps: {e}")
    finally:
        if not db.is_closed():
            db.close()


if __name__ == "__main__":
    generate_sitemaps()
