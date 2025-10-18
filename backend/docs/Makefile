# Makefile for Sphinx documentation using uv-managed environment
#

# Project paths
PROJECT_ROOT := $(abspath ..)
VENVDIR      := $(PROJECT_ROOT)/.venv
UV           ?= uv

# Detect platform
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENVDIR)/Scripts/python.exe
	SET_PYTHONPATH := set PYTHONPATH=$(PROJECT_ROOT) &&
else
	PYTHON := $(VENVDIR)/bin/python
	SET_PYTHONPATH := PYTHONPATH=$(PROJECT_ROOT)
endif

# Sphinx configuration
SPHINXOPTS   ?=
SOURCEDIR    = source
BUILDDIR     = build

# Ensure PYTHONPATH includes the backend directory for autodoc
SPHINXBUILD  := PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m sphinx

# Put it first so that "make" without argument is like "make help".
help: docs-deps
	@$(SET_PYTHONPATH) $(PYTHON) -m sphinx -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

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
	$(SET_PYTHONPATH) $(PYTHON) -m sphinx -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)

# Preview documentation in default browser
preview: html
	@echo "Opening documentation in browser..."
ifeq ($(OS),Windows_NT)
	cmd /c start "" "$(abspath $(BUILDDIR)/html/index.html)"
else ifeq ($(shell uname),Darwin)
	open "$(BUILDDIR)/html/index.html"
else
	xdg-open "$(BUILDDIR)/html/index.html"
endif

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: docs-deps
	@$(SET_PYTHONPATH) $(PYTHON) -m sphinx -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
