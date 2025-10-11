# Makefile for Sphinx documentation using uv-managed environment
#

# Project paths
PROJECT_ROOT := $(abspath ..)
VENVDIR      := $(PROJECT_ROOT)/.venv
PYTHON       := $(VENVDIR)/bin/python
UV           ?= uv

# Sphinx configuration
SPHINXOPTS   ?=
SOURCEDIR    = source
BUILDDIR     = build

# Ensure PYTHONPATH includes the backend directory for autodoc
SPHINXBUILD  := PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m sphinx

# Put it first so that "make" without argument is like "make help".
help: docs-deps
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help docs-deps clean preview Makefile

# Ensure the uv virtual environment exists
$(VENVDIR):
	cd $(PROJECT_ROOT) && $(UV) venv .venv

# Install/sync dependencies using uv (includes Sphinx and extensions)
docs-deps: $(VENVDIR)
	cd $(PROJECT_ROOT) && $(UV) sync

# Clean build artifacts
clean:
	rm -rf $(BUILDDIR)/*

# HTML build target
html: docs-deps
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)

# Preview documentation in default browser
preview: html
	@echo "Opening documentation in browser..."
	xdg-open "$(BUILDDIR)/html/index.html"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: docs-deps
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
