Sphinx
###########################
From the backend/docs directory you can build HTML docs with:

- make html (Linux/macOS) or
- .\make.bat html (Windows)

The site will be generated in build/html.

Run make preview or make reload to view the site.

The live-reload server is available at http://127.0.0.1:8001/ by default.
Override the port with ``make reload Sphinx_port=<port>`` if needed.
