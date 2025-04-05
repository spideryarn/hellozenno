from pathlib import Path
from typing import Union

from config import PROMPT_TEMPLATES_DIRN


def get_prompt_template_path(template_name: str) -> Path:
    """Get path to a Jinja template in the prompt templates directory.
    
    Args:
        template_name: Name of the template without .jinja extension
        
    Returns:
        Path object to the template file
    """
    template_path = PROMPT_TEMPLATES_DIRN / f"{template_name}.jinja"
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found at {template_path}")
    return template_path