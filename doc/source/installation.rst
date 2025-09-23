.. include:: ./refs.rst

Installation
============

The basic library can be installed with pip:

.. code-block:: bash

    ?> pip install sphinxcontrib-typer

There are several optional dependency sets that are involved in more advanced automated rendering.
If you want to use :pypi:`selenium` to automatically determine the heights of the iframes when
rendering in html you should install the html extras:

.. code-block:: bash

    ?> pip install sphinxcontrib-typer[html]

If you wish to convert rendered docs to png images you'll need the png dependency set:

.. code-block:: bash

    ?> pip install sphinxcontrib-typer[png]

If you wish to convert rendered docs to pdf format you'll need the pdf dependency set:

.. code-block:: bash

    ?> pip install sphinxcontrib-typer[pdf]


Once installed you need to add ``sphinxcontrib.typer`` to your ``conf.py`` file:

.. code-block:: python

    # be sure that the commands you want to document are importable
    # from the python path when building the docs
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / 'path/to/your/commands'))

    extensions = [
        ...
        'sphinxcontrib.typer',
        ...
    ]
