# Goal, context

Enable users to upload a PDF and automatically create multiple `Sourcefile`s (one per page) by converting each page to an image in the browser, then reusing the existing image upload/OCR pipeline. Keep scope minimal; production is on Vercel Serverless with a ~4.5 MB request body limit.


## References

- `frontend/src/routes/language/[target_language_code]/source/[sourcedir_slug]/+page.svelte` – existing image/audio/text upload UI and `uploadFiles()` implementation.
- `backend/views/sourcedir_api.py#upload_sourcedir_new_sourcefile_api` – endpoint used by the frontend to upload files sequentially.
- `backend/utils/sourcefile_utils.py#process_uploaded_file` – image resizing and text/audio branching (images feed into OCR later).
- `backend/config.py` – allowed extensions and size limits; currently PDF is commented out.
- `gjdutils/docs/instructions/WRITE_PLANNING_DOC.md` – structure for planning docs.


## Principles, key decisions

- Keep it simple: one `Sourcefile` per PDF page; no page range UI for v1.
- Treat PDFs as images to reuse the existing pipeline; no backend PDF parsing.
- Do processing client-side to avoid server dependencies incompatible with Vercel.
- Respect Vercel request limits by controlling output page image size/quality; upload pages sequentially or in small batches.
- Mobile-friendly: solution should work on iOS Safari and Android Chrome.
- Fail fast: if anything unexpected happens during conversion or upload, show a clear, user-visible error with actionable info and stop immediately (no silent fallbacks).


## Stages & actions

### Stage: Browser-side PDF → images (v1 minimal)
- [ ] Add "Upload PDF" action and hidden file input (`accept=".pdf"`) next to existing upload inputs in `+page.svelte`.
  - When clicked, trigger a new `pdfInput` element. This mirrors the existing pattern for images/audio/text.
- [ ] Add lightweight PDF rendering in the browser using `pdfjs-dist` (no native deps).
  - Load PDF from `File.arrayBuffer()`; iterate pages sequentially.
  - Render each page to a canvas at target width (e.g. 1600–2000 px) with scaling based on page size and DPI.
  - Export to JPEG (`canvas.toBlob('image/jpeg', 0.8–0.85)`), downscaling/re-encoding if blob > ~3.5 MB to stay below Vercel limits with headroom.
  - Generate page filenames like `basename_p01.jpg`, `basename_p02.jpg`, … (zero-padded).
- [ ] Reuse existing `uploadFiles()` by constructing a `File[]` from generated blobs; progress bar shows conversion and then upload progress.
- [ ] UX: show a small modal/progress for "Converting PDF… page X / N"; allow cancel.
- [ ] Testing: manual test on desktop Chrome/Firefox/Safari and iOS Safari with a 5–10 page PDF; confirm pages appear as image `Sourcefile`s and OCR runs as usual.
  - [ ] Error UX: on any thrown error, display alert/modal with the message and abort further work; ensure the input resets so the same file can be retried.


### Stage: Robustness & safeguards
- [ ] Size control: adaptive downscale loop if blob exceeds 3.5 MB (reduce quality, then dimensions until under threshold or minimum limits reached).
- [ ] Memory control: process pages one-by-one, releasing canvas and blob references between pages to reduce peak memory.
- [ ] Error handling: catch PDF parsing/rendering errors; show actionable message; skip unreadable pages rather than failing the whole PDF.
- [ ] Filename/slug safety: sanitize `basename` (no spaces/long length) before composing page filenames.


### Stage: Optional batching (nice-to-have)
- [ ] Add an option to upload pages N-at-a-time (e.g. N=2 or 3) to shorten wall-clock time while keeping request sizes small and within serverless concurrency.
  - Implement as a small concurrency limiter around calls to the existing per-file POST flow.
  - Keep default sequential; expose concurrency as a constant for easy tuning.


### Stage: Documentation and follow-ups
- [ ] Update `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md` (brief mention of PDF client-side conversion and limits).
- [ ] Update any relevant user-facing help text/tooltips for the PDF option.
- [ ] Consider v2 ideas (not in v1 scope): backend PDF handling, embedded-text extraction fallback, sending PDF directly to LLM provider.

### Optional later-stage improvements (architecture/implementation)
- [ ] Extract PDF conversion utilities into `$lib/pdf/convert.ts` to keep the Svelte page lean and aid unit testing.
- [ ] Centralize upload concurrency and progress tracking in a small queue utility (reuseable by URL and YouTube flows).
- [ ] Add an image-size advisor that records actual per-page JPEG sizes in metadata for diagnostics.
- [ ] Offer a "keep original PDF" toggle that stores the PDF as a non-processed attachment (served via existing static endpoint) for provenance.


## Notes & constraints

- Vercel Serverless HTTP body limit ≈ 4.5 MB: aim for per-page JPEG under ~3.5 MB; upload is per-file POST so each request stays small.
- Dependency choice: `pdfjs-dist` only; avoid libraries that require native binaries (e.g., Poppler, PyMuPDF) in production.
- Mobile Safari: canvas rendering is supported; large canvases can crash — keep target width reasonable and process sequentially.
- Typical PDFs expected < 10 pages; no hard page limit in v1.


## Acceptance criteria

- Selecting a PDF produces one `Sourcefile` per page with image thumbnails/filenames visible in the Source Files list.
- OCR/translation/vocab pipeline runs identically to uploaded photos.
- Works on desktop and iPhone Safari for a 5–10 page PDF without crashes; each upload request body < 4.5 MB.
- No backend changes required; existing endpoints handle the images as-is.


