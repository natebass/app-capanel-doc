import os
import sys

os.environ.setdefault('POSTGRES_SERVER', 'localhost')
os.environ.setdefault('POSTGRES_USER', 'postgres')
os.environ.setdefault('POSTGRES_PASSWORD', 'postgres')
os.environ.setdefault('POSTGRES_DB', 'app')
os.environ.setdefault('FIRST_SUPERUSER', 'admin@example.com')
os.environ.setdefault('FIRST_SUPERUSER_PASSWORD', 'changeme')
sys.path.insert(0, os.path.abspath('../..'))
project = 'California Accountability Panel'
copyright = '2025, Open Sacramento'
author = 'Open Sacramento'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]
templates_path = ['_templates']
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_favicon = '_static/image/favicon.ico'
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'use_edit_page_button': True,
    'navbar_align': 'right',
}
html_context = {
    'github_user': 'opensacorg',
    'github_repo': 'app-capanel-doc',
    'github_version': 'main',
    'doc_path': 'backend/docs/source',
}


def setup_to_main(
    app: Sphinx, pagename: str, templatename: str, context, doctree
) -> None:
    """
    Add a function that jinja can access for returning an "edit this page" link
    pointing to `main`.
    """

    def to_main(link: str) -> str:
        """
        Transform "Edit on GitHub" links and make sure they always point to the
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


def setup(app: Sphinx) -> Dict[str, Any]:
    """Add custom configuration to the Sphinx app.

    Args:
        app: the Sphinx application
    Returns:
        the 2 parallel parameters set to ``True``.
    """
    app.connect("html-page-context", setup_to_main)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
