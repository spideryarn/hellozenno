"""Learn flow API endpoints (persistent Learn flow).

Routes:
- GET /api/lang/learn/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/summary
- POST /api/lang/learn/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate

Notes:
- No persistence in v1; sentence/audio are generated on-the-fly and returned.
- Lemma metadata may be generated if missing (requires auth per store_utils).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request, g

from loguru import logger

from utils.error_utils import safe_error_message

from utils.auth_utils import api_auth_required
from utils.word_utils import get_sourcefile_lemmas
from utils.store_utils import load_or_generate_lemma_metadata
from utils.exceptions import AuthenticationRequiredForGenerationError
from utils.lang_utils import get_language_name
from utils.prompt_utils import get_prompt_template_path
from utils.vocab_llm_utils import anthropic_client, generate_gpt_from_template
from utils.sentence_utils import generate_sentence
from utils.audio_utils import ensure_sentence_audio_variants
from utils.db_connection import database
from db_models import Sentence, SentenceAudio, Lemma, Sourcefile, Sourcedir


learn_api_bp = Blueprint("learn_api", __name__, url_prefix="/api/lang/learn")


def _difficulty_score(metadata: dict) -> float:
    commonality = metadata.get("commonality")
    guessability = metadata.get("guessability")
    commonality_val = commonality if isinstance(commonality, (int, float)) else 0.5
    guessability_val = guessability if isinstance(guessability, (int, float)) else 0.5
    # Higher score = harder
    return (1.0 - guessability_val) + (1.0 - commonality_val)


@learn_api_bp.route(
    "/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/summary",
    methods=["GET"],
)
@api_auth_required
def learn_sourcefile_summary_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Return ranked lemma summaries for the given sourcefile.

    Response shape:
    {
      "lemmas": [{
        "lemma": str,
        "translations": list[str],
        "etymology": str,
        "commonality": float | null,
        "guessability": float | null,
        "part_of_speech": str | "unknown"
      }...],
      "meta": {"total_candidates": int, "returned": int, "durations": {...}}
    }
    """
    started_at = time.time()
    durations: Dict[str, float] = {}

    try:
        top_n_param = request.args.get("top", default="20")
        try:
            top_n = max(1, min(100, int(str(top_n_param))))
        except Exception:
            top_n = 20

        # Collect candidate lemmas
        t0 = time.time()
        lemmas: List[str] = get_sourcefile_lemmas(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
        durations["collect_lemmas_s"] = time.time() - t0

        # Time budget for summary (seconds), with sane bounds
        budget_param = request.args.get("time_budget_s")
        try:
            time_budget_s = (
                float(str(budget_param)) if budget_param is not None else 12.0
            )
        except Exception:
            time_budget_s = 12.0
        time_budget_s = max(3.0, min(120.0, time_budget_s))

        # Bulk-prefetch existing lemma metadata in one query to avoid N queries
        bulk_t0 = time.time()
        existing_map: Dict[str, Dict[str, Any]] = {}
        try:
            if lemmas:
                # Peewee will expand the IN (...) safely
                q = Lemma.select(
                    Lemma.lemma,
                    Lemma.translations,
                    Lemma.etymology,
                    Lemma.commonality,
                    Lemma.guessability,
                    Lemma.part_of_speech,
                    Lemma.example_usage,
                    Lemma.mnemonics,
                    Lemma.is_complete,
                ).where(
                    (Lemma.target_language_code == target_language_code)
                    & (Lemma.lemma.in_(lemmas))
                )
                for row in q:
                    existing_map[row.lemma] = {
                        "lemma": row.lemma,
                        "translations": list(row.translations or []),
                        "etymology": row.etymology or "",
                        "commonality": row.commonality,
                        "guessability": row.guessability,
                        "part_of_speech": row.part_of_speech or "unknown",
                        "example_usage": list(row.example_usage or []),
                        "mnemonics": list(row.mnemonics or []),
                        "is_complete": bool(row.is_complete),
                    }
        except Exception as e:
            logger.warning(
                f"Bulk lemma prefetch failed; falling back to per-item loads. Reason: {e}"
            )
            existing_map = {}
        durations["bulk_fetch_s"] = time.time() - bulk_t0

        # Load/generate metadata and score with time budget and partial behavior
        ranked: List[Dict[str, Any]] = []
        generation_s_total = 0.0
        counts = {
            "lemmas_total": len(lemmas),
            "existing_loaded": len(existing_map),
            "generated": 0,
            "fallback_defaults": 0,
            "skipped_due_to_budget": 0,
        }

        for lemma in lemmas:
            now = time.time()
            elapsed = now - started_at
            have = existing_map.get(lemma)
            md: Dict[str, Any]
            if have and have.get("is_complete"):
                md = have
            else:
                # If budget remains, attempt to load/generate; otherwise fallback defaults
                if elapsed < time_budget_s:
                    gen_t0 = time.time()
                    try:
                        md = load_or_generate_lemma_metadata(
                            lemma=lemma,
                            target_language_code=target_language_code,
                            generate_if_incomplete=True,
                        )
                        counts["generated"] += 1
                    except AuthenticationRequiredForGenerationError:
                        md = {
                            "lemma": lemma,
                            "translations": [],
                            "etymology": "",
                            "commonality": 0.5,
                            "guessability": 0.5,
                            "part_of_speech": "unknown",
                            "is_complete": False,
                        }
                        counts["fallback_defaults"] += 1
                    except Exception as e:
                        logger.warning(
                            f"Failed to load/generate metadata for '{lemma}': {e}"
                        )
                        md = {
                            "lemma": lemma,
                            "translations": [],
                            "etymology": "",
                            "commonality": 0.5,
                            "guessability": 0.5,
                            "part_of_speech": "unknown",
                            "is_complete": False,
                        }
                        counts["fallback_defaults"] += 1
                    finally:
                        generation_s_total += time.time() - gen_t0
                else:
                    counts["skipped_due_to_budget"] += 1
                    md = {
                        "lemma": lemma,
                        "translations": [],
                        "etymology": "",
                        "commonality": 0.5,
                        "guessability": 0.5,
                        "part_of_speech": "unknown",
                        "is_complete": False,
                    }
                    counts["fallback_defaults"] += 1

            # Build summary item; include a couple of examples/mnemonics for UX
            example_usage = md.get("example_usage") or []
            if isinstance(example_usage, list):
                example_usage = example_usage[:2]
            mnemonics = md.get("mnemonics") or []
            if isinstance(mnemonics, list):
                mnemonics = mnemonics[:2]

            item = {
                "lemma": md.get("lemma", lemma),
                "translations": md.get("translations", []) or [],
                "etymology": md.get("etymology") or "",
                "commonality": md.get("commonality"),
                "guessability": md.get("guessability"),
                "part_of_speech": md.get("part_of_speech", "unknown") or "unknown",
                "example_usage": example_usage,
                "mnemonics": mnemonics,
                "is_complete": md.get("is_complete", False),
            }
            item["difficulty_score"] = _difficulty_score(item)
            ranked.append(item)

        durations["lemma_warmup_total_s"] = (
            durations.get("bulk_fetch_s", 0.0) + generation_s_total
        )
        durations["generation_s"] = generation_s_total

        # Sort by difficulty desc and take top N
        ranked.sort(key=lambda x: x.get("difficulty_score", 0.0), reverse=True)
        top_items = ranked[:top_n]

        durations["total_s"] = time.time() - started_at
        return (
            jsonify(
                {
                    "lemmas": top_items,
                    "meta": {
                        "total_candidates": len(ranked),
                        "returned": len(top_items),
                        "durations": durations,
                        "partial": counts["skipped_due_to_budget"] > 0,
                        "counts": counts,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": safe_error_message(e, "learn_sourcefile_summary_api")}), 500


# Maximum time budget for the /generate endpoint to ensure we return before
# Vercel's function timeout kills the request (which causes CORS errors
# because Vercel's termination response lacks CORS headers).
# With maxDuration=300 in vercel.json, we use 280s to leave margin for response.
GENERATE_TIME_BUDGET_S = 280.0


@learn_api_bp.route(
    "/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate",
    methods=["POST"],
)
@api_auth_required
def learn_sourcefile_generate_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Generate/persist a batch of sentences and audio for provided lemmas.

    Always persists to Sentence/SentenceLemma with provenance="learn" and
    generation_metadata containing source_context, used_lemmas, order_index, tts_voice.

    Request JSON: {
        "lemmas": list[str],
        "num_sentences": int=5,
        "language_level": str|null,
        "skip_audio": bool=False  # When True, skip TTS generation for faster response
    }
    Response JSON: {
        "sentences": [{
            sentence, translation, used_lemmas, language_level?,
            audio_data_url,  # null if skip_audio=True and no cached audio
            audio_status,    # "ready" | "pending" (included when skip_audio=True)
            sentence_id      # Always included for ensure-audio calls
        }]
    }

    Note: This endpoint has a time budget to ensure it returns before serverless
    timeouts. If generation takes too long, partial results are returned with
    "timed_out": true in meta.
    """
    t0 = time.time()
    try:
        body = request.get_json(force=True, silent=True) or {}
        if not isinstance(body, dict):
            return (
                jsonify(
                    {
                        "error": "Invalid request",
                        "message": "Request body must be a JSON object",
                    }
                ),
                400,
            )
        lemmas: List[str] = body.get("lemmas") or []
        if not isinstance(lemmas, list) or not all(isinstance(x, str) for x in lemmas):
            return (
                jsonify(
                    {
                        "error": "Invalid request",
                        "message": "'lemmas' must be list[str]",
                    }
                ),
                400,
            )
        num_sentences = body.get("num_sentences") or 5
        try:
            num_sentences = max(1, min(10, int(num_sentences)))
        except Exception:
            num_sentences = 5
        language_level: Optional[str] = body.get("language_level")
        skip_audio: bool = body.get("skip_audio", False) is True

        # Resolve the Sourcefile to get its ID for FK-based lookups
        reuse_t0 = time.time()
        existing_items: List[Dict[str, Any]] = []
        try:
            sourcefile_obj = (
                Sourcefile.select(Sourcefile.id)
                .join(Sourcedir)
                .where(
                    (Sourcedir.slug == sourcedir_slug)
                    & (Sourcedir.target_language_code == target_language_code)
                    & (Sourcefile.slug == sourcefile_slug)
                )
                .get()
            )
            sourcefile_id = sourcefile_obj.id
        except Sourcefile.DoesNotExist:
            return (
                jsonify({"error": "Sourcefile not found"}),
                404,
            )

        try:
            # Use sourcefile_id FK for efficient lookup
            existing_q = (
                Sentence.select()
                .where(
                    (Sentence.target_language_code == target_language_code)
                    & (Sentence.provenance == "learn")
                    & (Sentence.sourcefile_id == sourcefile_id)
                )
                .order_by(Sentence.created_at.asc())
                .limit(num_sentences)
            )

            existing_sentences = list(existing_q)
            reuse_timed_out = False
            for s in existing_sentences:
                selected_variant_id = None
                audio_status = "pending"

                if skip_audio:
                    # When skip_audio=True, only do cheap DB lookup for existing audio
                    variants = list(
                        SentenceAudio.select()
                        .where(SentenceAudio.sentence == s)
                        .order_by(SentenceAudio.created_at)
                        .limit(1)
                    )
                    if variants:
                        selected_variant_id = variants[0].id
                        audio_status = "ready"
                else:
                    # Original behavior: generate audio if missing
                    # Check time budget before expensive audio operations
                    elapsed = time.time() - t0
                    if elapsed >= GENERATE_TIME_BUDGET_S:
                        logger.warning(
                            f"Learn generate: time budget exhausted during reuse processing "
                            f"({elapsed:.1f}s >= {GENERATE_TIME_BUDGET_S}s)"
                        )
                        reuse_timed_out = True
                        # Still include sentence but skip audio generation
                        # Use .limit(1) for efficiency when budget exhausted
                        variants = list(
                            SentenceAudio.select()
                            .where(SentenceAudio.sentence == s)
                            .order_by(SentenceAudio.created_at)
                            .limit(1)
                        )
                    else:
                        try:
                            variants, _ = ensure_sentence_audio_variants(s, n=1)
                        except AuthenticationRequiredForGenerationError:
                            variants = list(
                                SentenceAudio.select()
                                .where(SentenceAudio.sentence == s)
                                .order_by(SentenceAudio.created_at)
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to ensure audio variants for sentence id={s.id}: {e}"
                            )
                            variants = list(
                                SentenceAudio.select()
                                .where(SentenceAudio.sentence == s)
                                .order_by(SentenceAudio.created_at)
                            )

                        # If still missing, auto-generate a minimal fallback when authenticated
                        # (only if we haven't timed out)
                        if not variants and not reuse_timed_out:
                            try:
                                from config import (
                                    PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES,
                                )

                                if getattr(g, "user", None):
                                    try:
                                        fallback_n = max(
                                            1,
                                            int(
                                                PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES
                                            ),
                                        )
                                    except Exception:
                                        fallback_n = 1
                                    try:
                                        # Use default enforce_auth=True, requires g.user
                                        variants, _ = ensure_sentence_audio_variants(
                                            s, n=fallback_n
                                        )
                                    except Exception as gen_err:
                                        logger.warning(
                                            f"Auto-generated audio fallback failed for sentence id={s.id}: {gen_err}"
                                        )
                            except Exception:
                                # If config import fails, just continue without auto-gen
                                pass

                    if not variants:
                        logger.warning(
                            f"Persisted sentence id={s.id} has no sentence_audio variants; continuing without audio"
                        )
                    else:
                        # Pin a specific variant to avoid random selection across range requests
                        selected_variant_id = variants[0].id
                        audio_status = "ready"

                meta = s.generation_metadata or {}
                used_lemmas = meta.get("used_lemmas") or []
                item = {
                    "sentence": s.sentence,
                    "translation": s.translation,
                    "used_lemmas": used_lemmas,
                    "language_level": s.language_level,
                    "audio_data_url": (
                        f"/api/lang/sentence/{target_language_code}/{s.id}/audio?variant_id={selected_variant_id}"
                        if selected_variant_id is not None
                        else None
                    ),
                    "sentence_id": s.id,
                }
                # Include audio_status when skip_audio=True for frontend tracking
                if skip_audio:
                    item["audio_status"] = audio_status
                existing_items.append(item)
        except Exception as e:
            # If DB is not migrated yet or JSON operators unsupported, skip reuse gracefully
            logger.warning(
                f"Learn reuse query failed; proceeding without reuse. Reason: {e}"
            )

        remaining = max(0, num_sentences - len(existing_items))

        # Note: @api_auth_required ensures user is authenticated, so no anonymous fallback needed

        llm_duration = 0.0
        audio_duration = 0.0
        new_items: List[Dict[str, Any]] = []
        timed_out = False
        skipped_due_to_timeout = 0

        if remaining > 0:
            # Check time budget before starting expensive LLM generation
            elapsed = time.time() - t0
            if elapsed >= GENERATE_TIME_BUDGET_S:
                logger.warning(
                    f"Learn generate: time budget exhausted before LLM call ({elapsed:.1f}s >= {GENERATE_TIME_BUDGET_S}s)"
                )
                timed_out = True
                skipped_due_to_timeout = (
                    remaining  # Track how many we couldn't generate
                )
                remaining = 0  # Skip generation entirely

        if remaining > 0:
            # Call LLM once to generate a set of sentences (we'll slice to 'remaining')
            llm_t0 = time.time()
            target_language_name = get_language_name(target_language_code)
            prompt_path = get_prompt_template_path("generate_sentence_flashcards")
            llm_out, extra = generate_gpt_from_template(
                client=anthropic_client,
                prompt_template=prompt_path,
                context_d={
                    "target_language_name": target_language_name,
                    "already_words": lemmas,
                },
                response_json=True,
                max_tokens=4096,
                verbose=0,
            )
            llm_duration = time.time() - llm_t0

            raw_sentences = []
            if isinstance(llm_out, dict):
                raw_sentences = llm_out.get("sentences") or []
            if not isinstance(raw_sentences, list):
                raise ValueError("LLM did not return a valid 'sentences' list")

            raw_sentences = raw_sentences[:remaining]

            audio_t0 = time.time()
            order_start = len(existing_items)
            for idx, s in enumerate(raw_sentences):
                # Check time budget before processing each sentence
                elapsed = time.time() - t0
                if elapsed >= GENERATE_TIME_BUDGET_S:
                    logger.warning(
                        f"Learn generate: time budget exhausted during sentence processing "
                        f"({elapsed:.1f}s >= {GENERATE_TIME_BUDGET_S}s), "
                        f"processed {idx}/{len(raw_sentences)} sentences"
                    )
                    timed_out = True
                    skipped_due_to_timeout = len(raw_sentences) - idx
                    break

                sentence_text = (s.get("sentence") or "").strip()
                translation_text = (s.get("translation") or "").strip()
                used_lemmas = s.get("lemma_words") or []
                cefr = s.get("language_level") or language_level

                if not sentence_text or not translation_text:
                    raise ValueError("LLM produced an empty sentence or translation")

                generation_metadata = {
                    "used_lemmas": used_lemmas,
                    "used_wordforms": [],
                    "order_index": order_start + idx,
                    "prompt_version": "generate_sentence_flashcards@v1",
                    "source_context": {
                        "type": "sourcefile",
                        "slug": sourcefile_slug,
                        "sourcedir_slug": sourcedir_slug,
                    },
                }

                # Persist sentence + audio (sourcefile_id resolved at start of function)
                db_sentence, meta = generate_sentence(
                    target_language_code=target_language_code,
                    sentence=sentence_text,
                    translation=translation_text,
                    lemma_words=used_lemmas,
                    language_level=cefr,
                    provenance="learn",
                    generation_metadata=generation_metadata,
                    sourcefile_id=sourcefile_id,
                )

                sent_id = meta.get("id") or db_sentence.id
                if not sent_id:
                    raise ValueError(
                        "Failed to persist generated sentence (missing id)"
                    )

                selected_variant_id = None
                audio_status = "pending"

                if skip_audio:
                    # Skip audio generation entirely for new sentences when skip_audio=True
                    pass
                else:
                    # Original behavior: generate audio
                    try:
                        variants, _ = ensure_sentence_audio_variants(db_sentence, n=1)
                    except AuthenticationRequiredForGenerationError:
                        variants = []
                    except Exception as ensure_err:
                        logger.warning(
                            f"Failed to ensure audio variants for generated sentence id={sent_id}: {ensure_err}"
                        )
                        variants = []

                    # If variants are missing, auto-generate a minimal fallback when authenticated
                    if not variants:
                        try:
                            from config import (
                                PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES,
                            )

                            if getattr(g, "user", None):
                                try:
                                    fallback_n = max(
                                        1,
                                        int(
                                            PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES
                                        ),
                                    )
                                except Exception:
                                    fallback_n = 1
                                try:
                                    # Use default enforce_auth=True, requires g.user
                                    variants, _ = ensure_sentence_audio_variants(
                                        db_sentence, n=fallback_n
                                    )
                                except Exception as gen_err:
                                    logger.warning(
                                        f"Auto-generated audio fallback failed for generated sentence id={sent_id}: {gen_err}"
                                    )
                        except Exception:
                            # If config import fails, just continue without auto-gen
                            pass

                    if variants:
                        selected_variant_id = variants[0].id
                        audio_status = "ready"

                item = {
                    "sentence": sentence_text,
                    "translation": translation_text,
                    "used_lemmas": used_lemmas,
                    "language_level": cefr,
                    "audio_data_url": (
                        f"/api/lang/sentence/{target_language_code}/{sent_id}/audio?variant_id={selected_variant_id}"
                        if selected_variant_id is not None
                        else None
                    ),
                    "sentence_id": sent_id,
                }
                # Include audio_status when skip_audio=True for frontend tracking
                if skip_audio:
                    item["audio_status"] = audio_status
                new_items.append(item)

            audio_duration = time.time() - audio_t0

        total_duration = time.time() - t0
        sentences_out = existing_items + new_items

        response_meta = {
            "reused_count": len(existing_items),
            "new_count": len(new_items),
            "durations": {
                "reuse_s": time.time() - reuse_t0,
                "llm_s": llm_duration,
                "audio_total_s": audio_duration,
                "total_s": total_duration,
            },
        }
        if timed_out:
            response_meta["timed_out"] = True
            response_meta["skipped_due_to_timeout"] = skipped_due_to_timeout

        return (
            jsonify(
                {
                    "sentences": sentences_out,
                    "meta": response_meta,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": safe_error_message(e, "learn_sourcefile_generate_api")}), 500


@learn_api_bp.route("/sentence/<int:sentence_id>/ensure-audio", methods=["POST"])
@api_auth_required
def ensure_sentence_audio_api(sentence_id: int):
    """Ensure audio exists for a sentence, generating if needed.

    Requires authentication. This endpoint is designed for lazy audio loading:
    - Returns existing audio immediately if cached
    - Generates audio on-demand if missing (~3-8s for generation)

    Response: {
        "audio_data_url": "/api/lang/sentence/{lang}/{id}/audio?variant_id=...",
        "generated": true/false,  # Whether audio was freshly generated
        "duration_s": 3.5         # Time taken (for observability)
    }

    Error responses:
    - 401: Unauthorized (handled by @api_auth_required decorator)
    - 404: Sentence not found
    - 500: Audio generation failed
    """
    t0 = time.time()
    try:
        # Scope DB reads to release connection before slow TTS generation.
        # This prevents holding a pool slot during the 3-8s TTS call.
        with database.connection_context():
            try:
                sentence = Sentence.get_by_id(sentence_id)
            except Sentence.DoesNotExist:
                return (
                    jsonify(
                        {
                            "error": "Sentence not found",
                            "message": f"No sentence with id={sentence_id}",
                        }
                    ),
                    404,
                )

            target_language_code = sentence.target_language_code

            # Check for existing audio variants (cheap DB lookup)
            existing_variants = list(
                SentenceAudio.select()
                .where(SentenceAudio.sentence == sentence)
                .order_by(SentenceAudio.created_at)
                .limit(1)
            )
        # Connection released here - TTS runs without holding pool slot

        if existing_variants:
            # Audio already exists - return it
            selected_variant_id = existing_variants[0].id
            duration_s = time.time() - t0
            return (
                jsonify(
                    {
                        "audio_data_url": f"/api/lang/sentence/{target_language_code}/{sentence_id}/audio?variant_id={selected_variant_id}",
                        "generated": False,
                        "duration_s": round(duration_s, 3),
                    }
                ),
                200,
            )

        # Generate audio (single TTS call, typically 3-8s)
        # Note: @api_auth_required decorator ensures user is authenticated
        try:
            variants, created_count = ensure_sentence_audio_variants(sentence, n=1)
        except AuthenticationRequiredForGenerationError:
            # Shouldn't happen with @api_auth_required decorator, but handle defensively
            logger.warning(f"Unexpected auth error for authenticated user on sentence id={sentence_id}")
            duration_s = time.time() - t0
            return (
                jsonify(
                    {
                        "error": "Authentication required",
                        "message": "Authentication required to generate audio.",
                        "duration_s": round(duration_s, 3),
                    }
                ),
                401,
            )
        except Exception as gen_err:
            logger.exception(f"Failed to generate audio for sentence id={sentence_id}")
            duration_s = time.time() - t0
            return (
                jsonify(
                    {
                        "error": "Audio generation failed",
                        "message": str(gen_err),
                        "duration_s": round(duration_s, 3),
                    }
                ),
                500,
            )

        if not variants:
            duration_s = time.time() - t0
            return (
                jsonify(
                    {
                        "error": "Audio generation failed",
                        "message": "No audio variants were created.",
                        "duration_s": round(duration_s, 3),
                    }
                ),
                500,
            )

        selected_variant_id = variants[0].id
        duration_s = time.time() - t0
        return (
            jsonify(
                {
                    "audio_data_url": f"/api/lang/sentence/{target_language_code}/{sentence_id}/audio?variant_id={selected_variant_id}",
                    "generated": created_count > 0,
                    "duration_s": round(duration_s, 3),
                }
            ),
            200,
        )

    except Exception as e:
        duration_s = time.time() - t0
        return (
            jsonify(
                {
                    "error": safe_error_message(e, f"ensure_sentence_audio_api sentence_id={sentence_id}"),
                    "duration_s": round(duration_s, 3),
                }
            ),
            500,
        )
