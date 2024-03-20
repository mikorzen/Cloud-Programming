# ruff:noqa:ERA001

from pathlib import Path

from fastapi.templating import Jinja2Templates

__all__ = [
    "templates",
]

# Define paths to the configuration file and the template directory
# (.parents[i] is equivalent to calling .parent i+1 times)
_CONFIG_FILE = Path(__file__).resolve().parents[1] / "config.toml"
_TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"

# Bind the template directory to a Jinja2Templates object
# that will be used to serve templates on request
templates = Jinja2Templates(_TEMPLATE_DIR)
