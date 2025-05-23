// Helper function to get language name from language code
// This is now a redirect to language-utils.ts which uses static data when possible
import { error } from '@sveltejs/kit';
import { get_language_name as getLanguageNameFromUtils } from './language-utils';

/**
 * @deprecated Use get_language_name from language-utils.ts which uses static data first
 */
export async function get_language_name(
    target_language_code: string,
    customFetch?: typeof fetch,
): Promise<string> {
    try {
        return await getLanguageNameFromUtils(target_language_code, customFetch);
    } catch (err) {
        // If it's already a SvelteKit error, just rethrow it
        if (err && typeof err === 'object' && 'status' in err) {
            throw err;
        }
        
        // Otherwise log and throw a new error
        console.error(
            `Error fetching language name for ${target_language_code}:`,
            err,
        );
        throw error(500, `Failed to fetch language data: ${target_language_code}`);
    }
}

/**
 * Truncates text to a maximum length, adding ellipsis if truncated
 * Use this for page titles and meta descriptions where content can be lengthy
 * 
 * @param text The text to truncate
 * @param maxLength Maximum length allowed (default: 50)
 * @returns Truncated text with ellipsis if needed
 */
export function truncate(text: string, maxLength: number = 50): string {
    if (!text) return '';
    
    // If text is shorter than maxLength, return it as is
    if (text.length <= maxLength) return text;
    
    // Otherwise truncate and add ellipsis
    return text.substring(0, maxLength - 1).trim() + '…';
}

/**
 * Generates a meta description tag for SEO optimization
 * This is especially useful for longer content (sentences, lemmas) where titles are truncated
 * 
 * @param content Main content for the description (will be truncated if too long)
 * @param context Optional contextual information to add after content
 * @param maxLength Maximum length for the entire description (default: 160 chars for SEO)
 * @returns Formatted meta description optimized for SEO
 */
export function generateMetaDescription(
    content: string, 
    context?: string,
    maxLength: number = 160
): string {
    if (!content) return '';
    
    // If no context, just truncate the content
    if (!context) {
        return truncate(content, maxLength);
    }
    
    // Calculate available space for content based on context length
    // Leave 5 chars for separator and buffer
    const separator = ' - ';
    const availableSpace = maxLength - context.length - separator.length;
    
    // If not enough space for meaningful content, prioritize it
    if (availableSpace < 30) {
        return truncate(content, maxLength);
    }
    
    // Otherwise combine truncated content with context
    const truncatedContent = truncate(content, availableSpace);
    return `${truncatedContent}${separator}${context}`;
}
