# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# Add the parent directory (backend) to the Python path for autodoc
import os
import sys

# Provide minimal environment variables so app imports don't fail during autodoc
os.environ.setdefault('POSTGRES_SERVER', 'localhost')
os.environ.setdefault('POSTGRES_USER', 'postgres')
os.environ.setdefault('POSTGRES_PASSWORD', 'postgres')
os.environ.setdefault('POSTGRES_DB', 'app')
os.environ.setdefault('FIRST_SUPERUSER', 'admin@example.com')
os.environ.setdefault('FIRST_SUPERUSER_PASSWORD', 'changeme')

# Insert the backend root so `import app.*` works. We need the parent of the
# `app` package on sys.path, not the package directory itself.
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'California Accountability Panel'
copyright = '2025, Open Sacramento'
author = 'Open Sacramento'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_favicon = '_static/image/favicon.ico'

html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    "use_edit_page_button": True,
}

html_context = {
    "github_user": "opensacorg",
    "github_repo": "app-capanel-doc",
    "github_version": "main",
    "doc_path": "backend/docs/source",
}
