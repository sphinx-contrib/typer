from datetime import datetime
import sys
from pathlib import Path
from contextlib import contextmanager
import platform
from sphinxcontrib import typer as sphinxcontrib_typer

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

sys.path.append(str(Path(__file__).parent.parent))


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
    'sphinx_rtd_theme',
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
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['style.css']
html_js_files = []

todo_include_todos = True

latex_engine = 'xelatex'


@contextmanager
def typer_get_web_driver(directive):
    import os
    
    if not os.environ.get('READTHEDOCS_BUILD', None):
        with sphinxcontrib_typer.typer_get_web_driver(directive) as driver:
            yield driver
        return
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    # Set up headless browser options
    options=Options()
    options.binary_location = os.path.expanduser("~/chrome/opt/google/chrome/google-chrome")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()
