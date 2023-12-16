import pytest
from sphinx.application import Sphinx
import os
from pathlib import Path
import shutil

DOC_DIR = Path(__file__).parent.parent / 'doc'
SRC_DIR = DOC_DIR / 'source'
BUILD_DIR = DOC_DIR / 'build'



def test_sphinx_html_build():
    """
    The documentation is extensive and exercises most of the features of the extension so
    we just check to see that our documentation builds!
    """
    shutil.rmtree(BUILD_DIR / 'html', ignore_errors=True)
    if (SRC_DIR / 'typer_cache.json').exists():
        os.remove(SRC_DIR / 'typer_cache.json')

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR,
        BUILD_DIR / 'doctrees',
        buildername='html'
    )

    # Build the documentation
    app.build()

    # Test passes if no Sphinx errors occurred during build
    assert not app.statuscode, "Sphinx documentation build failed"


def test_sphinx_text_build():
    
    shutil.rmtree(BUILD_DIR / 'text', ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR,
        BUILD_DIR / 'doctrees',
        buildername='text'
    )

    # Build the documentation
    app.build()

    assert not app.statuscode, "Sphinx documentation build failed"


def test_sphinx_latex_build():
    
    shutil.rmtree(BUILD_DIR / 'latex', ignore_errors=True)

    # Create a Sphinx application instance
    app = Sphinx(
        SRC_DIR,
        SRC_DIR,
        BUILD_DIR,
        BUILD_DIR / 'doctrees',
        buildername='latex'
    )

    # Build the documentation
    app.build()

    assert not app.statuscode, "Sphinx documentation build failed"

