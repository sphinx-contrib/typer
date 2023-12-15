import pytest
from sphinx.application import Sphinx
import os
from pathlib import Path

DOC_DIR = Path(__file__).parent.parent / 'doc'
SRC_DIR = DOC_DIR / 'source'
BUILD_DIR = DOC_DIR / 'build'



def test_sphinx_html_build():
    """
    The documentation is extensive and exercises most of the features of the extension so
    we just check to see that our documentation builds!
    """
    
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
