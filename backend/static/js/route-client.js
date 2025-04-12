/**
 * Client-side utility for resolving routes using the route registry.
 * 
 * This script provides functions to work with the server-generated route registry
 * that is injected into the global window.ROUTES object.
 */

(function () {
    /**
     * Resolve a route template with parameters.
     * 
     * @param {string} routeName - Name of the route from ROUTES
     * @param {Object} params - Parameters to substitute in the route template
     * @returns {string} Resolved URL with parameters
     * @example
     *   // Returns "/api/lang/sourcedir/el"
     *   resolveRoute('SOURCEDIR_API_LIST_SOURCEDIRS', {target_language_code: 'el'})
     */
    function resolveRoute(routeName, params = {}) {
        if (!window.ROUTES || !window.ROUTES[routeName]) {
            console.error(`Route not found: ${routeName}`);
            return '';
        }

        let url = window.ROUTES[routeName];

        // Replace template parameters with actual values
        Object.entries(params).forEach(([key, value]) => {
            url = url.replace(`{${key}}`, encodeURIComponent(value));
        });

        return url;
    }

    // Export functions to global scope
    window.resolveRoute = resolveRoute;
})();