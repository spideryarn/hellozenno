---
Date: 2025-09-14
Duration: ~15–20 min (approx.)
Type: Decision-making
Status: Active
Related Docs: 
- `docs/planning/250914c_multilingual_word_segmentation_for_hover_links.md`
---

## Context & Goals

Adopt a single, robust multilingual word segmentation system to power inline hover-links across all target languages (Thai, Chinese, Japanese, Korean, and space-delimited languages) without developer/user setup. Clarify whether language-specific tokenizers ("plugins") are required, and whether to standardize on one approach.

## Key Background

- Current backend implements ICU-based segmentation via PyICU, with optional Thai plugin (PyThaiNLP) and a known-word Aho–Corasick fast path behind flags.
- User preference: "I don't want fallbacks, I just want one system that works well."
- Prior issue: Thai recognition was empty under regex \b boundaries; ICU+normalization resolved it; Thai plugin further improved coverage in local tests.

## Main Discussion

### ICU vs. Plugins (jieba/SudachiPy/etc.)
- Plugins are not part of ICU; they are separate tokenizers (e.g., jieba for Chinese, SudachiPy for Japanese, PyThaiNLP for Thai).
- ICU (PyICU) already includes dictionary-based word segmentation for Chinese and Japanese (and Thai), and serves as a single cross-language solution.
- Therefore, plugins are not required for baseline correctness for zh/ja if ICU is present.

#### Clarification (emphasis)
> "Are the plugins related to ICU or something else? I don't want fallbacks, I just want one system that works well."

- Answer: Plugins are separate libraries, not ICU. They can replace or augment ICU but introduce variance and extra setup. If we want one system, we choose ICU-only.

#### TL;DR
- Treat ICU as the single, universal segmenter across languages.
- Only consider plugins later for targeted accuracy boosts, explicitly opted-in.

### One System vs. Fallbacks
- The user wants a single system without fallbacks. The proposed direction is ICU-only across all languages.
- Enforce fail-fast on startup if PyICU is missing to avoid silent degradation.
- Keep optional modules (PyThaiNLP, jieba, SudachiPy) disabled by default; use only for targeted accuracy wins if explicitly enabled later.

### Coverage and Tests
- ICU covers: zh, ja (dictionary-based), th, ko, and all space-delimited languages.
- Existing tests expect ICU availability; zh/ja test currently skips only if ICU dicts are missing in the environment. With a standard ICU install, tests pass.
- If we lock to ICU-only and add a startup check, we can remove the zh/ja skip in future.

### Known-word Fast Path (Aho–Corasick)
- Not a tokenizer; complements segmentation by matching known DB wordforms in NFC.
- Helpful for multi-morpheme entries that span segmentation boundaries. Feature-flagged; optional to keep disabled by default.

### Normalization & Offsets
- NFC normalization is enforced where offsets are computed; offset parity tests pass.
- Keep the exact normalized text returned to the frontend to preserve index parity.

## Alternatives Considered

- Per-language plugins as the default (jieba, SudachiPy, PyThaiNLP):
  - Pros: Potentially higher lexical accuracy per language.
  - Cons: Heavier dependencies, dictionaries/models, operational complexity, inconsistent behavior.
- Legacy regex word-boundary recognition:
  - Fails for languages without spaces and under-recognizes in Thai/CJK.
- AC-only (without segmentation):
  - Fast for known-word matching but not a tokenizer; risks false positives and boundary ambiguity.

## Decisions Made (tentative)

- Standardize on ICU-only segmentation across all languages.
- Add a startup check to require PyICU; fail-fast if unavailable.
- Keep language-specific tokenizers and AC fast path available but disabled by default.
- Maintain current API shape (`recognized_words`) and NFC offset invariants.

## Open Questions

- Environments without system ICU (e.g., serverless): Do we vendor or ensure compatible wheels so ICU is always available?
- Do we want stricter tests (remove zh/ja skip) once ICU availability is guaranteed in CI/CD?
- Which languages beyond Thai need focused accuracy evaluation (zh/ja domain texts, ko, vi)?

## Next Steps

- Enforce ICU-only at runtime: add import-time/startup check and clear error if PyICU is missing.
- Keep env toggles off by default (`SEGMENTATION_*`, `RECOGNITION_KNOWN_WORD_SEARCH`).
- Optional: tighten tests to require zh/ja recognition once CI has ICU dictionaries.
- Manual UI verification for zh/ja routes to confirm multiple hover-links and tooltip behavior.

## Sources & References

- `backend/utils/segmentation.py` — ICU segmentation and optional Thai plugin wiring.
- `backend/utils/vocab_llm_utils.py` — segmentation-first recognition, offset parity, optional AC pass.
- `backend/requirements.txt` — includes `PyICU` (mandatory), `pythainlp` (optional), `pyahocorasick` (optional).
- `backend/tests/backend/test_segmentation_recognition_per_language.py` — per-language recognition smoke.
- `backend/tests/backend/test_offset_parity.py`, `backend/tests/backend/test_segmentation_icu.py` — parity and ICU unit tests.
- Planning doc: `docs/planning/250914c_multilingual_word_segmentation_for_hover_links.md`.

## Related Work

- Thai coverage and debug instrumentation (token intersections) captured in the planning doc above.


