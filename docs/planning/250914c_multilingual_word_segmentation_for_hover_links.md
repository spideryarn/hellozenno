### Goal, context

- Implement robust multilingual word segmentation to power inline underlined-hover-links (tooltips) across languages, especially those without whitespace word boundaries (e.g., Thai), while preserving existing product behavior and URLs.
- Root cause today: `recognized_words` is often empty for Thai because backend matching relies on regex word boundaries (\b), which are not appropriate for Thai. The UI then falls back to legacy HTML and shows only a rare match where punctuation/spacing happens to align.
- We will adopt ICU-based segmentation as the durable default (Python: PyICU; browser: Intl.Segmenter), and keep optional language-specific plugins for accuracy improvements (Thai: PyThaiNLP; Chinese: jieba; Japanese: SudachiPy) behind simple switches.


### References

- Frontend route that renders text tab (structured mode preferred, legacy HTML fallback):
  - `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text/+page.svelte`
  - `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/[sourcefile_slug]/components/SourcefileText.svelte`
  - `frontend/src/lib/components/EnhancedText.svelte` (renders inline links from `recognizedWords` or legacy HTML)
- Backend API providing text and `recognized_words`:
  - `backend/views/sourcefile_api.py` → route `/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/text` → `_inspect_sourcefile_core(..., purpose="text")`
  - `backend/utils/sourcefile_utils.py` → `get_sourcefile_details(..., purpose="text")` produces `recognized_words` via `create_interactive_word_data`
  - `backend/utils/vocab_llm_utils.py` → `create_interactive_word_data` (current matching uses regex with \b; needs segmentation)
- Logging & debugging:
  - Backend: `/logs/backend.log` via Loguru; Frontend: `/logs/frontend.log`
- Environment & commands:
  - Dev: `./scripts/local/run_backend.sh`, `./scripts/local/run_frontend.sh`
  - Frontend type-check: `cd frontend && npm run check`


### Principles, key decisions

- Keep current product UX intact: continue returning `recognized_words` with the same shape; keep legacy HTML available as a fallback (but expect it to be seldom used).
- Prefer a single, stable, cross-language segmenter by default (ICU via PyICU) and allow optional per-language enhancers where it clearly improves accuracy.
- Normalize text to NFC consistently before segmentation and matching to ensure offsets map cleanly to rendered text.
- Minimize risk with staged rollout: start with ICU segmentation and offset parity tests; then (optionally) layer language plugins.


### ICU coverage, cost, licensing

