from pathlib import Path

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

__all__ = [
    "static_router",
    "template_config",
]

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"


static_router = create_static_files_router("/static", [STATIC_DIR])
template_config = TemplateConfig(
    engine=JinjaTemplateEngine,
    directory=TEMPLATE_DIR,
)
