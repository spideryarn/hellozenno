#!/usr/bin/env python
"""
CLI tool to generate language learning content.

This utility generates new Sourcefile content for HelloZenno in various languages.
It uses an LLM to create content at different CEFR levels, and stores it in the
database using existing infrastructure.

Usage:
    python -m utils.generate_sourcefiles generate --title "My Topic"
"""

from anthropic import Anthropic
import datetime
import typer
from loguru import logger
import random
from slugify import slugify
from typing import Optional

# Relative imports for running from backend directory
from config import SUPPORTED_LANGUAGES
from utils.env_config import VITE_FRONTEND_URL
from db_models import Sourcedir, Sourcefile
from gjdutils.llm_utils import generate_gpt_from_template
from utils.lang_utils import validate_language_code, validate_language_level
from utils.types import VALID_LANGUAGE_LEVELS
from utils.env_config import CLAUDE_API_KEY
from utils.prompt_utils import get_prompt_template_path
from utils.lang_utils import get_language_name, get_all_languages
from utils.db_connection import init_db
from utils.sourcefile_utils import _create_text_sourcefile

# Constants
DEFAULT_SOURCEDIR_NAME = "AI-generated examples"


# Initialize database connection
init_db()

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY.get_secret_value())

# Initialize Typer app
app = typer.Typer(help="Generate language learning content")


def find_language_with_no_sourcefiles() -> str:
    """Find a language code with no or few sourcefiles.

    Returns:
        A language code string (e.g., 'el' for Greek)
    """
    # Get all supported languages
    languages = [lang["code"] for lang in get_all_languages()]

    # Filter to just the supported ones if configured
    if SUPPORTED_LANGUAGES:
        languages = [code for code in languages if code in SUPPORTED_LANGUAGES]

    # First, try to find languages with no sourcefiles
    empty_languages = []
    for lang_code in languages:
        # Count sourcefiles for this language
        sourcefile_count = (
            Sourcefile.select()
            .join(Sourcedir)
            .where(Sourcedir.target_language_code == lang_code)
            .count()
        )

        if sourcefile_count == 0:
            empty_languages.append(lang_code)

    # If we found languages with no sourcefiles, choose one randomly
    if empty_languages:
        return random.choice(empty_languages)

    # Otherwise, find the language with the fewest sourcefiles
    language_counts = []
    for lang_code in languages:
        sourcefile_count = (
            Sourcefile.select()
            .join(Sourcedir)
            .where(Sourcedir.target_language_code == lang_code)
            .count()
        )
        language_counts.append((lang_code, sourcefile_count))

    # Sort by count and return the language with fewest sourcefiles
    language_counts.sort(key=lambda x: x[1])
    return language_counts[0][0]


