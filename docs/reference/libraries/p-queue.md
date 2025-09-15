
Last updated: 2025-09-15

### Overview
p-queue is a small, well-maintained promise queue that adds practical features for browser and Node runtimes:
- Concurrency limits (run N tasks at once)
- Per-task priority
- Optional rate limiting via interval + intervalCap
- Pause/resume and queue draining helpers
- Built-in TypeScript types and ESM-first packaging

It’s a good fit to orchestrate multiple async calls (e.g., API requests, I/O-bound tasks) without overwhelming the backend or the user’s browser.

References:
- npm: [p-queue](https://www.npmjs.com/package/p-queue)
- GitHub: [sindresorhus/p-queue](https://github.com/sindresorhus/p-queue)

### Use cases
- Limit simultaneous fetch calls from the browser (prevent network/CPU overload)
- Respect backend or third-party API limits by capping requests per time window
- Prioritize urgent tasks ahead of bulk/background tasks
- Graceful cancellation and pausing during navigation or user interaction

### Getting started
Install:
```bash
npm install p-queue
```

Basic usage:
```ts
import PQueue from 'p-queue';

const queue = new PQueue({ concurrency: 2 });

await queue.add(async () => {
  const res = await fetch('/api/do-something');
  return res.json();
});
```

Rate limiting and priority:
```ts
import PQueue from 'p-queue';

const queue = new PQueue({
  concurrency: 2,
  interval: 1000,    // length of the time window in ms
  intervalCap: 5     // max tasks per interval
});

// Higher priority number = higher priority
queue.add(() => fetch('/fast-lane'), { priority: 10 });
queue.add(() => fetch('/background'), { priority: 0 });
```

Pause/resume and draining:
```ts
queue.pause();
// ... later
queue.resume();

// Wait until the queue becomes empty (no waiting tasks)
await queue.onEmpty();

// Wait until everything has completed (nothing pending or active)
await queue.onIdle();
```

Cancellation with AbortController:
```ts
import PQueue from 'p-queue';

const queue = new PQueue({ concurrency: 2 });
const ac = new AbortController();

const task = queue.add(async () =>
  fetch('/api/slow', { signal: ac.signal })
);

// If needed
ac.abort();
```

References:
- npm: [p-queue](https://www.npmjs.com/package/p-queue)
- GitHub: [README, API examples](https://github.com/sindresorhus/p-queue)

### Key concepts
- Concurrency: Maximum number of tasks that can run simultaneously.
- Priority: Higher numbers run first when capacity frees up.
- Rate limiting: interval + intervalCap limit throughput; works with concurrency.
- Draining helpers: onEmpty and onIdle return Promises for coordinated shutdowns.
- Metrics: `queue.size` (waiting tasks), `queue.pending` (actively running tasks).

### Best practices
- Start with conservative concurrency (2–3) and tune based on backend limits and UX.
- Use `interval`/`intervalCap` to respect external API quotas.
- Prefer per-task priorities over hand-rolled reordering logic.
- Wrap fetches with AbortController so navigation/unmount can cancel in-flight tasks.
- Await `onIdle()` before updating UI with “all done” states.

### Common gotchas
- ESM-only import: use `import PQueue from 'p-queue'` (not CommonJS require).
- Priority semantics: Larger `priority` numbers mean higher priority.
- Rate limiting affects starts per interval; it doesn’t pause tasks mid-flight.

### Migration from queue-typescript
Current usage in this repo:
```1:1:frontend/src/lib/processing-queue.ts
import { Queue } from 'queue-typescript';
```
`queue-typescript` provides a FIFO data structure but does not schedule async work nor support concurrency/rate limiting. p-queue replaces manual enqueue/dequeue loops with promise-returning tasks and built-in scheduling.

Step-by-step migration sketch:
1) Install and import p-queue; remove `queue-typescript` dependency.
```bash
npm install p-queue && npm uninstall queue-typescript
```
```ts
import PQueue from 'p-queue';
```
2) Replace manual queueing/dequeue loop with `queue.add(() => task())` calls. For example, instead of holding an array or linked list of steps and a `while (queue.length > 0) { ... await process(step) }`, push each step as a function into p-queue:
```ts
const queue = new PQueue({ concurrency: 2, interval: 1000, intervalCap: 5 });

steps.forEach((step) => {
  queue.add(() => processSingleStep(step));
});

await queue.onIdle(); // all done
```
3) Use priorities to control execution order (e.g., normal steps before long-tail metadata):
```ts
queue.add(() => processSingleStep(step), { priority: step.type === 'lemma_metadata' ? 0 : 10 });
```
4) Replace finalization logic with `await queue.onIdle()` and then fetch final state.
5) If needed, expose pause/resume and wire AbortController for cancellation.

Effort estimate for this codebase:
- Code touch points: 1 file (`frontend/src/lib/processing-queue.ts`) plus `frontend/package.json` deps.
- Scope: Small. Most logic (step building, UI updates) remains. Replace queue wiring and loop with p-queue adds.
- Time: ~1–2 hours including testing and tuning `concurrency`/rate limits.

References:
- `queue-typescript` on npm: [queue-typescript](https://www.npmjs.com/package/queue-typescript)
- p-queue docs: [npm](https://www.npmjs.com/package/p-queue), [GitHub](https://github.com/sindresorhus/p-queue)

### Alternatives
- Bottleneck — powerful rate limiter with grouping/cluster features: [npm](https://www.npmjs.com/package/bottleneck), [GitHub](https://github.com/SGrondin/bottleneck)
- p-limit — minimal concurrency limiter (no rate limiting, no priorities): [npm](https://www.npmjs.com/package/p-limit), [GitHub](https://github.com/sindresorhus/p-limit)

### Troubleshooting
- Build complains about default import: ensure your bundler targets ESM and TypeScript config supports ESM. In Vite/SvelteKit this is the default.
- Tasks not respecting rate limits: verify both `interval` and `intervalCap` are set; ensure you’re adding tasks to the same queue instance.
- UI claims “done” too early: use `await queue.onIdle()` rather than checking `queue.size`.

### Notes for HelloZenno
- Start with `concurrency: 2` and add `interval`/`intervalCap` if backend endpoints have limits.
- Use per-step priority to keep core steps ahead of lemma metadata batch.
- Consider exposing a cancel control tied to AbortController for long operations.


