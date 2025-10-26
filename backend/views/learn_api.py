"""Learn flow API endpoints (persistent Learn flow).

Routes:
- GET /api/lang/learn/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/summary
- POST /api/lang/learn/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate

Notes:
- No persistence in v1; sentence/audio are generated on-the-fly and returned.
- Lemma metadata may be generated if missing (requires auth per store_utils).
"""

from __future__ import annotations

import base64
import time
from typing import Any, Dict, List, Optional
from peewee import fn

from flask import Blueprint, jsonify, request, g

from loguru import logger

from utils.auth_utils import api_auth_optional
from utils.word_utils import get_sourcefile_lemmas
from utils.store_utils import load_or_generate_lemma_metadata
from utils.exceptions import AuthenticationRequiredForGenerationError
from utils.lang_utils import get_language_name
from utils.prompt_utils import get_prompt_template_path
from utils.vocab_llm_utils import anthropic_client, generate_gpt_from_template
from utils.sentence_utils import generate_sentence
from utils.audio_utils import ensure_sentence_audio_variants
from db_models import Sentence, SentenceAudio


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
@api_auth_optional
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

        # Load/generate metadata and score
        ranked: List[Dict[str, Any]] = []
        t1 = time.time()
        for lemma in lemmas:
            try:
                md = load_or_generate_lemma_metadata(
                    lemma=lemma,
                    target_language_code=target_language_code,
                    generate_if_incomplete=True,
                )
            except AuthenticationRequiredForGenerationError:
                # Fall back to minimal defaults if generation requires auth
                md = {
                    "lemma": lemma,
                    "translations": [],
                    "etymology": "",
                    "commonality": 0.5,
                    "guessability": 0.5,
                    "part_of_speech": "unknown",
                    "is_complete": False,
                }
            except Exception as e:
                logger.warning(f"Failed to load/generate metadata for '{lemma}': {e}")
                md = {
                    "lemma": lemma,
                    "translations": [],
                    "etymology": "",
                    "commonality": 0.5,
                    "guessability": 0.5,
                    "part_of_speech": "unknown",
                    "is_complete": False,
                }

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

        durations["lemma_warmup_total_s"] = time.time() - t1

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
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception("Error in learn_sourcefile_summary_api")
        return jsonify({"error": "Failed to build summary", "message": str(e)}), 500


