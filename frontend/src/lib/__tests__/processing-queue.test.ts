import { describe, it, expect, vi, beforeEach, afterAll } from 'vitest';
import { SourcefileProcessingQueue } from '../processing-queue';

// Minimal mocks for global fetch and getApiUrl dependency side-effects inside class
const originalFetch = global.fetch;

describe('SourcefileProcessingQueue', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    // assign to global fetch for test
    // @ts-ignore
    global.fetch = vi.fn(async () => ({ ok: true, json: async () => ({ status: {
      has_text: true,
      has_translation: true,
      wordforms_count: 1,
      phrases_count: 1,
      incomplete_lemmas: [],
      incomplete_lemmas_count: 0
    } }) })) as unknown as typeof fetch;
  });

  it('returns true immediately when no steps are required', async () => {
    const q = new SourcefileProcessingQueue(
      null,
      'es',
      'dir',
      'file',
      'text'
    );
    const result = await q.processAll(1);
    expect(result).toBe(true);
  });
});

// Restore
afterAll(() => {
  // @ts-ignore
  global.fetch = originalFetch;
});


