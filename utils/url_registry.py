def endpoint_for(view_func):
    """Get the endpoint string for url_for from a view function.
    
    This helps avoid hardcoding endpoint strings in url_for() calls,
    making them more resistant to function renames.
    
    Args:
        view_func: The view function to get the endpoint for
        
    Returns:
        str: The endpoint string in the format 'blueprint.function_name'
        
    Example:
        from views.sourcedir_views import sourcedirs_list
        url_for(endpoint_for(sourcedirs_list), target_language_code='el')
    """
    # Get the module name where the function is defined
    module_name = view_func.__module__
    
    # Extract the blueprint name from module name (assumes module = views.blueprint_name_views)
    parts = module_name.split('.')
    if len(parts) > 1:
        module_part = parts[-1]
        
        # Handle special cases for different view types
        if module_part.endswith('_views'):
            blueprint_name = module_part[:-6]  # Remove '_views' suffix
        elif module_part.endswith('_api'):
            blueprint_name = f"{module_part}"  # Keep '_api' suffix for API blueprints
        else:
            blueprint_name = module_part
    else:
        # Fallback if the module structure is different
        blueprint_name = module_name
    
    # Return in blueprint.function_name format
    return f"{blueprint_name}.{view_func.__name__}"

def generate_route_registry(app):
    """Generate route registry from Flask app.url_map.

    Creates a dictionary of route names mapped to URL templates.
    Routes are named in the format BLUEPRINT_VIEWFUNC and URL
    templates use {param} syntax for parameters.

    Args:
        app: The Flask application

    Returns:
        dict: A dictionary of route names and templates
    """
    routes = {}
    for rule in app.url_map.iter_rules():
        # Skip static and other special routes
        if rule.endpoint.startswith("static") or "." not in rule.endpoint:
            continue

        # Extract blueprint and function name
        blueprint, view_func = rule.endpoint.split(".")

        # Convert to BLUEPRINT_VIEWFUNC format
        route_name = f"{blueprint.upper()}_{view_func.upper()}"

        # Convert Flask route syntax to template syntax
        route_template = str(rule)
        # Replace Flask's <param> with {param}
        for arg in rule.arguments:
            # Handle converter syntax like <int:id>
            for converter in ["int", "float", "path", "uuid", "string"]:
                route_template = route_template.replace(
                    f"<{converter}:{arg}>", f"{{{arg}}}"
                )
            # Handle standard syntax <arg>
            route_template = route_template.replace(f"<{arg}>", f"{{{arg}}}")

        routes[route_name] = route_template

    return routes


def generate_typescript_routes(app, output_path="static/js/generated/routes.ts"):
    """Generate TypeScript route definitions from Flask app.url_map.

    Creates a TypeScript file with route constants, types, and a
    utility function for client-side route resolution.

    Args:
        app: The Flask application
        output_path: Path to write the TypeScript file

    Returns:
        str: The generated TypeScript code
    """
    import re
    import os

    with app.app_context():
        routes = generate_route_registry(app)

    # Create TypeScript type for route names
    route_names = list(routes.keys())
    route_name_type = (
        "export type RouteName = "
        + " | ".join([f'"{name}"' for name in route_names])
        + ";"
    )

    # Create parameter types based on route patterns
    param_types = {}
    for name, path in routes.items():
        # Extract parameter names from {param} patterns
        params = re.findall(r"\{([^}]+)\}", path)
        if params:
            param_types[name] = (
                "{ " + "; ".join([f"{param}: string" for param in params]) + " }"
            )
        else:
            param_types[name] = "{}"

    # Generate TypeScript interfaces for params
    param_interface = "export type RouteParams = {\n"
    for name, param_type in param_types.items():
        param_interface += f"  [RouteName.{name}]: {param_type};\n"
    param_interface += "};\n"

    # Generate route constants
    route_constants = "export const ROUTES = {\n"
    for name, path in routes.items():
        route_constants += f'  {name}: "{path}",\n'
    route_constants += "} as const;\n"

    # Generate enum for route names (better IDE autocomplete)
    route_enum = "export enum RouteName {\n"
    for name in routes.keys():
        route_enum += f'  {name} = "{name}",\n'
    route_enum += "}\n"

    # Combine all TypeScript code
    typescript_code = f"""// Auto-generated from Flask app.url_map
{route_enum}

{route_constants}

{param_interface}

/**
 * Resolve a route template with parameters.
 * 
 * @param routeName Name of the route from ROUTES
 * @param params Parameters to substitute in the route template
 * @returns Resolved URL with parameters
 */
export function resolveRoute<T extends RouteName>(
  routeName: T, 
  params: RouteParams[T]
): string {{
  let url = ROUTES[routeName];
  
  // Replace template parameters with actual values
  Object.entries(params).forEach(([key, value]) => {{
    url = url.replace(`{{${{key}}}}`, encodeURIComponent(String(value)));
  }});
  
  return url;
}}
"""

    # Write the TypeScript file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(typescript_code)

    return typescript_code
