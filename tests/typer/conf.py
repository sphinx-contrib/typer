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

TEST_CALLBACKS = Path(__file__).parent / "callback_record.json"

test_callbacks = {}


def record_callback(callback):
    """crude but it works"""
    if TEST_CALLBACKS.is_file():
        os.remove(TEST_CALLBACKS)
    test_callbacks[callback] = True
    TEST_CALLBACKS.write_text(json.dumps(test_callbacks))


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

typer_iframe_height_padding = 40
