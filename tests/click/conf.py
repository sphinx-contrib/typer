from datetime import datetime
import sys
from pathlib import Path
from sphinxcontrib import typer as sphinxcontrib_typer
import json
import os

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# get all sub directories from here and add them to the path
sys.path.append(str(Path(__file__).parent))
for path in Path(__file__).parent.iterdir():
    if path.is_dir():
        sys.path.append(str(path))


# -- Project information -----------------------------------------------------

project = "SphinxContrib Typer Tests"
copyright = f"2023-{datetime.now().year}, Brian Kohan"
author = "Brian Kohan"

# The full version, including alpha/beta/rc tags
release = sphinxcontrib_typer.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_rtd_theme", "sphinxcontrib.typer"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

todo_include_todos = True

###########################################################
# Test our typer configuration parameter function overrides

typer_render_html = "callbacks.typer_render_html"
typer_get_iframe_height = "callbacks.typer_get_iframe_height"
typer_svg2pdf = "callbacks.typer_svg2pdf"
typer_convert_png = "callbacks.typer_convert_png"
typer_get_web_driver = "callbacks.typer_get_web_driver"

typer_iframe_height_padding = 40


def setup(app):
    app.connect("builder-inited", iframe_cache)


def iframe_cache(app):
    if not hasattr(app.env, "iframe_heights"):
        app.env.iframe_heights = {}
    app.env.iframe_heights["validation"] = 347
