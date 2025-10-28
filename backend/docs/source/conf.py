import os
import sys
from typing import Any, Dict

from sphinx.application import Sphinx

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
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_favicon = '_static/image/favicon.ico'
html_logo = '_static/image/logo.svg'
html_theme_options = {
    'use_edit_page_button': True,
    'navbar_align': 'content',
    'logo': {'text': 'Documentation'},
    'navbar_center': ['navbar-nav'],
    'navbar_end': ['theme-switcher', 'navbar-icon-links'],
    'navbar_persistent': ['search-button'],
    'show_nav_level': 2,
    'navigation_depth': 4,
    'icon_links': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/your-org/your-repo',
            'icon': 'fab fa-github',
            'type': 'fontawesome',
        },
    ],
}

html_show_sourcelink = False

html_context = {
    'github_user': 'opensacorg',
    'github_repo': 'app-capanel-doc',
    'github_version': 'main',
    'doc_path': 'backend/docs/source',
}
html_sidebars = {'**': ['sidebar-nav-bs.html', 'page-toc.html']}


def setup_to_main(
    app: Sphinx, pagename: str, templatename: str, context, doctree
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
        links = link.split('/')
        idx = links.index('edit')
        return '/'.join(links[: idx + 1]) + '/main/' + '/'.join(links[idx + 2 :])

    context['to_main'] = to_main


def setup(app: Sphinx) -> Dict[str, Any]:
    """Add custom configuration to the Sphinx app.

    Args:
        app: the Sphinx application
    Returns:
        the 2 parallel parameters set to ``True``.
    """
    app.connect('html-page-context', setup_to_main)

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
