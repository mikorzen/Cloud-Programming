from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

__all__ = [
    "templates",
]

_CONFIG_FILE = Path(__file__).resolve().parents[1] / "config.toml"
_STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
_TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"

# Define paths to the configuration file and the template directory
# (.parents[i] is equivalent to calling .parent i+1 times)
_CONFIG_FILE = Path(__file__).resolve().parents[1] / "config.toml"
_STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
_TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"

# Bind the static directory to a StaticFiles object
# that will be used to serve static files on request
static_files = StaticFiles(directory=_STATIC_DIR)

# Bind the template directory to a Jinja2Templates object
# that will be used to serve templates on request
templates = Jinja2Templates(directory=_TEMPLATE_DIR)
