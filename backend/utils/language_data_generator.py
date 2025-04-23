"""
Generate TypeScript language data from Python configuration.

This module provides functions to generate TypeScript files containing
language data for use in the frontend, eliminating the need for API calls
to fetch basic language information.
"""

import os


def generate_typescript_language_data(app):
    """Generate TypeScript language data from application config.
    
    Creates a TypeScript file with language constants from the backend configuration.
    
    Args:
        app: The Flask application
    
    Returns:
        str: Path to the generated TypeScript file
    """
    from utils.lang_utils import get_all_languages
    
    # Use absolute path to ensure the file is always generated in the same location
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    output_path = os.path.join(project_root, "frontend/src/lib/generated/languages.ts")
    
    with app.app_context():
        # Get all languages
        languages = get_all_languages()
    
    # Generate TypeScript interfaces and constants
    typescript_code = """// Auto-generated from Flask language configuration
/**
 * Interface for a language definition
 */
export interface Language {
  /** Two-letter language code (ISO 639-1) */
  code: string;
  /** Human-readable language name */
  name: string;
}

/**
 * All supported languages in the application.
 * This is auto-generated from backend configuration.
 */
export const LANGUAGES: Language[] = [
"""
    
    # Add each language as a TypeScript object
    for lang in languages:
        typescript_code += f"  {{ code: \"{lang['code']}\", name: \"{lang['name']}\" }},\n"
    
    typescript_code += """];

/**
 * Map of language codes to language names for quick lookups.
 */
export const LANGUAGE_NAMES: Record<string, string> = {
"""
    
    # Add language name map
    for lang in languages:
        typescript_code += f"  \"{lang['code']}\": \"{lang['name']}\",\n"
    
    typescript_code += """};

/**
 * Get a language name from a language code.
 * 
 * @param target_language_code Two-letter language code
 * @returns The language name, or the code if not found
 */
export function getLanguageName(target_language_code: string): string {
  return LANGUAGE_NAMES[target_language_code] || target_language_code;
}

/**
 * Find a language by its code.
 * 
 * @param target_language_code Two-letter language code
 * @returns The language object, or undefined if not found
 */
export function findLanguageByCode(target_language_code: string): Language | undefined {
  return LANGUAGES.find(lang => lang.code === target_language_code);
}
"""
    
    # Write the TypeScript file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(typescript_code)
    
    return output_path