import { describe, it, expect } from 'vitest';
import { sanitizeHtml, escapeHtml } from './sanitize';

describe('sanitizeHtml', () => {
	describe('XSS payload neutralization', () => {
		const XSS_PAYLOADS = [
			'<script>alert(1)</script>',
			'<script src="evil.js"></script>',
			'<img src=x onerror=alert(1)>',
			'<img src="x" onerror="alert(1)">',
			'<a href="javascript:alert(1)">click</a>',
			'<a href="JAVASCRIPT:alert(1)">click</a>',
			'<a href=" javascript:alert(1)">click</a>',
			'<a href="data:text/html,<script>alert(1)</script>">click</a>',
			'<a href="vbscript:alert(1)">click</a>',
			'<svg onload=alert(1)>',
			'<svg/onload=alert(1)>',
			'<div style="background:url(javascript:alert(1))">',
			'<div onclick="alert(1)">click me</div>',
			'<body onload="alert(1)">',
			'<input onfocus="alert(1)" autofocus>',
			'<marquee onstart="alert(1)">',
			'<iframe src="javascript:alert(1)">',
			'<object data="javascript:alert(1)">',
			'<embed src="javascript:alert(1)">',
			'"><script>alert(1)</script>',
			"'><script>alert(1)</script>",
			'<math><mtext><table><mglyph><style><img src=x onerror=alert(1)>'
		];

		it.each(XSS_PAYLOADS)('neutralizes XSS payload: %s', (payload) => {
			const result = sanitizeHtml(payload);
			expect(result).not.toContain('<script');
			expect(result).not.toContain('onerror');
			expect(result).not.toContain('onclick');
			expect(result).not.toContain('onload');
			expect(result).not.toContain('onfocus');
			expect(result).not.toMatch(/href=["']?\s*javascript:/i);
			expect(result).not.toContain('<svg');
			expect(result).not.toContain('<iframe');
			expect(result).not.toContain('<object');
			expect(result).not.toContain('<embed');
			expect(result).not.toContain('<img');
		});
	});

	describe('preserves legitimate content', () => {
		it('preserves allowed tags', () => {
			const html = '<span class="hz-foreign-text">слово</span>';
			expect(sanitizeHtml(html)).toBe(html);
		});

		it('preserves links with safe hrefs', () => {
			const html = '<a href="/language/uk/lemma/test" class="word-link">test</a>';
			const result = sanitizeHtml(html);
			expect(result).toContain('href="/language/uk/lemma/test"');
			expect(result).toContain('class="word-link"');
			expect(result).toContain('rel="noopener noreferrer"');
		});

		it('preserves br tags', () => {
			const html = 'line 1<br>line 2<br>line 3';
			expect(sanitizeHtml(html)).toBe('line 1<br>line 2<br>line 3');
		});

		it('preserves formatting tags', () => {
			const html = '<em>italic</em> <strong>bold</strong> <mark>highlighted</mark>';
			expect(sanitizeHtml(html)).toBe(html);
		});

		it('preserves data attributes', () => {
			const html = '<span data-word="test" data-lemma="test">test</span>';
			expect(sanitizeHtml(html)).toContain('data-word="test"');
			expect(sanitizeHtml(html)).toContain('data-lemma="test"');
		});

		it('preserves paragraph tags', () => {
			const html = '<p>Paragraph 1</p><p>Paragraph 2</p>';
			expect(sanitizeHtml(html)).toBe(html);
		});
	});

	describe('edge cases', () => {
		it('handles null input', () => {
			expect(sanitizeHtml(null)).toBe('');
		});

		it('handles undefined input', () => {
			expect(sanitizeHtml(undefined)).toBe('');
		});

		it('handles empty string', () => {
			expect(sanitizeHtml('')).toBe('');
		});

		it('handles plain text', () => {
			expect(sanitizeHtml('just plain text')).toBe('just plain text');
		});

		it('is stable on multiple calls', () => {
			const html = '<span class="test">content</span>';
			const result1 = sanitizeHtml(html);
			const result2 = sanitizeHtml(html);
			const result3 = sanitizeHtml(result1);
			expect(result1).toBe(result2);
			expect(result1).toBe(result3);
		});
	});
});

describe('escapeHtml', () => {
	it('escapes HTML entities', () => {
		expect(escapeHtml('<script>alert(1)</script>')).toBe(
			'&lt;script&gt;alert(1)&lt;/script&gt;'
		);
	});

	it('escapes quotes', () => {
		expect(escapeHtml('say "hello" & \'goodbye\'')).toBe(
			'say &quot;hello&quot; &amp; &#039;goodbye&#039;'
		);
	});

	it('handles plain text unchanged', () => {
		expect(escapeHtml('plain text')).toBe('plain text');
	});
});
