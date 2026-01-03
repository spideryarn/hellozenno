/**
 * HTML sanitization utilities for XSS prevention.
 * Uses DOMPurify with a strict allowlist configuration.
 */
import DOMPurify from 'isomorphic-dompurify';

const STRICT_CONFIG = {
	ALLOWED_TAGS: ['span', 'em', 'strong', 'a', 'br', 'p', 'mark', 'i', 'b'],
	ALLOWED_ATTR: ['class', 'href', 'target', 'rel', 'data-word', 'data-lemma'],
	ALLOW_DATA_ATTR: true,
	FORBID_TAGS: ['script', 'style', 'svg', 'math', 'iframe', 'object', 'embed', 'img'],
	FORBID_ATTR: ['onerror', 'onclick', 'onload', 'onmouseover', 'onmouseout', 'onfocus', 'onblur']
};

let hooksInstalled = false;

function installHooks() {
	if (hooksInstalled) return;

	DOMPurify.addHook('afterSanitizeAttributes', (node) => {
		if (node.tagName === 'A') {
			// Ensure safe link attributes
			node.setAttribute('rel', 'noopener noreferrer');

			// Block dangerous URL schemes
			const href = node.getAttribute('href') || '';
			const normalizedHref = href.trim().toLowerCase();
			if (
				normalizedHref.startsWith('javascript:') ||
				normalizedHref.startsWith('data:') ||
				normalizedHref.startsWith('vbscript:')
			) {
				node.removeAttribute('href');
			}
		}
	});

	hooksInstalled = true;
}

/**
 * Sanitize HTML string to prevent XSS attacks.
 * Uses a strict allowlist of tags and attributes.
 */
export function sanitizeHtml(dirty: string | null | undefined): string {
	if (!dirty) return '';
	installHooks();
	const result = DOMPurify.sanitize(dirty, STRICT_CONFIG);
	return typeof result === 'string' ? result : String(result);
}

/**
 * Escape HTML entities for safe text interpolation.
 * Use this for plain text that should never contain HTML.
 */
export function escapeHtml(text: string): string {
	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#039;');
}
