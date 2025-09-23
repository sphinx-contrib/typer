.. include:: ./refs.rst

===================
sphinxcontrib-typer
===================

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://badge.fury.io/py/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer/
   :alt: PyPI pyversions

.. image:: https://img.shields.io/pypi/status/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer
   :alt: PyPI status

.. image:: https://readthedocs.org/projects/sphinxcontrib-typer/badge/?version=latest
   :target: http://sphinxcontrib-typer.readthedocs.io/?badge=latest/
   :alt: Documentation Status

.. image:: https://codecov.io/gh/sphinx-contrib/typer/branch/main/graph/badge.svg?token=0IZOKN2DYL
   :target: https://app.codecov.io/gh/sphinx-contrib/typer
   :alt: Code Cov

.. image:: https://github.com/sphinx-contrib/typer/workflows/Test/badge.svg
   :target: https://github.com/sphinx-contrib/typer/actions/workflows/test.yml
   :alt: Test Status

.. image:: https://github.com/sphinx-contrib/typer/workflows/Lint/badge.svg
   :target: https://github.com/sphinx-contrib/typer/actions/workflows/lint.yml
   :alt: Lint Status

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff


A Sphinx directive for auto generating docs for Typer_ (and :doc:`Click <click:index>` commands!)
using the rich console formatting available in Typer_. This package generates concise command
documentation in text, html or svg formats out of the box, but if your goal is to greatly customize
the generated documentation :doc:`sphinx-click:index` may be more appropriate and will also work for
Typer_ commands.

See the `github <https://github.com/sphinx-contrib/typer>`_ repository for issue tracking and source
code and install from :pypi:`sphinxcontrib-typer` with ``pip install sphinxcontrib-typer``.

For example, commands and subcommands are renderable separately in four different formats:

* svg
* html
* text
* png

.. typer:: examples.example.app
   :convert-png: latex
   :preferred: html

|

.. typer:: examples.example.app:foo
   :width: 70
   :preferred: html
   :convert-png: latex

|

.. typer:: examples.example.app:bar
   :width: 92
   :preferred: text
   :convert-png: latex


The ``typer`` directive has options for generating docs for all subcommands as well and optionally
generating independent sections for each. There are also mechanisms for passing options to the
underlying console and svg generation functions. See table of contents for more information.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   installation
   howto
   themes
   reference/index
   changelog
