|MIT license| |PyPI version fury.io| |PyPI pyversions| |PyPI status| |Documentation Status|
|Code Cov| |Test Status|

.. |MIT license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://lbesson.mit-license.org/

.. |PyPI version fury.io| image:: https://badge.fury.io/py/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer/

.. |PyPI status| image:: https://img.shields.io/pypi/status/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer

.. |Documentation Status| image:: https://readthedocs.org/projects/sphinxcontrib-typer/badge/?version=latest
   :target: http://sphinxcontrib-typer.readthedocs.io/?badge=latest/

.. |Code Cov| image:: https://codecov.io/gh/bckohan/sphinxcontrib-typer/branch/main/graph/badge.svg?token=0IZOKN2DYL
   :target: https://codecov.io/gh/bckohan/sphinxcontrib-typer

.. |Test Status| image:: https://github.com/bckohan/sphinxcontrib-typer/workflows/test/badge.svg
   :target: https://github.com/bckohan/sphinxcontrib-typer/actions


sphinxcontrib-typer
===================

.. _Typer: https://typer.tiangolo.com/
.. _Click: https://click.palletsprojects.com/
.. _sphinx-click: https://sphinx-click.readthedocs.io/en/latest/

A Sphinx directive for auto generating docs for Typer_ commands. Typer_ is a typed 
interface built on top of Click_. This means that the sphinx-click_ package will also
work to generate documentation and if your goal is to customize the generated
documentation sphinx-click_ provides more hooks and functionality for doing that. 

The goal of sphinxcontrib-typer is to generate documentation that looks like the rich console
output of the typer commands. It is therefore less customizable than the sphinx-click_
generated docs.

