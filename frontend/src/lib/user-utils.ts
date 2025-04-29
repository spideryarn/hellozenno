/**
 * Utility functions for user-related operations and formatting
 */

/**
 * Formats a UUID to be shorter and more readable by taking just the first segment
 * Used for displaying user IDs in a consistent way across the application
 * 
 * @param id The UUID to format
 * @returns Formatted user ID (first segment of UUID)
 */
export function formatUserId(id: string | null | undefined): string {
  if (!id) return '';
  
  // If it looks like a UUID, format it to be shorter
  if (id.length > 8 && id.includes('-')) {
    // Return just the first part of the UUID
    return id.split('-')[0];
  }
  return id;
}