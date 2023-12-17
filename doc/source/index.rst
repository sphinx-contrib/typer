.. include:: ./refs.rst

===================
sphinxcontrib-typer
===================

A Sphinx directive for auto generating docs for Typer_ (and Click_ commands!)
using the rich console formatting available in Typer_. This package generates
concise command documentation in text, html or svg formats out of the box,
but if your goal is to greatly customize the generated documentation
sphinx-click_ may be more appropriate and will also work for Typer_ commands.

See the github_ repository for issue tracking and source code and install from
PyPI_ with ``pip install sphinxcontrib-typer``.

For example, commands and subcommands are renderable separately in three 
different formats svg, html and text:

.. typer:: examples.example.app
   :convert-png: latex

.. typer:: examples.example.app:foo
   :width: 70
   :preferred: html
   :convert-png: latex

.. typer:: examples.example.app:bar
   :width: 93
   :preferred: text
   :convert-png: latex


The ``typer`` directive has options for generating docs for all subcommands as
well and optionally generating independent sections for each. There are also
mechanisms for passing options to the underlying console and svg generation
functions. See table of contents for more information.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   installation
   usage
   builders
   click
   reference
   changelog
