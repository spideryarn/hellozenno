/**
 * HTML sanitization utilities for XSS prevention.
 * Uses sanitize-html with a strict allowlist configuration.
 */
import sanitize from 'sanitize-html';

const STRICT_CONFIG: sanitize.IOptions = {
	allowedTags: ['span', 'em', 'strong', 'a', 'br', 'p', 'mark', 'i', 'b'],
	allowedAttributes: {
		'*': ['class'],
		a: ['href', 'target', 'rel'],
		span: ['data-word', 'data-lemma']
	},
	allowedSchemes: ['http', 'https', 'mailto'],
	transformTags: {
		a: (tagName, attribs) => {
			return {
				tagName,
				attribs: {
					...attribs,
					rel: 'noopener noreferrer'
				}
			};
		}
	}
};

/**
 * Sanitize HTML string to prevent XSS attacks.
 * Uses a strict allowlist of tags and attributes.
 */
export function sanitizeHtml(dirty: string | null | undefined): string {
	if (!dirty) return '';
	return sanitize(dirty, STRICT_CONFIG);
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
