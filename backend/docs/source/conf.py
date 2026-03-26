import os
import sys
from typing import Any

from sphinx.application import Sphinx

os.environ.setdefault("PROJECT_NAME", "California Accountability Panel")
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "app")
os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "changeme")
os.environ.setdefault("SECRET_KEY", "dummy-secret-key-for-docs")
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("."))
project = "California Accountability Panel"
copyright = "2026, Open Sacramento"
author = "Open Sacramento"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_design",
    "_extension.gallery_directive",
    "_extension.component_directive",
    "sphinxcontrib.mermaid",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_favicon = "_static/image/favicon.ico"
html_logo = "_static/image/logo.svg"
html_show_sourcelink = False
html_theme_options = {
    "use_edit_page_button": True,
    "navbar_align": "content",
    "logo": {"text": "Accountability Panel Docs"},
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "show_nav_level": 1,
    "navigation_depth": 4,
    "icon_links": [
        {
            "name": "Website",
            "url": "https://capanel-full-5418848943.us-west1.run.app",
            "icon": "fas fa-globe",
            "type": "fontawesome",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/opensacorg/app-capanel-web",
            "icon": "fab fa-github",
            "type": "fontawesome",
        },
    ],
}
html_context = {
    "github_user": "opensacorg",
    "github_repo": "app-capanel-doc",
    "github_version": "main",
    "doc_path": "install/docs/source",
}
html_sidebars = {
    "developer-guide/index": ["sidebar-nav-bs.html", "page-toc.html"],
    "feature/index": ["sidebar-nav-bs.html", "page-toc.html"],
    "user-guide/index": ["sidebar-nav-bs.html", "page-toc.html"],
}


def setup_to_main(
    _app: Sphinx,
    _pagename: str,
    _templatename: str,
    context: dict[str, Any],
    _doctree: Any,
) -> None:
    """
    Add a function that jinja can access for returning an 'edit this page' link
    pointing to `main`.
    """

    def to_main(link: str) -> str:
        """
        Transform 'Edit on GitHub' links and make sure they always point to the
        main branch.

        Args:
            link: the link to the GitHub edit interface

        Returns:
            the link to the tip of the main branch for the same file
        """
        links = link.split("/")
        idx = links.index("edit")
        return "/".join(links[: idx + 1]) + "/main/" + "/".join(links[idx + 2 :])

    context["to_main"] = to_main


def setup(sphinxApp: Sphinx) -> dict[str, Any]:
    """Add custom configuration to the Sphinx app.

    Args:
        app: the Sphinx application
    Returns:
        the 2 parallel parameters set to ``True``.
    """
    sphinxApp.connect("html-page-context", setup_to_main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


try:
    import app.api.routes.items

    print(f"Successfully imported items: {dir(app.api.routes.items)}")
except Exception as e:
    print(f"Failed to import items: {e}")
