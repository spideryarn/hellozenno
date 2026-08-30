# Claude Models

Which Claude model HelloZenno uses, and what to do when Anthropic retires it.

See also:
- `backend/docs/DEVOPS.md` - deployment, including the gjdutils/PyPI coupling
- `docs/reference/CONFIGURATION.md` - other configuration settings

## Current model

`config.CLAUDE_MODEL_NAME` (in `backend/config.py`) is the single place the model
is set. It is currently `claude-sonnet-5`.

Every LLM call goes through `utils.vocab_llm_utils.generate_gpt_from_template`,
a thin wrapper around gjdutils' function that injects `CLAUDE_MODEL_NAME`. To
change models, edit that one constant. To override for a single call, pass
`model=` explicitly.

Model IDs from the 4.6 generation onwards (`claude-sonnet-5`, `claude-opus-5`,
`claude-haiku-4-5`) are pinned snapshots - they never silently roll to a
different model - so it is safe to hardcode them.

## When a model gets retired

Anthropic retires old models. **A retired model returns HTTP 404 and every LLM
call in the app fails**, with no deploy and no code change to point at.

This has already bitten us once. We were on `claude-sonnet-4-0`, an alias for
`claude-sonnet-4-20250514`, which was deprecated 2026-04-14 and **retired
2026-06-15**. Every Claude-backed feature - wordform and lemma metadata,
translations, sentence generation, sourcefile processing, the `/learn` flow -
was broken in production for about ten weeks before anyone noticed.

Nothing in our setup caught it:
- `/sys/health-check` tests Flask, not Claude.
- Every backend test mocks `generate_gpt_from_template`, so the suite passed throughout.
- The deprecation email went to the account owner 60+ days ahead and was missed.

**To check what is currently callable**, list the live models (this is free):

```bash
source .env.local
curl -s https://api.anthropic.com/v1/models \
  -H "x-api-key: $CLAUDE_API_KEY" -H "anthropic-version: 2023-06-01" \
  | python -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data']]"
```

Anthropic's deprecation schedule: https://platform.claude.com/docs/en/about-claude/model-deprecations
(note `docs.anthropic.com` now redirects to `platform.claude.com`).

## Gotchas when changing model

Newer models are not always drop-in. When moving to a current model, check:

- **`temperature` / `top_p` / `top_k` are rejected** on Sonnet 5, Opus 5 and the
  4.7+ family - HTTP 400 from the API, or a `TypeError` from the SDK itself on
  anthropic 1.x, which removed the parameter. gjdutils therefore omits the
  keyword entirely unless it is explicitly set, rather than passing `NOT_GIVEN`.
- **`response.content[0]` is often a `thinking` block, not the answer.** Current
  models think adaptively by default, so code must select the first block whose
  `type` is `"text"` rather than indexing by position. Indexing `content[0].text`
  raises `AttributeError` - and only on the harder prompts that actually trigger
  thinking, so it can pass a smoke test and fail in production.
- **Thinking tokens count towards `max_tokens`**, and Sonnet 5's tokenizer
  produces roughly 30% more tokens for the same text. gjdutils' default
  `max_tokens` is 16384 to leave headroom.
- **`stop_reason: "refusal"` arrives as HTTP 200**, not an exception. gjdutils
  raises on it rather than reading a missing content block.

The handling for all four lives in `gjdutils/src/gjdutils/llms_claude.py`
(`call_claude_gpt`), not in this repo - see DEVOPS.md for how that reaches
production.

## Watch out for SDK version skew

`backend/requirements.txt` pins `anthropic>=1.2.0,<2`. Keep it pinned. It used to
be bare, which meant local machines ran whatever was installed months ago while
production installed the newest release at build time.

That skew hid a real bug through a whole deploy: anthropic 1.x **removed**
`temperature` from `Messages.create()`, so passing the keyword at all - even as
`NOT_GIVEN` - raises `TypeError` before any request is made. On a local env
still running anthropic 0.49 the code tested clean; production, on 1.2.0, 500'd
on every wordform page.

If you are verifying a change to the LLM path, check the SDK version you are
testing against actually matches what production will install:

```bash
python -c "import anthropic, inspect; print(anthropic.__version__)"
```

## Verifying a model change

The test suite mocks the LLM layer, so it cannot catch a bad model. Exercise the
real prompt templates against the live API instead:

```bash
source .env.local
python -c "
import sys; sys.path.insert(0, 'backend')
from utils.vocab_llm_utils import generate_gpt_from_template, anthropic_client
from utils.prompt_utils import get_prompt_template_path
out, extra = generate_gpt_from_template(
    client=anthropic_client,
    prompt_template=get_prompt_template_path('metadata_for_lemma'),
    context_d={'target_language_name': 'Greek', 'lemma': 'τρέχω'},
    response_json=True)
print(extra['response']['model'], list(out.keys()))
"
```

Templates worth checking, since they cover both JSON and plain-text modes:
`metadata_for_lemma`, `quick_search_for_wordform`, `extract_tricky_wordforms`,
`extract_phrases_from_text`, `generate_sentence_flashcards` (JSON), and
`translate_to_english` (plain text).
