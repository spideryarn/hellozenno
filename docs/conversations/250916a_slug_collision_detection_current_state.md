# Slug collision detection - 2025-09-16

---
Date: 2025-09-16
Duration: ~10 minutes
Type: Exploratory
Status: Active
Related Docs: docs/planning/250915a_backend_test_suite_consolidation.md
---

## Context & Goals

"Let's think about how to handle slug collision detection, ideally in a robust, clean, simple, general way that's reused at least somewhat across models. 

Investigate how this is handled currently. 

Be in @SOUNDING_BOARD_MODE.md"

## Main Discussion (verbatim)

I scanned the backend models, migrations, and views for slug usage and uniqueness. Here’s what we have today and what’s missing.

### What we do today (by model)

- Sourcedir
  - Slug is auto-generated on save if missing; no suffixing, only truncation.
  - Uniqueness is enforced per language via a DB unique index.
  - The create API pre-checks slug collisions and returns 409; still slices to 100 chars.
```843:850:backend/db_models.py
def save(self, *args, **kwargs):
    # Generate slug from path if not set
    if not self.slug:
        self.slug = slugify(str(self.path))
        # Truncate slug if it exceeds max length
        if len(self.slug) > SOURCEDIR_SLUG_MAX_LENGTH:
            self.slug = self.slug[:SOURCEDIR_SLUG_MAX_LENGTH]
    return super().save(*args, **kwargs)
```
```852:857:backend/db_models.py
class Meta:
    database = database
    indexes = (
        (("path", "target_language_code"), True),  # Unique index
        (("slug", "target_language_code"), True),  # Unique index for URLs
    )
```
```62:72:backend/views/sourcedir_api.py
# Check if a sourcedir with the same slug exists for this language
test_slug = slugify(str(path))[:100]
if (
    Sourcedir.select()
    .where(
        Sourcedir.slug == test_slug,
        Sourcedir.target_language_code == target_language_code,
    )
    .exists()
):
    return jsonify({"error": "Directory already exists"}), 409
```
```76:82:backend/views/sourcedir_api.py
sourcedir = Sourcedir.create(
    path=path,
    target_language_code=target_language_code,
    slug=test_slug,
    created_at=datetime.datetime.now(),
    updated_at=datetime.datetime.now(),
)
```

- Sourcefile
  - Slug is always regenerated from filename on save; no suffixing, only truncation (via slugify), and may collide for different filenames that slugify the same.
  - Uniqueness is enforced per sourcedir via a DB unique index.
```886:895:backend/db_models.py
def save(self, *args, **kwargs):
    # Always generate slug from current filename
    self.slug = slugify(str(self.filename))
    # Validate sourcefile_type
    if self.sourcefile_type not in VALID_SOURCEFILE_TYPES:
        raise ValueError(
            f"Invalid sourcefile_type: {self.sourcefile_type}. "
            f"Must be one of: {', '.join(sorted(VALID_SOURCEFILE_TYPES))}"
        )
    return super().save(*args, **kwargs)
```
```897:901:backend/db_models.py
class Meta:
    indexes = (
        (("sourcedir", "filename"), True),  # Composite unique index
        (("sourcedir", "slug"), True),  # Unique slug per sourcedir
    )
```

- Sentence
  - Slug is set if missing on save; no suffixing.
  - Uniqueness enforced per language via DB unique index.
```553:560:backend/db_models.py
def save(self, *args, **kwargs):
    # Generate slug from sentence if not set
    if not self.slug:
        self.slug = slugify(str(self.sentence))
        # Truncate slug if it exceeds max length
        if len(self.slug) > 255:
            self.slug = self.slug[:255]
    return super().save(*args, **kwargs)
```
```631:635:backend/db_models.py
class Meta:
    indexes = (
        (("sentence", "target_language_code"), True),  # Unique index
        (("slug", "target_language_code"), True),  # Unique index for URLs
    )
```

- Phrase
  - Slug is set if missing on save; no suffixing.
  - Uniqueness enforced per language via DB unique index.
```675:682:backend/db_models.py
def save(self, *args, **kwargs):
    # Generate slug from canonical_form if not set
    if not self.slug:
        self.slug = slugify(str(self.canonical_form))
        # Truncate slug if it exceeds max length
        if len(self.slug) > 255:
            self.slug = self.slug[:255]
    return super().save(*args, **kwargs)
```
```684:688:backend/db_models.py
class Meta:
    indexes = (
        (("canonical_form", "target_language_code"), True),  # Unique index
        (("slug", "target_language_code"), True),  # Unique index for URLs
    )
```

### Other observations and inconsistencies

