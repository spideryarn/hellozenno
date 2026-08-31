import { describe, it, expect } from 'vitest';
import { resolveApiPath } from './api';
import { API_BASE_URL } from './config';

/**
 * These pin down a bug that is invisible in development: the vite dev server
 * proxies /api to the Flask backend, so root-relative media paths returned by
 * the API resolve correctly locally. In production the frontend and the API are
 * separate deployments and www has no /api route, so the same path 404s.
 */
describe('resolveApiPath', () => {
	it('makes a root-relative API path absolute against the API base', () => {
		expect(resolveApiPath('/api/lang/lemma/el/x/audio?variant_id=7')).toBe(
			`${API_BASE_URL}/api/lang/lemma/el/x/audio?variant_id=7`,
		);
	});

	it('leaves an absolute http(s) URL untouched', () => {
		const url = 'https://api.hellozenno.com/api/lang/sentence/el/42/audio';
		expect(resolveApiPath(url)).toBe(url);
	});

	it('does not double up the slash when the path lacks one', () => {
		expect(resolveApiPath('api/lang/x')).toBe(`${API_BASE_URL}/api/lang/x`);
	});

	it('leaves a data: URL untouched', () => {
		expect(resolveApiPath('data:audio/mpeg;base64,AAAA')).toBe('data:audio/mpeg;base64,AAAA');
	});

	it('never returns a page-origin-relative path', () => {
		// The whole point: the result must not start with "/", or the browser
		// resolves it against www.hellozenno.com instead of api.hellozenno.com.
		expect(resolveApiPath('/api/lang/lemma/el/x/audio').startsWith('/')).toBe(false);
	});
});
