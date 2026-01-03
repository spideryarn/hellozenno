/**
 * Environment-aware logging utility.
 * 
 * - debug/info: Only log in development mode (tree-shaken from production builds)
 * - warn/error: Always log (important for production diagnostics)
 * 
 * Usage:
 *   import { logger } from '$lib/logger';
 *   logger.debug('Some debug info', { data });
 *   logger.error('Something failed', error);
 */

export const logger = {
  debug: (...args: unknown[]): void => {
    if (import.meta.env.DEV) console.log('[DEBUG]', ...args);
  },
  info: (...args: unknown[]): void => {
    if (import.meta.env.DEV) console.info('[INFO]', ...args);
  },
  warn: (...args: unknown[]): void => {
    console.warn('[WARN]', ...args);
  },
  error: (...args: unknown[]): void => {
    console.error('[ERROR]', ...args);
  }
};
