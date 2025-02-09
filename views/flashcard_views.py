from utils.audio_utils import ensure_model_audio_data
from db_models import Sentence, Sourcefile, SourcefileWordform, Sourcedir, Wordform
from utils.lang_utils import get_language_name
from peewee import DoesNotExist
from utils.sentence_utils import get_random_sentence
from flask import abort, redirect, render_template, request, url_for, Blueprint

from utils.word_utils import get_sourcedir_lemmas, get_sourcefile_lemmas

# Create a new blueprint for flashcard views
flashcard_views_bp = Blueprint("flashcard_views", __name__)


@flashcard_views_bp.route("/<language_code>/flashcards")
def flashcard_landing(language_code: str):
    """Landing page for flashcards with start button."""
    target_language_name = get_language_name(language_code)
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    sourcefile_entry = None
    sourcedir_entry = None
    lemma_count = None

    # If sourcedir is provided, get lemma count
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(language_code, sourcedir_slug)
            lemma_count = len(lemmas)
        except DoesNotExist:
            abort(404, description="Sourcedir not found")
    # If sourcefile is provided, get its lemma count
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(SourcefileWordform)
                .where(Sourcefile.slug == sourcefile_slug)
                .get()
            )
            lemmas = get_sourcefile_lemmas(language_code, sourcefile_slug)
            lemma_count = len(lemmas)
        except DoesNotExist:
            abort(404, description="Sourcefile not found")

    return render_template(
        "flashcard_landing.jinja",
        target_language_code=language_code,
        target_language_name=target_language_name,
        sourcefile=sourcefile_entry,
        sourcedir=sourcedir_entry,
        lemma_count=lemma_count,
    )


@flashcard_views_bp.route("/<language_code>/flashcards/sentence/<slug>")
def flashcard_sentence(language_code: str, slug: str):
    """View a specific sentence as a flashcard."""
    target_language_name = get_language_name(language_code)

    try:
        sentence = Sentence.get(
            (Sentence.language_code == language_code) & (Sentence.slug == slug)
        )
    except DoesNotExist:
        abort(404, description="Sentence not found")

    # Pre-generate audio if needed
    if not sentence.audio_data:
        try:
            ensure_model_audio_data(
                model=sentence,
                should_add_delays=True,
                verbose=1,
            )
        except Exception as e:
            # Log error but continue - audio can be generated on demand
            print(f"Error pre-generating audio: {e}")

    # Get parameters from query
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    sourcefile_entry = None
    sourcedir_entry = None
    lemma_count = None

    # If sourcedir is provided, get lemma count
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(language_code, sourcedir_slug)
            lemma_count = len(lemmas)
        except DoesNotExist:
            abort(404, description="Sourcedir not found")
    # If sourcefile is provided, get its lemma count
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(SourcefileWordform)
                .where(Sourcefile.slug == sourcefile_slug)
                .get()
            )
            lemmas = get_sourcefile_lemmas(language_code, sourcefile_slug)
            lemma_count = len(lemmas)
        except DoesNotExist:
            abort(404, description="Sourcefile not found")

    return render_template(
        "sentence_flashcards.jinja",
        target_language_code=language_code,
        target_language_name=target_language_name,
        sentence=sentence,
        sourcefile=sourcefile_entry,
        sourcedir=sourcedir_entry,
        lemma_count=lemma_count,
    )


@flashcard_views_bp.route("/<language_code>/flashcards/random")
def random_flashcard(language_code: str):
    """Redirect to a random sentence flashcard."""
    sourcefile_slug = request.args.get("sourcefile")
    sourcedir_slug = request.args.get("sourcedir")

    lemmas = None

    # If sourcedir is provided, get lemmas for filtering
    if sourcedir_slug:
        try:
            sourcedir_entry = Sourcedir.get(Sourcedir.slug == sourcedir_slug)
            lemmas = get_sourcedir_lemmas(language_code, sourcedir_slug)
        except DoesNotExist:
            abort(404, description="Sourcedir not found")
    # If sourcefile is provided, get its lemmas for filtering
    elif sourcefile_slug:
        try:
            sourcefile_entry = (
                Sourcefile.select()
                .join(SourcefileWordform)
                .where(Sourcefile.slug == sourcefile_slug)
                .get()
            )
            lemmas = get_sourcefile_lemmas(language_code, sourcefile_slug)
        except DoesNotExist:
            abort(404, description="Sourcefile not found")

    # Get random sentence
    sentence = get_random_sentence(
        target_language_code=language_code, required_lemmas=lemmas if lemmas else None
    )

    if not sentence:
        abort(404, description="No matching sentences found")

    # Preserve only sourcefile/sourcedir in redirect
    query_params = {}
    if sourcefile_slug:
        query_params["sourcefile"] = sourcefile_slug
    if sourcedir_slug:
        query_params["sourcedir"] = sourcedir_slug

    return redirect(
        url_for(
            "flashcard_views.flashcard_sentence",
            language_code=language_code,
            slug=sentence["slug"],
            **query_params,
        )
    )
