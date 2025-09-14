# Browser-side Concurrency and Queue Library Evaluation - 2025-09-14

---
Date: 2025-09-14
Duration: ~10 minutes
Type: Research Review
Status: Resolved
Related Docs: `frontend/src/lib/processing-queue.ts`
---

## Context & Goals

User wanted to understand the existing concurrency/queuing capabilities in the HelloZenno frontend codebase and evaluate whether the current solution supports concurrent processing or if a better library should be adopted.

## Key Background

The codebase already uses `queue-typescript` in the processing queue implementation at `frontend/src/lib/processing-queue.ts`. The user specifically asked: "Do we have any functionality/libraries that handle browser-side concurrency/queuing already implemented?"

## Main Discussion

### Current Implementation Discovery

Found that the project uses `queue-typescript` library in `frontend/src/lib/processing-queue.ts` for managing sourcefile processing steps. The implementation:

- Uses `Queue` from `queue-typescript` package (version 1.0.1)
- Processes API calls sequentially (one at a time)
- Handles processing steps including:
  - Text extraction
  - Translation
  - Wordforms extraction
  - Phrases extraction
  - Lemma metadata completion
- Tracks progress through a Svelte store (`processingState`)
- Includes authentication handling with Supabase JWT tokens

### queue-typescript Limitations

Research revealed that `queue-typescript`:
- **Does NOT support concurrency** - it's a simple FIFO queue processing items sequentially
- Last updated 7 years ago (published version 1.0.1)
- Only provides basic queue operations with TypeScript generics support
- Based on linked-list data structure
- Has minimal community adoption (22 projects using it)

### Alternative Library Research

User requested: "Search the web for a library that has an active, long-lasting community with lots of documentation, and is well-designed and robust."

Evaluated several options:
1. **p-queue** - Emerged as the recommended choice
2. **BullMQ** - Redis-backed, better for distributed systems
3. **better-queue** - Supports concurrent workers
4. **concurrent-promise-queue** - Rate limiting focus
5. **concurrent-queue** - Simple concurrency limits

## Decisions Made

### Recommended: p-queue

**p-queue** was identified as the best replacement for `queue-typescript` based on:

**Community & Maintenance:**
- Created by sindresorhus (prolific open-source contributor)
- 9.7M weekly downloads on npm
- Regular updates and active maintenance
- Feature-complete and stable

**Technical Capabilities:**
- Configurable concurrency limits (e.g., process 2+ items simultaneously)
- Priority queuing for task prioritization
- Rate limiting with interval caps (e.g., max 5 requests per second)
- Pause/resume functionality
- AbortController support for cancellation
- Native TypeScript support (no @types package needed)
- Native ESM package

**Migration Path:**
- Simple API that would allow easy migration from queue-typescript
- Clear upgrade path for the existing `SourcefileProcessingQueue` class

### Example Implementation
```typescript
import PQueue from 'p-queue';

const queue = new PQueue({
  concurrency: 2,  // Process 2 items simultaneously
  interval: 1000,  // Rate limiting
  intervalCap: 5   // Max 5 per interval
});

await queue.add(async () => fetchData());
```

## Open Questions

1. What's the optimal concurrency level for the sourcefile processing API calls?
2. Should different processing steps have different concurrency limits?
3. Are there API rate limits that need to be respected?

## Next Steps

If implementing p-queue:
1. Install p-queue package: `npm install p-queue`
2. Refactor `SourcefileProcessingQueue` class to use PQueue
3. Configure appropriate concurrency limits based on API capabilities
4. Test performance improvements with concurrent processing

## Sources & References

**npm Packages Evaluated:**
- **queue-typescript** ([npm](https://www.npmjs.com/package/queue-typescript)) - Current implementation, no concurrency support
- **p-queue** ([npm](https://www.npmjs.com/package/p-queue), [GitHub](https://github.com/sindresorhus/p-queue)) - Recommended replacement
- **BullMQ** ([Website](https://bullmq.io/)) - Redis-backed alternative for distributed systems

**Key Finding:** p-queue would allow processing multiple API calls concurrently while respecting rate limits, potentially providing significant performance improvements for the sourcefile processing pipeline.