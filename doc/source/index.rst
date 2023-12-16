===================
sphinxcontrib-typer
===================

.. _Typer: https://typer.tiangolo.com/
.. _Click: https://click.palletsprojects.com/
.. _sphinx-click: https://sphinx-click.readthedocs.io/en/latest/

A Sphinx directive for auto generating docs for Typer_ (and Click_ commands!)
using the rich console formatting available in Typer_. This package generates
beautiful command documentation in text, html or svg formats out of the box,
but if your goal is to greatly customize the generated documentation
sphinx-click_ may be more appropriate and will also work for Typer_ commands.

Installation
============

Install with pip::

    pip install sphinxcontrib-typer

Add ``sphinxcontrib.typer`` to your ``conf.py`` file:

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

Usage
=====

Say you have a command in the file ``examples/example.py`` that looks like
this:

.. literalinclude:: ../examples/example.py
   :language: python

You can generate documentation for this command using the ``typer`` directive
like so:

.. code-block:: rst

    .. typer:: examples.example.app
        :prog: example1
        :width: 70
        :preferred: html


This would generate html that looks like this:

.. typer:: examples.example.app
   :prog: example
   :width: 70
   :preferred: html


You could change ``:preferred:`` to svg, to generate svg instead:

.. typer:: examples.example.app
   :prog: example
   :preferred: svg

|

Or to text:

.. typer:: examples.example.app
   :prog: example
   :preferred: text
   :width: 93


The ``typer`` directive has options for generating docs for all subcommands as
well and optionally generating independent sections for each. There are also
mechanisms for passing options to the underlying console and svg generation
functions. See table of contents for more information.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
