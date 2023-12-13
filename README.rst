sphinx-typer
==============

.. _Typer: https://typer.tiangolo.com/
.. _Click: https://click.palletsprojects.com/
.. _sphinx-clock: https://sphinx-click.readthedocs.io/en/latest/

A Sphinx directive for auto generating docs for Typer_ commands. Typer_ is a typed 
interface built on top of Click_. This means that the sphinx-click_ package will also
work to generate documentation and if your goal is to really customze the generated
documentation sphinx-click_ provides more hooks and functionality for doing that. 

The goal of sphinx-typer is to generate documentation that looks like the rich console
output of the typer commands. It is therefore less customizable than the sphinx-click_
generated docs.

