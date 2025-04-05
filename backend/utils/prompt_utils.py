from pathlib import Path
import os
from typing import Union


# Get absolute path to prompt_templates directory regardless of working directory
PROMPT_TEMPLATES_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "prompt_templates"


def get_prompt_template_path(template_name: str) -> Path:
    """Get path to a Jinja template in the prompt templates directory.
    
    Args:
        template_name: Name of the template without .jinja extension
        
    Returns:
        Path object to the template file
    """
    template_path = PROMPT_TEMPLATES_DIR / f"{template_name}.jinja"
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found at {template_path}")
    return template_path