import tempfile
from typing import get_args
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from pathlib import Path
from peewee import DoesNotExist

from config import (
    DEFAULT_LANGUAGE_LEVEL,
)
from db_models import (
    Phrase,
    Sourcedir,
    Sourcefile,
    SourcefilePhrase,
    SourcefileWordform,
    Wordform,
)
from utils.lang_utils import get_language_name
from utils.sentence_utils import get_all_sentences
from utils.sourcedir_utils import (
    _get_navigation_info,
    _navigate_sourcefile,
)
from utils.sourcefile_utils import (
    _get_sourcefile_entry,
    process_sourcefile,
)
from utils.types import LanguageLevel
from utils.url_registry import endpoint_for
from utils.vocab_llm_utils import (
    create_interactive_word_links,
)
from utils.word_utils import get_sourcefile_lemmas


sourcefile_views_bp = Blueprint("sourcefile_views", __name__, url_prefix="/lang")


@sourcefile_views_bp.route("/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>")
def inspect_sourcefile_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Redirect to the text view of a source file."""
    try:
        # Check if the file exists first
        _get_sourcefile_entry(target_language_code, sourcedir_slug, sourcefile_slug)

        return redirect(
            url_for(
                endpoint_for(inspect_sourcefile_text_vw),
                target_language_code=target_language_code,
                sourcedir_slug=sourcedir_slug,
                sourcefile_slug=sourcefile_slug,
            )
        )
    except DoesNotExist:
        abort(404, description="File not found")


# Helper functions for reducing redundancy in inspect_sourcefile_* views
def _get_wordforms_data(sourcefile_entry):
    """Get wordforms data using the optimized query, including junction table data in one query."""
    # Use the enhanced version of get_all_wordforms_for that includes junction data
    language_code = sourcefile_entry.sourcedir.language_code

    # This avoids N+1 queries by including junction table data in a single query
    return Wordform.get_all_wordforms_for(
        language_code=language_code,
        sourcefile=sourcefile_entry,
        include_junction_data=True,  # This will return wordform dicts with centrality and ordering
    )


def _get_phrases_data(sourcefile_entry):
    """Get phrases data using the optimized query with included junction data."""
    language_code = sourcefile_entry.sourcedir.language_code

    # Use the enhanced get_all_phrases_for method with include_junction_data=True
    # This returns phrase dictionaries with centrality and ordering already included
    return Phrase.get_all_phrases_for(
        language_code=language_code,
        sourcefile=sourcefile_entry,
        include_junction_data=True,  # This will return phrase dicts with centrality and ordering
    )


def _get_phrases_count(sourcefile_entry):
    """Get only the phrase count for a sourcefile."""
    return (
        SourcefilePhrase.select()
        .where(SourcefilePhrase.sourcefile == sourcefile_entry)
        .count()
    )


def _get_wordforms_count(sourcefile_entry):
    """Get only the wordforms count for a sourcefile."""
    return (
        SourcefileWordform.select()
        .where(SourcefileWordform.sourcefile == sourcefile_entry)
        .count()
    )


def _get_sourcefile_metadata(sourcefile_entry):
    """Create a metadata dictionary for a sourcefile."""
    metadata = {
        "created_at": sourcefile_entry.created_at,
        "updated_at": sourcefile_entry.updated_at,
    }
    if sourcefile_entry.metadata and "image_processing" in sourcefile_entry.metadata:
        metadata["image_processing"] = sourcefile_entry.metadata["image_processing"]

    return metadata


def _get_available_sourcedirs(target_language_code):
    """Get all available sourcedirs for a language."""
    return (
        Sourcedir.select(Sourcedir.path, Sourcedir.slug)
        .where(Sourcedir.language_code == target_language_code)
        .order_by(Sourcedir.path)
    )


def _get_common_template_params(
    target_language_code,
    target_language_name,
    sourcefile_entry,
    sourcedir_slug,
    sourcefile_slug,
    nav_info,
    metadata,
    already_processed,
    available_sourcedirs,
):
    """Get common template parameters used in all sourcefile view functions."""
    return {
        "target_language_code": target_language_code,
        "target_language_name": target_language_name,
        "sourcedir": sourcefile_entry.sourcedir.path,
        "sourcedir_slug": sourcedir_slug,
        "sourcefile": sourcefile_entry.filename,
        "sourcefile_slug": sourcefile_slug,
        "sourcefile_type": sourcefile_entry.sourcefile_type,
        "sourcefile_entry": sourcefile_entry,
        "metadata": metadata,
        "nav_info": nav_info,
        "already_processed": already_processed,
        "available_sourcedirs": available_sourcedirs,
    }


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/text"
)
def inspect_sourcefile_text_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the text content of a source file."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get navigation info
        nav_info = _get_navigation_info(
            sourcefile_entry.sourcedir, sourcefile_entry.slug  # type: ignore
        )

        # Get existing linked wordforms from database
        wordforms_d = _get_wordforms_data(sourcefile_entry)

        # Get phrases from database
        phrases_d = _get_phrases_data(sourcefile_entry)

        # Create enhanced text with interactive word links
        enhanced_original_txt, found_wordforms = create_interactive_word_links(
            text=str(sourcefile_entry.text_target or ""),
            wordforms=wordforms_d,
            target_language_code=target_language_code,
        )

        # Create metadata dict
        metadata = _get_sourcefile_metadata(sourcefile_entry)

        # Check if file has been processed before
        already_processed = bool(wordforms_d)

        # Get all available sourcedirs for this language (for move dropdown)
        available_sourcedirs = _get_available_sourcedirs(target_language_code)

        # Get common template parameters
        template_params = _get_common_template_params(
            target_language_code,
            target_language_name,
            sourcefile_entry,
            sourcedir_slug,
            sourcefile_slug,
            nav_info,
            metadata,
            already_processed,
            available_sourcedirs,
        )

        # Add view-specific parameters
        template_params.update(
            {
                "enhanced_original_txt": enhanced_original_txt,
                "translated_txt": sourcefile_entry.text_english,
                "active_tab": "text",
                "wordforms_d": wordforms_d,
                "phrases_d": phrases_d,
            }
        )

        return render_template("sourcefile_text.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/words"
)
def inspect_sourcefile_words_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the words and phrases of a source file."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get navigation info
        nav_info = _get_navigation_info(
            sourcefile_entry.sourcedir, sourcefile_entry.slug  # type: ignore
        )

        # Get existing linked wordforms from database with optimized query
        wordforms_d = _get_wordforms_data(sourcefile_entry)

        # For the words view, we only need phrases count for the tab, not full data
        phrases_count = _get_phrases_count(sourcefile_entry)
        # But for backward compatibility, we'll still get the full phrases data
        phrases_d = _get_phrases_data(sourcefile_entry)

        # Create metadata dict
        metadata = _get_sourcefile_metadata(sourcefile_entry)

        # Check if file has been processed before
        already_processed = bool(wordforms_d)

        # Get all available sourcedirs for this language (for move dropdown)
        available_sourcedirs = _get_available_sourcedirs(target_language_code)

        # Get common template parameters
        template_params = _get_common_template_params(
            target_language_code,
            target_language_name,
            sourcefile_entry,
            sourcedir_slug,
            sourcefile_slug,
            nav_info,
            metadata,
            already_processed,
            available_sourcedirs,
        )

        # Add view-specific parameters
        template_params.update(
            {
                "active_tab": "words",
                "wordforms_d": wordforms_d,
                "phrases_d": phrases_d,
            }
        )

        return render_template("sourcefile_words.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/phrases"
)
def inspect_sourcefile_phrases_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the phrases of a source file."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get navigation info
        nav_info = _get_navigation_info(
            sourcefile_entry.sourcedir, sourcefile_entry.slug  # type: ignore
        )

        # For the phrases view, we only need wordforms count for the tab, not full data
        wordforms_count = _get_wordforms_count(sourcefile_entry)
        # But for backward compatibility, we'll still get the full wordforms data
        wordforms_d = _get_wordforms_data(sourcefile_entry)

        # Get phrases data with optimized query
        phrases_d = _get_phrases_data(sourcefile_entry)

        # Create metadata dict
        metadata = _get_sourcefile_metadata(sourcefile_entry)

        # Check if file has been processed before
        already_processed = bool(phrases_d)

        # Get all available sourcedirs for this language (for move dropdown)
        available_sourcedirs = _get_available_sourcedirs(target_language_code)

        # Get common template parameters
        template_params = _get_common_template_params(
            target_language_code,
            target_language_name,
            sourcefile_entry,
            sourcedir_slug,
            sourcefile_slug,
            nav_info,
            metadata,
            already_processed,
            available_sourcedirs,
        )

        # Add view-specific parameters
        template_params.update(
            {
                "active_tab": "phrases",
                "phrases_d": phrases_d,
                "wordforms_d": wordforms_d,
            }
        )

        return render_template("sourcefile_phrases.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")


def access_sourcefile(
    target_language_code: str,
    sourcedir_slug: str,
    sourcefile_slug: str,
    *,
    as_attachment: bool = False,
):
    """Helper function to access source files."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(str(sourcefile_entry.filename)).suffix
        ) as temp_file:
            # Write the content to the temporary file based on type
            if sourcefile_entry.sourcefile_type in ["audio", "youtube_audio"]:
                if sourcefile_entry.audio_data is None:
                    abort(404, description="Audio content not found")
                temp_file.write(bytes(sourcefile_entry.audio_data))
            else:  # image type
                if sourcefile_entry.image_data is None:
                    abort(404, description="Image content not found")
                temp_file.write(bytes(sourcefile_entry.image_data))
            temp_file.flush()

            # Map common file extensions to MIME types
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".pdf": "application/pdf",
                ".txt": "text/plain",
                ".mp3": "audio/mpeg",
            }
            suffix = Path(str(sourcefile_entry.filename)).suffix.lower()
            mimetype = mime_types.get(suffix, "application/octet-stream")

            response = send_file(
                temp_file.name,
                mimetype=mimetype,
                as_attachment=as_attachment,
            )
            if as_attachment:
                # Sanitize filename for Content-Disposition header
                safe_filename = (
                    str(sourcefile_entry.filename).encode("ascii", "ignore").decode()
                )
                if not safe_filename:  # If filename becomes empty after sanitization
                    safe_filename = sourcefile_slug + suffix
                response.headers["Content-Disposition"] = (
                    f'attachment; filename="{safe_filename}"'
                )
            return response
    except DoesNotExist:
        abort(404, description="File not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/view"
)
def view_sourcefile_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """View the source file."""
    return access_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, as_attachment=False
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/download"
)
def download_sourcefile_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Download the source file."""
    return access_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, as_attachment=True
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/process"
)
def process_sourcefile_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Process a source file to transcribe, translate, andextract wordforms and phrases.

    You can run this multiple times to extract more words and phrases.

    GET parameters:
    - max_new_words: Maximum number of words to extract (default=3, 0 to skip, None for no limit)
    - max_new_phrases: Maximum number of phrases to extract (default=1, 0 to skip, None for no limit)
    - language_level: Language level for word/phrase selection (default=config.DEFAULT_LANGUAGE_LEVEL)
    """

    def already_processed(sourcefile_entry: Sourcefile):
        return bool(sourcefile_entry.text_target)

    # try:
    sourcefile_entry = _get_sourcefile_entry(
        target_language_code, sourcedir_slug, sourcefile_slug
    )
    DEFAULT_MAX_NEW_WORDS_FOR_UNPROCESSED_SOURCEFILE = 3
    DEFAULT_MAX_NEW_PHRASES_FOR_UNPROCESSED_SOURCEFILE = 1
    if "max_new_words" in request.args:
        max_new_words = int(request.args["max_new_words"])
    else:
        if already_processed(sourcefile_entry):
            max_new_words = None
        else:
            max_new_words = DEFAULT_MAX_NEW_WORDS_FOR_UNPROCESSED_SOURCEFILE
    if "max_new_phrases" in request.args:
        max_new_phrases = int(request.args["max_new_phrases"])
    else:
        if already_processed(sourcefile_entry):
            max_new_phrases = None
        else:
            max_new_phrases = DEFAULT_MAX_NEW_PHRASES_FOR_UNPROCESSED_SOURCEFILE
    language_level = request.args.get("language_level", DEFAULT_LANGUAGE_LEVEL)
    assert language_level in get_args(
        LanguageLevel
    ), f"Invalid language level: {language_level}"
    # Use the new combined process_sourcefile function with default parameters
    process_sourcefile(
        sourcefile_entry,
        language_level=language_level,  # type: ignore
        max_new_words=max_new_words,
        max_new_phrases=max_new_phrases,
    )

    flash("Sourcefile processed successfully")
    # except DoesNotExist:
    #     return "Sourcefile not found", 404
    # except Exception as e:
    #     flash(f"Sourcefile processing failed: {str(e)}")

    # Always redirect back to the sourcefile view
    return redirect(
        url_for(
            endpoint_for(inspect_sourcefile_vw),
            target_language_code=target_language_code,
            sourcedir_slug=sourcedir_slug,
            sourcefile_slug=sourcefile_slug,
        )
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/audio"
)
def play_sourcefile_audio_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Play the audio file associated with the source file."""
    try:
        # Get the sourcefile entry using helper
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Create a temporary file to store the content
        audio_filename = Path(str(sourcefile_entry.filename)).with_suffix(".mp3").name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            # Write the audio content to the temporary file
            if sourcefile_entry.audio_data is None:
                abort(404, description="Audio content not found")
            temp_file.write(bytes(sourcefile_entry.audio_data))
            temp_file.flush()

            return send_file(
                temp_file.name, mimetype="audio/mpeg", download_name=audio_filename
            )
    except DoesNotExist:
        abort(404, description="Audio file not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/sentences"
)
def sourcefile_sentences_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Show sentences for a sourcefile."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get sourcedir and sourcefile
        sourcedir = Sourcedir.get(
            Sourcedir.slug == sourcedir_slug,
            Sourcedir.language_code == target_language_code,
        )
        sourcefile = Sourcefile.get(
            Sourcefile.slug == sourcefile_slug,
            Sourcefile.sourcedir == sourcedir,
        )

        # Get lemmas from sourcefile's wordforms
        lemmas = get_sourcefile_lemmas(
            target_language_code, sourcedir_slug, sourcefile_slug
        )

        # Get sentences containing any of these lemmas
        matching_sentences = [
            s
            for s in get_all_sentences(target_language_code)
            if s.get("lemma_words")
            and any(lemma in s["lemma_words"] for lemma in lemmas)
        ]

        # Get the first matching sentence for initial display
        sentence = matching_sentences[0] if matching_sentences else None

        return render_template(
            "sentence_flashcards.jinja",
            target_language_code=target_language_code,
            target_language_name=target_language_name,
            sourcedir=sourcedir,
            sourcefile=sourcefile,
            lemmas=lemmas,
            sentence=sentence,
        )
    except DoesNotExist:
        abort(404, description="Source file not found")


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/next"
)
def next_sourcefile_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Navigate to the next sourcefile alphabetically."""
    return _navigate_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, increment=1
    )


@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/prev"
)
def prev_sourcefile_vw(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Navigate to the previous sourcefile alphabetically."""
    return _navigate_sourcefile(
        target_language_code, sourcedir_slug, sourcefile_slug, increment=-1
    )