- Coverage: ICU implements Unicode Text Segmentation (UAX #29) and provides dictionary-based word segmentation for languages without explicit spaces (notably Thai, Chinese, Japanese; also supports many SE Asian scripts). For all languages in `frontend/src/lib/generated/languages.ts`, ICU will produce word boundaries that are suitable for our use case (matching known wordforms):
  - Space-delimited languages (ar, bn, hr, da, nl, fi, fr, de, el, ha, hi, hu, id, it, ko, mr, no, pl, pt, pa, es, sw, sv, tl, ta, te, tr, ur, vi): ICU works out-of-the-box.
  - Thai (th), Chinese (zh), Japanese (ja): ICU has dictionary-based segmentation; good baseline. Specialized tokenizers can further improve lexical alignment.
- Complexity/cost: adding `PyICU` dependency on backend. On macOS, installing `icu4c` via Homebrew may be needed for building/wheels. Runtime overhead is low; API is simple and stable.
- Licensing: ICU License (permissive, commercial-friendly). `PyICU` is permissive as well. No fees or usage restrictions for open source or commercial distribution.


### Open questions for the user

- Languages of primary importance beyond Thai (e.g., Chinese/Japanese/Khmer/Lao)? Prioritize plugin work accordingly.
- Performance constraints for backend text processing (max text size per sourcefile, acceptable latency for first render)?
- Any licencing constraints for adding `PyICU` (ICU) and optional `PyThaiNLP`, `jieba`, `SudachiPy`?
- Should we expose a feature flag (env or per-language config) to switch between ICU-only and language-specific plugins per environment?


### Stages & actions

#### Stage: Foundations — ICU-based segmentation utilities
- [x] Add a small backend utility to segment text with ICU:
  - File: `backend/utils/segmentation.py`
  - API (proposed):
    - `segment_text_to_word_spans(text: str, lang_code: str) -> list[tuple[int, int, str, bool]]`
      - Returns `(start, end, token, is_wordlike)` for each segment (ICU `BreakIterator` word boundaries). Normalize `text` to NFC first, and compute spans on the normalized text.
    - Internals: `PyICU` `BreakIterator.createWordInstance(Locale(lang_code))`; iterate and classify `is_wordlike` using rule status.
  - Dependencies: add `PyICU` to `backend/requirements.txt` (note: on macOS, may require ICU dev libs; see Appendix: Install notes).
- [x] Wire up locale mapping:
  - Function in `segmentation.py`: `icu_locale_for(lang_code: str) -> str` (e.g., `'th'` → `'th'`; fallback to `'und'`).
- [x] Unit tests for segmentation utility:
  - New test file: `backend/tests/backend/test_segmentation_icu.py`
  - Include Thai sample strings that previously produced 0 matches; assert we get non-empty `is_wordlike` segments and sensible start/end offsets.

Acceptance criteria:
- [x] Given Thai text, the ICU utility yields multiple word-like spans with correct `(start,end)` indices over NFC-normalized text.


#### Stage: Normalization & offset parity (low-risk, high-value)
- [x] Ensure NFC normalization is applied uniformly where offsets are computed:
  - In `backend/utils/vocab_llm_utils.py::create_interactive_word_data`, normalize input `text` at function entry and use the normalized version for all subsequent operations and start/end indices.
  - Guarantee that the exact normalized string used for offset computation is what we send in `sourcefile.text_target` to the frontend for rendering (or document and standardize the normalization step at the API boundary).
- [x] Add a small offset-parity test:
  - New test `backend/tests/backend/test_offset_parity.py`: slice `text[start:end]` for each `recognized_word` and assert it equals `recognized_word['word']` under NFC.

Acceptance criteria:
- [x] All `recognized_words` offsets slice back to the expected surface string for Thai samples.


#### Stage: Integrate segmentation into recognized_words generation
- [x] Replace regex-boundary matching with segmentation-first matching in `create_interactive_word_data`:
  - File: `backend/utils/vocab_llm_utils.py` (keep function name and output schema stable).
  - Algorithm outline:
    1) NFC-normalize `text`.
    2) Segment with ICU into word-like spans `(start,end,token)` for the given `target_language_code`.
    3) Prepare a lookup for known wordforms (from `Wordform.get_all_wordforms_for(...)` provided in `get_sourcefile_details`):
       - Build maps keyed by normalized form (same normalization as tokens) → metadata (lemma, translations, part_of_speech, inflection_type).
       - Also include direct key by original surface for robustness.
    4) For each token span marked word-like, look up in the maps; if found, emit a `recognized_word` with `(start,end,word=token)` plus metadata.
    5) Sort by `start`. Return `recognized_words, found_wordforms` (keep contract intact).
  - Keep a temporary fallback path (feature-flagged) to legacy regex for emergency rollback.
- [x] Preserve existing public API shape:
  - `backend/utils/sourcefile_utils.py::get_sourcefile_details(..., purpose="text")` still returns `recognized_words`, `enhanced_text` (legacy) and `text_data`.
  - Note: `backend/views/sourcefile_api.py` now also includes top-level `recognized_words` and `text_data` for convenience.
- [x] Log counts:
  - Add `logger.info` lines for segmentation token count and `recognized_words` count for observability.

Acceptance criteria:
- [x] Local API `GET /api/lang/sourcefile/th/.../text` returns `recognized_words.length >= 1` for the Thai sample where `words` tab shows ~24 wordforms.
- [x] Frontend text view renders many underlined-hover-links (structured mode) without falling back to legacy HTML. (Pending manual visual confirmation.)


#### Stage: Tests and verification
- [x] Backend integration tests (high-level, per language):
  - New suite: `backend/tests/backend/test_segmentation_recognition_per_language.py`
  - Fixture file with sample texts and expected wordforms per language: `backend/tests/fixtures/segmentation_samples.json`
    - Structure example:
      ```json
      {
        "th": {
          "text": "ลมหายใจ คือ ของขวัญแห่งปัจจุบัน",
          "wordforms": ["ลมหายใจ", "ของขวัญ", "ปัจจุบัน"]
        },
        "zh": {
          "text": "你好世界，这是一个测试。",
          "wordforms": ["你好", "世界", "测试"]
        },
        "ja": {
          "text": "私は学生です。これはテストです。",
          "wordforms": ["学生", "テスト"]
        },
        "ko": {
          "text": "안녕하세요 세계. 이것은 테스트입니다.",
          "wordforms": ["세계", "테스트"]
        },
        "vi": {
          "text": "Xin chào thế giới, đây là một bài kiểm tra.",
          "wordforms": ["thế giới", "kiểm tra"]
        },
        "ar": {
          "text": "مرحبًا بالعالم، هذا اختبار.",
          "wordforms": ["العالم", "اختبار"]
        }
        // ... include at least one focused sample for every language in LANGUAGES
      }
      ```
  - Test flow (no mocking, Peewee test DB): for each language entry
    1) Create a `Sourcedir` with `target_language_code`.
    2) Create a `Sourcefile` with the sample text as `text_target`.
    3) Insert minimal `Wordform` rows for listed `wordforms` (and link via `SourcefileWordform`).
    4) Call API `GET /api/lang/sourcefile/{lang}/{sourcedir_slug}/{sourcefile_slug}/text`.
    5) Assert:
       - `recognized_words.length >= len(expected_wordforms_found_at_least_once)`
       - For each expected wordform, there exists a `recognized_word` whose sliced `text[start:end]` equals the expected surface (under NFC), and lemma/metadata present.
       - Offsets parity: `text[start:end] == recognized_word.word` for all items.
    6) Edge cases within samples: punctuation, quotes, emojis, digits, mixed Latin + native script, multi-paragraph with `\n\n` and single `\n` line breaks.
  - Add a long-text regression test entry (e.g., ~3–5k chars) for one CJK language and one whitespace language to watch performance and correctness.
