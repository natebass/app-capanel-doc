Project_root := $(abspath ..)
Venv_directory := $(Project_root)/.venv
Uv ?= uv
Sphinx_options ?=
Source_directory = source
Build_directory = build
ifeq ($(OS),Windows_NT)
	Python := $(Venv_directory)/Scripts/python.exe
	Set_python_path := set Python_path=$(Project_root) &&
else
	Python := $(Venv_directory)/bin/python
	Set_python_path := Python_path=$(Project_root)
endif
SPHINX_BUILD := Python_path=$(Project_root) $(Python) -m sphinx

help: docs-deps
	@$(Set_python_path) $(Python) -m sphinx -M help "$(Source_directory)" "$(Build_directory)" $(Sphinx_options) $(O)
.PHONY: help docs-deps clean preview Makefile
$(Venv_directory):
	cd $(Project_root) && $(Uv) venv .venv
docs-deps: $(Venv_directory)
	cd $(Project_root) && $(Uv) sync --all-groups
clean:
	rm -rf $(Build_directory)/*
html: docs-deps
	$(Set_python_path) $(Python) -m sphinx -b html "$(Source_directory)" "$(Build_directory)/html" $(Sphinx_options)
preview: html
	@echo "Opening documentation in browser..."
ifeq ($(OS),Windows_NT)
	cmd /c start "" "$(abspath $(Build_directory)/html/index.html)"
else ifeq ($(shell uname),Darwin)
	open "$(Build_directory)/html/index.html"
else
	xdg-open "$(Build_directory)/html/index.html"
endif
reload: docs-deps
	$(Set_python_path) sphinx-autobuild "$(Source_directory)" "$(Build_directory)/html" $(Sphinx_options) --host 192.168.7.81
%: docs-deps
	@$(Set_python_path) $(Python) -m sphinx -M $@ "$(Source_directory)" "$(Build_directory)" $(Sphinx_options) $(O)
reload-intellij: docs-deps
	 $(Set_python_path) $(Python) -m sphinx -b html source build/html
