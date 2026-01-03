# Frontend Console Logging Cleanup

**Priority**: High (Easy + High Value)
**Effort**: Medium (expanded scope from initial assessment)
**Risk**: Low

## Problem

60+ `console.log/warn/error` statements in production frontend code pollute the browser console.

**Priority files (high noise):**
- `frontend/src/lib/api.ts` - logs every request URL, response status, headers (SECURITY: may leak auth tokens)
- `frontend/src/lib/processing-queue.ts` - debug logs throughout
- `frontend/src/lib/components/EnhancedText.svelte` - extensive tooltip debug logging

**Secondary files (found via grep):**
- Route files with reactive logging (`$: console.log(...)`) - particularly impactful
- Other lib components (DataGrid, navigation, etc.)

## Approach

### Phase 1: Create logging utility
Create `frontend/src/lib/logger.ts`:
```typescript
export const logger = {
  debug: (...args: unknown[]) => { if (import.meta.env.DEV) console.log('[DEBUG]', ...args); },
  info: (...args: unknown[]) => { if (import.meta.env.DEV) console.info('[INFO]', ...args); },
  warn: (...args: unknown[]) => console.warn('[WARN]', ...args),
  error: (...args: unknown[]) => console.error('[ERROR]', ...args)
};
```

### Phase 2: Clean priority files
1. **api.ts**: Remove header logging entirely (security risk), gate request/response logging with `import.meta.env.DEV`
2. **processing-queue.ts**: Replace console.log with `logger.debug`
3. **EnhancedText.svelte**: Already has good DEV pattern at lines 159-172; clean remaining logs

### Phase 3: Clean reactive logging
Remove `$: console.log(...)` patterns from route files - these fire on every change.

### Log Type Categorization
- **console.log** → Remove or wrap in `import.meta.env.DEV` / use `logger.debug`
- **console.warn** → Case-by-case; keep if operationally relevant
- **console.error** → Keep (actual error handling)

## Success Criteria

- Zero console output in production builds for normal operations
- Debug logs available in development mode
- Error logs preserved (actual errors should still log)
- No auth tokens/sensitive data ever logged (even in DEV)

## Verification

After implementation:
```bash
cd frontend && npm run build
# Check no console.log in production output (console.error is allowed)
```

## Files to Modify

**Phase 1:**
- `frontend/src/lib/logger.ts` (new)

**Phase 2:**
- `frontend/src/lib/api.ts`
- `frontend/src/lib/processing-queue.ts`
- `frontend/src/lib/components/EnhancedText.svelte`

**Phase 3 (if time permits):**
- Route files with `$: console.log` patterns

## Notes

Triple-review scores: GPT-5.2 (88%), Gemini (90%), Opus (78%)
Refined based on reviewer feedback to expand scope and add logging utility.