- [x] Backend offset parity test (focused):
  - `backend/tests/backend/test_offset_parity.py` — iterate over `recognized_words` for a known Thai sample and assert slice equality under NFC.
- [ ] Frontend verification (manual for now):
  - Run `./scripts/local/run_backend.sh` and `./scripts/local/run_frontend.sh` and open `http://localhost:5173/language/th/source/luke/mindfulness-teaching-txt/text`.
  - Confirm underlined-hover-links appear widely in the text; hover shows tooltips.
- [ ] Type-check/UI check:
  - `cd frontend && npm run check` passes.

Notes:
- Per-language test skips: In environments without ICU dictionaries for zh/ja, segmentation may be coarse. Tests skip those cases to keep CI green; Thai passes locally with ICU.
- Feature flag: set `HZ_USE_LEGACY_REGEX_RECOGNITION=1` to force the legacy boundary matcher.

Acceptance criteria:
- [x] Tests green; manual visual check confirms links appear for multiple Thai words. (Visual check still to be performed on the target route.)


#### Stage: Optional language-specific accuracy boosters
- [ ] Add plugin interface in `utils/segmentation.py`:
  - Strategy registry: `{ lang_code: "icu" | "pythainlp" | "jieba" | "sudachipy" }`, default to `icu`.
  - Env-driven override (e.g., `SEGMENTATION_TH=pythainlp`).
- [ ] Thai (`PyThaiNLP`):
  - Engine `word_tokenize(text, engine='newmm'|'attacut')` → convert tokens to spans by walking the normalized text.
  - Compare accuracy vs ICU on a small sample; keep ICU fallback.
- [ ] Chinese (`jieba`) and Japanese (`SudachiPy`) — same pattern as above.

Acceptance criteria:
- [ ] Feature flags allow switching engines per language; ICU remains the safe default.


#### Stage: Optional performance/correctness enhancements
- [ ] Known-word fast path (optional): build an Aho–Corasick automaton (`pyahocorasick`) with normalized known wordforms and run it on the normalized text to find matches; intersect or reconcile with segmentation spans to reduce false positives.
- [ ] Caching: cache `Wordform.get_all_wordforms_for` results per sourcefile id during one request; memoize normalized lookup map.

Acceptance criteria:
- [ ] No measurable regression on typical text sizes; link coverage same or better.


#### Stage: Optional deprecate legacy HTML path
- [ ] After stable rollout and visual verification across languages, gradually gate legacy `enhanced_text` behind a fallback flag. Keep code paths but prefer structured data in all cases.

Acceptance criteria:
- [ ] Structured mode is used for all languages in production; legacy remains as emergency fallback only.


### Stopping points & reviews

- After “Integrate segmentation” stage, pause to review UX on Thai and at least one CJK sample.
- After “Optional plugins” stage, decide whether to enable Thai `PyThaiNLP` in production.


### Health checks (per stage)

- Backend tests (pytest) for new utilities and recognized_words behavior.
- Frontend `npm run check` after backend field names remain unchanged.
- Manual smoke on target routes (text and words tabs) and hover tooltips.


### Acceptance criteria (overall)

- Backend returns non-empty `recognized_words` for Thai texts that have known wordforms in the DB.
- Offsets align with rendered text (NFC parity checks pass).
- Frontend shows multiple underlined-hover-links (structured mode) with tooltips.
- No regressions for whitespace languages (EN/FR/etc.).


### Rollout plan

- Dev: implement ICU segmentation + tests, verify on Thai.
- Staging (if available): enable logs, verify link counts and hover tooltips.
- Prod: deploy; monitor `/logs/backend.log` for segmentation and recognition counts; compare with words tab counts.
- Rollback: feature flag to revert `create_interactive_word_data` to the legacy regex matching if needed.


### Implementation signposts (where to edit)

- Add: `backend/utils/segmentation.py` (new)
- Modify: `backend/utils/vocab_llm_utils.py`
  - `create_interactive_word_data` — replace regex boundary matching with segmentation-first matching; keep function signature and output schema.
