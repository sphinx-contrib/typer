from datetime import datetime
import sys
from pathlib import Path
from sphinxcontrib import typer as sphinxcontrib_typer
import shutil

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent / 'typer_doc_ext'))


# -- Project information -----------------------------------------------------

project = 'sphinxcontrib-typer'
copyright = f'2023-{datetime.now().year}, Brian Kohan'
author = 'Brian Kohan'

# The full version, including alpha/beta/rc tags
release = sphinxcontrib_typer.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinxcontrib.typer'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'
html_theme_options = {
    "source_repository": "https://github.com/sphinx-contrib/typer/",
    "source_branch": "main",
    "source_directory": "doc/source",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['style.css']
html_js_files = []

todo_include_todos = True

latex_engine = 'xelatex'

typer_get_web_driver = 'web_driver.typer_get_web_driver'

def setup(app):
    if Path(app.doctreedir).exists():
        shutil.rmtree(app.doctreedir)
