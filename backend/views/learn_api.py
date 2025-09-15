"""Learn flow API endpoints (MVP, ephemeral).

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

from flask import Blueprint, jsonify, request

from loguru import logger

from utils.auth_utils import api_auth_optional
from utils.word_utils import get_sourcefile_lemmas
from utils.store_utils import load_or_generate_lemma_metadata
from utils.exceptions import AuthenticationRequiredForGenerationError
from utils.lang_utils import get_language_name
from utils.prompt_utils import get_prompt_template_path
from utils.vocab_llm_utils import anthropic_client, generate_gpt_from_template
from utils.audio_utils import ensure_audio_data


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

            item = {
                "lemma": md.get("lemma", lemma),
                "translations": md.get("translations", []) or [],
                "etymology": md.get("etymology") or "",
                "commonality": md.get("commonality"),
                "guessability": md.get("guessability"),
                "part_of_speech": md.get("part_of_speech", "unknown") or "unknown",
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
                    "lemmas": [
                        {
                            k: v
                            for k, v in item.items()
                            if k
                            in (
                                "lemma",
                                "translations",
                                "etymology",
                                "commonality",
                                "guessability",
                                "part_of_speech",
                            )
                        }
                        for item in top_items
                    ],
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
    """Generate a batch of sentences and audio for provided lemmas.

    Request JSON: { "lemmas": list[str], "num_sentences": int=10, "language_level": str|null }
    Response JSON: { "sentences": [{ sentence, translation, used_lemmas, language_level?, audio_data_url }] }
    """
    t0 = time.time()
    try:
        body = request.get_json(force=True, silent=True) or {}
        lemmas: List[str] = body.get("lemmas") or []
        if not isinstance(lemmas, list) or not all(isinstance(x, str) for x in lemmas):
            return (
                jsonify({"error": "Invalid request", "message": "'lemmas' must be list[str]"}),
                400,
            )
        num_sentences = body.get("num_sentences") or 10
        try:
            num_sentences = max(1, min(20, int(num_sentences)))
        except Exception:
            num_sentences = 10
        language_level: Optional[str] = body.get("language_level")

        # Call LLM once to generate a set of sentences
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

        sentences_out: List[Dict[str, Any]] = []
        raw_sentences = []
        if isinstance(llm_out, dict):
            raw_sentences = llm_out.get("sentences") or []
        if not isinstance(raw_sentences, list):
            raw_sentences = []

        # Ensure we only take requested number if LLM returned more
        raw_sentences = raw_sentences[:num_sentences]

        # Generate audio per sentence (ephemeral, as data URL)
        audio_total_t0 = time.time()
        for s in raw_sentences:
            sentence_text = (s.get("sentence") or "").strip()
            translation_text = (s.get("translation") or "").strip()
            used_lemmas = s.get("lemma_words") or []
            cefr = s.get("language_level") or language_level

            if not sentence_text or not translation_text:
                continue

            audio_bytes = ensure_audio_data(text=sentence_text, should_add_delays=True, should_play=False, verbose=0)
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            data_url = f"data:audio/mpeg;base64,{audio_b64}"

            sentences_out.append(
                {
                    "sentence": sentence_text,
                    "translation": translation_text,
                    "used_lemmas": used_lemmas,
                    "language_level": cefr,
                    "audio_data_url": data_url,
                }
            )

        audio_duration = time.time() - audio_total_t0

        total_duration = time.time() - t0
        logger.info(
            f"Learn generate: llm_s={llm_duration:.2f}, audio_s={audio_duration:.2f}, total_s={total_duration:.2f}, n={len(sentences_out)}"
        )
        return (
            jsonify(
                {
                    "sentences": sentences_out,
                    "meta": {
                        "durations": {
                            "llm_s": llm_duration,
                            "audio_total_s": audio_duration,
                            "total_s": total_duration,
                        }
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.exception("Error in learn_sourcefile_generate_api")
        return jsonify({"error": "Failed to generate sentences", "message": str(e)}), 500