def get_or_create_ai_sourcedir(
    target_language_code: str, sourcedir_path: str = DEFAULT_SOURCEDIR_NAME
) -> Sourcedir:
    """Get or create a sourcedir for the given language.

    Args:
        target_language_code: The language code (e.g., 'el' for Greek)
        sourcedir_path: The path for the sourcedir (default: DEFAULT_SOURCEDIR_NAME)

    Returns:
        A Sourcedir object
    """
    # Try to find the sourcedir by path
    try:
        sourcedir = Sourcedir.get(
            Sourcedir.path == sourcedir_path,
            Sourcedir.target_language_code == target_language_code,
        )
        return sourcedir
    except:
        # If not found, create a new one
        sourcedir = Sourcedir.create(
            path=sourcedir_path,
            target_language_code=target_language_code,
            slug=slugify(sourcedir_path),
            description="AI-generated content for language learning",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        return sourcedir


def choose_language_level(target_language_code: str) -> str:
    """Choose a language level based on what's missing for a language.

    This will select a level that is less represented in the existing content,
    targeting intermediate to advanced levels (A2-C2) for variety.

    Args:
        target_language_code: The language code to check

    Returns:
        A CEFR level string (A2, B1, B2, C1)
    """
    from utils.types import VALID_LANGUAGE_LEVELS

    # We'll skip A1, C1, C2 unless explicitly requested, since our site targets intermediate+ learners
    intermediate_levels = ["A2", "B1", "B2"]

    # Count existing sourcefiles by language level
    level_counts = {}
    for level in intermediate_levels:
        level_counts[level] = (
            Sourcefile.select()
            .join(Sourcedir)
            .where(
                (Sourcedir.target_language_code == target_language_code)
                & (Sourcefile.language_level == level)
            )
            .count()
        )

    # Find the level with the fewest entries
    min_level = min(level_counts.items(), key=lambda x: x[1])

    # If we have no entries for any level, pick randomly from intermediate levels
    if min_level[1] == 0:
        return random.choice(intermediate_levels)

    # Otherwise return the level with fewest entries
    return min_level[0]


def generate_topic(
    target_language_code: str,
    sourcedir_path: str,
    language_level: str,
) -> str:
    """Generate a topic using the LLM.

    Args:
        target_language_code: The language code (e.g., 'el' for Greek)
        sourcedir_path: Path of the sourcedir to generate content for
        language_level: CEFR level (A2, B1, B2, C1)

    Returns:
        The generated topic title
    """
    # Get the language name for the template
    target_language_name = get_language_name(target_language_code)

    # Expect caller to pass a concrete language_level. Validate non-empty.
    if not language_level:
        raise ValueError("language_level must be provided when calling generate_topic")

    # Get existing filenames from this sourcedir to avoid duplicates
    existing_filenames = []
    try:
        sourcedir = Sourcedir.get(
            Sourcedir.path == sourcedir_path,
            Sourcedir.target_language_code == target_language_code,
        )
        existing_files = (
            Sourcefile.select(Sourcefile.filename)
            .where(Sourcefile.sourcedir == sourcedir)
            .order_by(Sourcefile.created_at.desc())
            .limit(10)  # Just check the most recent 10 files
        )
        existing_filenames = [f.filename for f in existing_files]
    except:
        # Sourcedir doesn't exist yet, so no files to check
        pass

    # Generate topic using the template
    template_path = get_prompt_template_path("generate_topic")
    # Convert to Path object as required by generate_gpt_from_template
    from pathlib import Path

    template_path = Path(template_path)

    generated_topic, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template=template_path,
        context_d={
            "target_language_name": target_language_name,
            "language_level": language_level,
            "sourcedir_path": sourcedir_path,
            "existing_filenames": existing_filenames,
        },
        response_json=False,
        verbose=1,
    )

    return generated_topic.strip()  # type: ignore


def generate_content(
    target_language_code: str,
    title: str,
    language_level: str,
    text_type: Optional[str] = None,
) -> tuple[str, list[str]]:
    """Generate content using the LLM.

    Args:
        target_language_code: The language code (e.g., 'el' for Greek)
        title: The title/topic for the content
        language_level: CEFR level (A2, B1, B2, C1)
        text_type: Optional type of text (e.g., "story", "article")

    Returns:
        The generated text content and a list of tags
    """
    # Get the language name for the template
    target_language_name = get_language_name(target_language_code)

    # Caller must supply language_level
    if not language_level:
        raise ValueError(
            "language_level must be provided when calling generate_content"
        )

    # Generate content using the template
    generated_text, extra = generate_gpt_from_template(
        client=anthropic_client,
        prompt_template=get_prompt_template_path("generate_sourcefiles"),
        context_d={
            "target_language_name": target_language_name,
            "language_level": language_level,
            "title": title,
            "text_type": text_type,
        },
        response_json=False,
        verbose=1,
    )

    # Generate 2-5 tags for the content
    tags = ["language-learning"]
    if "story" in title.lower() or "tale" in title.lower():
        tags.append("fiction")
    elif "history" in title.lower() or "historical" in title.lower():
        tags.append("history")
    elif (
        "food" in title.lower()
        or "cuisine" in title.lower()
        or "recipe" in title.lower()
    ):
        tags.append("food")
    elif (
        "travel" in title.lower()
        or "city" in title.lower()
        or "country" in title.lower()
    ):
        tags.append("travel")
    elif (
        "culture" in title.lower()
        or "tradition" in title.lower()
        or "festival" in title.lower()
    ):
        tags.append("culture")

    # Always add the language as a tag
    tags.append(target_language_name.lower())

    # Ensure we have at least 2 tags
    if len(tags) < 2:
        tags.append("educational")

    return generated_text, tags  # type: ignore