- Slug lengths are inconsistent:
```102:105:backend/config.py
# Maximum length for slugs
SOURCEDIR_SLUG_MAX_LENGTH = 1024  # Characters allowed in URL slugs
SOURCEFILE_SLUG_MAX_LENGTH = 1024  # Characters allowed in URL slugs
```
  - But `Sourcedir` save truncates to config max, while the API pre-slices to 100. Models `Sentence`/`Phrase` hardcode 255 instead of using config.
- Several create flows check filename collisions (for `Sourcefile`) but not slug collisions; if two distinct filenames map to the same slug in a directory, DB raises IntegrityError and some endpoints return 500 rather than a clean 409.
- Planning doc explicitly calls out adding a reusable helper for slug collisions (not yet implemented).

### Current collision behavior (net effect)

- We mostly rely on database unique indexes to reject duplicates.
- Only `Sourcedir` create pre-checks slug collisions (by returning 409), without suffixing; all other models do not pre-check or suffix.
- No shared helper exists for “ensure unique slug with suffix.”

### Proposal sketch (general, simple, reusable)

- Introduce `utils/slug_utils.py` with:
  - `slugify_trim(value, max_length)` – use `slugify(value, max_length=max_length)` when available; fallback to slice.
  - `ensure_unique_slug(model_cls, base_value, *, scope_filters: dict, max_length: int, slug_field="slug")`
    - Steps:
      1. `base_slug = slugify_trim(base_value, max_length)`
      2. If no row exists where `slug == base_slug` and `scope_filters` match, return it.
      3. Query existing slugs in scope that start with `base_slug` or `base_slug-N` pattern, extract numeric suffixes, compute `next_n`.
      4. Build `candidate = f"{base_slug[:max_length - len(f'-{next_n}')]}-{next_n}"` and check again.
      5. Loop on conflict; also wrap the eventual insert/save in a try/catch for IntegrityError to handle races (retry with next number up to a small cap).
- Integration:
  - `Sourcedir.save`: when slug empty or path changed, call helper with scope `{"target_language_code": self.target_language_code}`.
  - `Sourcefile.save`: always derive base from `filename`, then call helper with scope `{"sourcedir": self.sourcedir}`.
  - `Sentence.save`: when slug empty or sentence changed, scope `{"target_language_code": self.target_language_code}`.
  - `Phrase.save`: same as `Sentence`.
- API consistency:
  - Prefer letting models handle slug generation/uniqueness; remove ad-hoc 100-char truncation. Keep early 409s for user-friendly errors where appropriate, but suffixing should happen inside the save to avoid 500s.
- Tests:
  - Parametrize across models to validate:
    - simple duplicate → gets “-2”
    - multiple duplicates → gets “-3”, etc.
    - truncation leaves room for suffix
    - scoped uniqueness (per language or per sourcedir)
    - rename flows preserve uniqueness and suffix when needed

### Questions to decide

- Should slugs change on rename? Today they do (e.g., `Sourcedir.rename` updates slug). If stability matters, we could decouple slug from display fields and only change on explicit request.
- Do we want a maximum attempts cap (e.g., 50) before giving up with 409?
- Standardize max lengths:
  - Use config for Sentence/Phrase too?
  - Keep 1024 for `Sourcedir`/`Sourcefile`, or align all to 255?

- Return codes:
  - Prefer suffixing automatically and return 201/200; only return 409 when we explicitly refuse to auto-suffix?

- Any models beyond the four to include later (e.g., the `Document` mentioned in docs)?

- Performance:
  - The “find max suffix” pattern uses prefix LIKE queries; OK given small scope sizes per language/dir. Fine to start simple.

I can draft the helper and wire it into the four models’ `save()` methods, then align the APIs to stop pre-slicing at 100 and rely on the helper. Let me know preferences on slug stability on rename and the standardized max lengths.

- Key takeaways:
  - Today: DB constraints catch slug collisions; only `Sourcedir` has a pre-check; no suffixing anywhere; some flows can 500 on slug collisions.
  - Add `ensure_unique_slug(...)` helper with scoped suffixing and integrate into model saves.
  - Align max-length handling via config and remove ad-hoc 100-char truncation in the API.

## Sources & References

- `backend/db_models.py`, `backend/views/sourcedir_api.py`, `backend/views/sourcefile_api.py`, `backend/views/sentence_api.py`
- Migrations touching slugs: `backend/migrations/008_add_sourcedir_slug.py`, `009_add_sourcefile_slug.py`, `015_0_add_sentence_slug.py`, `015_1_add_sentence_slug_constraints.py`, `024_add_phrase_slug.py`, `040_increase_source_field_lengths.py`
- Planning: `docs/planning/250915a_backend_test_suite_consolidation.md`, `docs/planning/finished/250107_Sourcedir_slugs.md`, `docs/planning/finished/250107_Sourcefile_slugs.md`