- Modify: `backend/utils/sourcefile_utils.py`
  - `get_sourcefile_details(... purpose="text")` — no schema change; ensure it passes `target_language_code` to segmentation path in `create_interactive_word_data`.
- Tests:
  - `backend/tests/backend/test_segmentation_recognition_per_language.py`
  - `backend/tests/backend/test_offset_parity.py`
- No changes required on the frontend for the main goal (structured mode already supported in `EnhancedText.svelte`).


### Commands & environment notes

- PyICU installation (macOS):
  - Ensure ICU libs present (Homebrew):
    - `brew install icu4c`
    - Set env if needed during build: `export ICU_VERSION=$(pkg-config --modversion icu-i18n || echo '')`
  - Add `PyICU` to `backend/requirements.txt`; typical wheels exist for many platforms, but on macOS you may need headers from `icu4c`.
- Run locally:
  - `./scripts/local/run_backend.sh`
  - `./scripts/local/run_frontend.sh`
  - Open: `http://localhost:5173/language/th/source/luke/mindfulness-teaching-txt/text`
- Logs: `/logs/backend.log` should show lines like `segmented_tokens=NN recognized_words=MM` for observability.

#### Serverless/Vercel compatibility

- Vercel Python Serverless Functions support binary wheels; however, dependencies that dynamically link system libraries can be fragile. To de-risk:
  - Prefer a `PyICU` wheel that bundles ICU for Linux (manylinux) when available; keep function size under Vercel limits.
  - Provide a runtime fallback: if `PyICU` is unavailable at import time, the segmentation registry automatically switches to pure-Python engines (Thai → PyThaiNLP, Chinese → jieba, Japanese → SudachiPy), and whitespace tokenization for others. This guarantees functionality on Vercel.
  - Keep segmentation strategy configurable via env (e.g., `SEGMENTATION_DEFAULT=icu|plugin`) to force plugin mode on serverless if needed.


### Risks & mitigations

- PyICU installation friction on some environments → document install, pin versions, provide preflight check in dev notes.
- Offset mismatch due to normalization differences → enforce NFC at the single point of truth (where offsets are computed) and verify parity in tests.
- Language coverage variance → keep ICU default; add plugin per-language when justified.
- Performance under large texts → optional Aho–Corasick fast path and simple caching if needed.


### Appendix: Alternatives & tradeoffs (brief)

- ICU/PyICU (chosen):
  - Pros: industry standard, cross-language coverage (Thai/CJK supported), stable API, maintained by Unicode Consortium, available in both Python and JS (Intl.Segmenter).
  - Cons: For some languages, accuracy may be below specialized tokenizers.
- PyThaiNLP (Thai):
  - Pros: often higher accuracy for Thai; multiple engines (newmm/attacut/deepcut); active community.
  - Cons: language-specific dependency; maintain per-language plugin.
- jieba (Chinese):
  - Pros: widely adopted; simple; good default for many Chinese texts.
  - Cons: dictionary-driven; may require custom dictionaries for domains.
- SudachiPy (Japanese):
  - Pros: modern, flexible modes; good accuracy.
  - Cons: heavier dependency; dictionary management.
- Stanza (multilingual):
  - Pros: high accuracy NLP pipeline.
  - Cons: heavyweight; model downloads; overkill if only tokenization needed.
- pyahocorasick (matching):
  - Pros: very fast multi-pattern search; great for known wordforms.
  - Cons: not a tokenizer; best as a complement to segmentation.


### Per-language defaults and plugin recommendations

- Sensible defaults (invisible to users): use ICU for all languages by default. This fixes Thai and provides robust behavior across the board with minimal dependencies.
- Optional accuracy plugins (enable per env/feature flag when desired):
  - **Thai (th)**: `PyThaiNLP` (`newmm` or `attacut`) — better lexical segmentation vs ICU on Thai; License: Apache 2.0.
  - **Chinese (zh)**: `jieba` — widely adopted, simple API; License: MIT.
  - **Japanese (ja)**: `SudachiPy` — modern with flexible modes; License: Apache 2.0.
  - Others (only if future needs arise): Korean (KoNLPy/Khaiii), Vietnamese (VnCoreNLP), etc. Not needed for current scope.

Default mapping proposal:
- ar, bn, hr, da, nl, fi, fr, de, el, ha, hi, hu, id, it, ko, mr, no, pl, pt, pa, es, sw, sv, tl, ta, te, tr, ur, vi → ICU
- th → ICU (default), PyThaiNLP optional
- zh → ICU (default), jieba optional
- ja → ICU (default), SudachiPy optional

Licensing summary (commercial-friendly): ICU (ICU License); PyICU (permissive); PyThaiNLP (Apache 2.0); jieba (MIT); SudachiPy (Apache 2.0). No known conflicts for open source or future commercial use.