@app.command()
def generate(
    target_language_code: Optional[str] = typer.Option(
        None,
        "--target-language-code",
        help="Language code (e.g., 'el' for Greek)",
        callback=validate_language_code,
    ),
    sourcedir: str = typer.Option(
        DEFAULT_SOURCEDIR_NAME, "--sourcedir", help="Source directory name"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        help="Content title/topic (if not provided, one will be generated)",
    ),
    language_level: Optional[str] = typer.Option(
        None,
        "--language-level",
        help=f"CEFR level ({', '.join(VALID_LANGUAGE_LEVELS)})",
        callback=validate_language_level,
    ),
) -> None:
    """Generate a new text Sourcefile with AI-generated content."""
    # If no language code provided, find one with no sourcefiles
    if not target_language_code:
        target_language_code = find_language_with_no_sourcefiles()
        logger.info(
            f"Selected language with fewest sourcefiles: {target_language_code} ({get_language_name(target_language_code)})"
        )

    # ------------------------------------------------------------
    # Determine the language level *once* so it propagates through
    # ------------------------------------------------------------
    if language_level is None:
        language_level = choose_language_level(target_language_code)
        logger.info(
            f"No language level specified, selected {language_level} based on existing content"
        )

    # Get or create the sourcedir
    sourcedir_entry = get_or_create_ai_sourcedir(target_language_code, sourcedir)

    # Generate a topic if none provided
    if title is None:
        logger.info(f"No title specified, generating one automatically")
        title = generate_topic(
            target_language_code=target_language_code,
            sourcedir_path=sourcedir,
            language_level=language_level,
        )
        logger.info(f"Generated title: {title}")

    # Generate the content
    logger.info(
        f"Generating content for '{title}' in {get_language_name(target_language_code)}"
    )
    generated_content, tags = generate_content(
        target_language_code=target_language_code,
        title=title,
        language_level=language_level,
        text_type=None,  # Default to "short passage" in the template
    )

    # Create human-readable filename from title
    filename = f"{title}.txt"

    # Generate description - just use the model information
    description = f"AI-generated by Claude Sonnet 3.7"

    # Join tags with semicolons
    tags_str = ";".join(tags)

    # Prepare metadata
    metadata = {
        "generated": True,
        "title": title,
        "language_level": language_level,  # This will never be None now
        "generation_method": "llm",
        "tags": tags_str,
        "model": "Claude Sonnet 3.7",
    }

    # Create the sourcefile
    sourcefile = _create_text_sourcefile(
        sourcedir_entry=sourcedir_entry,
        filename=filename,
        text_target=generated_content,
        description=description,
        metadata=metadata,
        sourcefile_type="text",
        language_level=language_level,  # Pass language_level directly to use dedicated field
        ai_generated=True,  # Mark as AI-generated using the new field
    )

    logger.info(f"Created new sourcefile: {sourcefile.filename} ({sourcefile.id})")  # type: ignore
    logger.info(f"Content length: {len(generated_content.split())} words")

    # Show success message
    target_language_name = get_language_name(target_language_code)
    typer.echo(
        f"✅ Successfully generated {language_level} content about '{title}' in {target_language_name}"
    )
    typer.echo(f"📝 Sourcefile ID: {sourcefile.id}")  # type: ignore
    typer.echo(f"🏷️ Tags: {tags_str}")

    sourcefile_path = f"{sourcedir}/{filename}"
    full_url = f"{VITE_FRONTEND_URL}/language/{target_language_code}/source/{sourcedir_entry.slug}/{sourcefile.slug}/text"

    typer.echo(f"📁 Path: {sourcefile_path}")
    typer.echo(f"🔗 URL: {full_url}")


if __name__ == "__main__":
    app()
