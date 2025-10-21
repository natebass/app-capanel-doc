# Makefile for Sphinx documentation using uv-managed environment
#

# Project paths
PROJECT_ROOT := $(abspath ..)
VENV_DIR      := $(PROJECT_ROOT)/.venv
UV           ?= uv

# Detect platform
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV_DIR)/Scripts/python.exe
	SET_PYTHONPATH := set PYTHONPATH=$(PROJECT_ROOT) &&
else
	PYTHON := $(VENV_DIR)/bin/python
	SET_PYTHONPATH := PYTHONPATH=$(PROJECT_ROOT)
endif

# Sphinx configuration
SPHINX_OPTIONS   ?=
SOURCE_DIRECTORY    = source
BUILD_DIR     = build

# Ensure PYTHONPATH includes the backend directory for autodoc
SPHINX_BUILD  := PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m sphinx

# Put it first so that "make" without argument is like "make help".
help: docs-deps
	@$(SET_PYTHONPATH) $(PYTHON) -m sphinx -M help "$(SOURCE_DIRECTORY)" "$(BUILD_DIR)" $(SPHINX_OPTIONS) $(O)

.PHONY: help docs-deps clean preview Makefile

# Ensure the uv virtual environment exists
$(VENV_DIR):
	cd $(PROJECT_ROOT) && $(UV) venv .venv

# Install/sync dependencies using uv (includes Sphinx and extensions)
docs-deps: $(VENV_DIR)
	cd $(PROJECT_ROOT) && $(UV) sync

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)/*

# HTML build target
html: docs-deps
	$(SET_PYTHONPATH) $(PYTHON) -m sphinx -b html "$(SOURCE_DIRECTORY)" "$(BUILD_DIR)/html" $(SPHINX_OPTIONS)

# Preview documentation in default browser
preview: html
	@echo "Opening documentation in browser..."
ifeq ($(OS),Windows_NT)
	cmd /c start "" "$(abspath $(BUILD_DIR)/html/index.html)"
else ifeq ($(shell uname),Darwin)
	open "$(BUILD_DIR)/html/index.html"
else
	xdg-open "$(BUILD_DIR)/html/index.html"
endif

# Live reload backend
reload: docs-deps
	$(SET_PYTHONPATH) sphinx-autobuild "$(SOURCE_DIRECTORY)" "$(BUILD_DIR)/html" $(SPHINX_OPTIONS)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINX_OPTIONS).
%: docs-deps
	@$(SET_PYTHONPATH) $(PYTHON) -m sphinx -M $@ "$(SOURCE_DIRECTORY)" "$(BUILD_DIR)" $(SPHINX_OPTIONS) $(O)