@learn_api_bp.route(
    "/sourcefile/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/generate",
    methods=["POST"],
)
@api_auth_optional
def learn_sourcefile_generate_api(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Generate/persist a batch of sentences and audio for provided lemmas.

    Always persists to Sentence/SentenceLemma with provenance="learn" and
    generation_metadata containing source_context, used_lemmas, order_index, tts_voice.

    Request JSON: { "lemmas": list[str], "num_sentences": int=10, "language_level": str|null }
    Response JSON: { "sentences": [{ sentence, translation, used_lemmas, language_level?, audio_data_url }] }
    """
    t0 = time.time()
    try:
        body = request.get_json(force=True, silent=True) or {}
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
        num_sentences = body.get("num_sentences") or 10
        try:
            num_sentences = max(1, min(20, int(num_sentences)))
        except Exception:
            num_sentences = 10
        language_level: Optional[str] = body.get("language_level")

        # First reuse any existing persisted sentences for this sourcefile
        reuse_t0 = time.time()
        existing_items: List[Dict[str, Any]] = []
        try:
            # Match by generation_metadata.source_context.slug == sourcefile_slug
            # and source_context.type == 'sourcefile'
            slug_expr = fn.json_extract_path_text(
                Sentence.generation_metadata, "source_context", "slug"
            )
            type_expr = fn.json_extract_path_text(
                Sentence.generation_metadata, "source_context", "type"
            )

            existing_q = (
                Sentence.select()
                .where(
                    (Sentence.target_language_code == target_language_code)
                    & (Sentence.provenance == "learn")
                    & (slug_expr == sourcefile_slug)
                    & (type_expr == "sourcefile")
                )
                .order_by(Sentence.created_at.asc())
                .limit(num_sentences)
            )

            existing_sentences = list(existing_q)
            for s in existing_sentences:
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
                if not variants:
                    try:
                        from config import PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES

                        if getattr(g, "user", None):
                            try:
                                fallback_n = max(
                                    1, int(PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES)
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
                    selected_variant_id = None
                else:
                    # Pin a specific variant to avoid random selection across range requests
                    selected_variant_id = variants[0].id
                meta = s.generation_metadata or {}
                used_lemmas = meta.get("used_lemmas") or []
                existing_items.append(
                    {
                        "sentence": s.sentence,
                        "translation": s.translation,
                        "used_lemmas": used_lemmas,
                        "language_level": s.language_level,
                        "audio_data_url": (
                            f"/api/lang/sentence/{target_language_code}/{s.id}/audio?variant_id={selected_variant_id}"
                            if selected_variant_id is not None
                            else None
                        ),
                    }
                )
        except Exception as e:
            # If DB is not migrated yet or JSON operators unsupported, skip reuse gracefully
            logger.warning(
                f"Learn reuse query failed; proceeding without reuse. Reason: {e}"
            )

        remaining = max(0, num_sentences - len(existing_items))

        # If generation is required but the user is not authenticated, return fast
        # to avoid long-running operations (LLM/audio) that can hit platform timeouts.
        if remaining > 0 and not getattr(g, "user", None):
            total_duration = time.time() - t0
            return (
                jsonify(
                    {
                        "error": "Authentication required to generate sentences",
                        "message": "Authentication required to generate sentences",
                        "description": "Please log in to generate new practice sentences.",
                        "authentication_required_for_generation": True,
                        "sentences": existing_items,
                        "meta": {
                            "reused_count": len(existing_items),
                            "new_count": 0,
                            "durations": {
                                "reuse_s": time.time() - reuse_t0,
                                "llm_s": 0.0,
                                "audio_total_s": 0.0,
                                "total_s": total_duration,
                            },
                        },
                    }
                ),
                401,
            )

        llm_duration = 0.0
        audio_duration = 0.0
        new_items: List[Dict[str, Any]] = []
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
                    },
                }

                # Persist sentence + audio
                db_sentence, meta = generate_sentence(
                    target_language_code=target_language_code,
                    sentence=sentence_text,
                    translation=translation_text,
                    lemma_words=used_lemmas,
                    language_level=cefr,
                    provenance="learn",
                    generation_metadata=generation_metadata,
                )

                sent_id = meta.get("id") or db_sentence.id
                if not sent_id:
                    raise ValueError(
                        "Failed to persist generated sentence (missing id)"
                    )

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
                        from config import PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES

                        if getattr(g, "user", None):
                            try:
                                fallback_n = max(
                                    1, int(PUBLIC_AUTO_GENERATE_SENTENCE_AUDIO_SAMPLES)
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

                # Pin a specific variant to avoid random selection across range requests
                selected_variant_id = variants[0].id if variants else None
                new_items.append(
                    {
                        "sentence": sentence_text,
                        "translation": translation_text,
                        "used_lemmas": used_lemmas,
                        "language_level": cefr,
                        "audio_data_url": (
                            f"/api/lang/sentence/{target_language_code}/{sent_id}/audio?variant_id={selected_variant_id}"
                            if selected_variant_id is not None
                            else None
                        ),
                    }
                )

            audio_duration = time.time() - audio_t0

        total_duration = time.time() - t0
        sentences_out = existing_items + new_items

        return (
            jsonify(
                {
                    "sentences": sentences_out,
                    "meta": {
                        "reused_count": len(existing_items),
                        "new_count": len(new_items),
                        "durations": {
                            "reuse_s": time.time() - reuse_t0,
                            "llm_s": llm_duration,
                            "audio_total_s": audio_duration,
                            "total_s": total_duration,
                        },
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception("Error in learn_sourcefile_generate_api")
        return (
            jsonify({"error": "Failed to generate sentences", "message": str(e)}),
            500,
        )
