
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/sphinxcontrib-typer.svg)](https://pypi.python.org/pypi/sphinxcontrib-typer/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/sphinxcontrib-typer.svg)](https://pypi.python.org/pypi/sphinxcontrib-typer/)
[![PyPI status](https://img.shields.io/pypi/status/sphinxcontrib-typer.svg)](https://pypi.python.org/pypi/sphinxcontrib-typer)
[![Documentation Status](https://readthedocs.org/projects/sphinxcontrib-typer/badge/?version=latest)](http://sphinxcontrib-typer.readthedocs.io/?badge=latest/)
[![Code Cov](https://codecov.io/gh/sphinx-contrib/typer/branch/main/graph/badge.svg?token=0IZOKN2DYL)](https://app.codecov.io/gh/sphinx-contrib/typer)
[![Test Status](https://github.com/sphinx-contrib/typer/workflows/test/badge.svg)](https://github.com/sphinx-contrib/typer/actions/workflows/test.yml)
[![Lint Status](https://github.com/sphinx-contrib/typer/workflows/lint/badge.svg)](https://github.com/sphinx-contrib/typer/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# sphinxcontrib-typer

A Sphinx directive for auto generating docs for [Typer](https://typer.tiangolo.com/) 
(and [Click](https://click.palletsprojects.com/) commands!) using the rich console
formatting available in [Typer](https://typer.tiangolo.com/). This package generates
concise command documentation in text, html or svg formats out of the box, but if your
goal is to greatly customize the generated documentation
[sphinx-click](https://sphinx-click.readthedocs.io/en/latest/) may be more appropriate
and will also work for [Typer](https://typer.tiangolo.com/) commands.

## Installation

Install with pip::

    pip install sphinxcontrib-typer

Add ``sphinxcontrib.typer`` to your ``conf.py`` file:

```python
# be sure that the commands you want to document are importable
# from the python path when building the docs
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '../path/to/your/commands'))

extensions = [
    ...
    'sphinxcontrib.typer',
    ...
]
```

## Usage

Say you have a command in the file ``examples/example.py`` that looks like
this:

```python
import typer
import typing as t

app = typer.Typer(add_completion=False)

@app.callback()
def callback(
    flag1: bool = typer.Option(False, help="Flag 1."),
    flag2: bool = typer.Option(False, help="Flag 2.")
):
    """This is the callback function."""
    pass


@app.command()
def foo(
    name: str = typer.Option(..., help="The name of the item to foo.")
):
    """This is the foo command."""
    pass


@app.command()
def bar(
    names: t.List[str] = typer.Option(..., help="The names of the items to bar."),
):
    """This is the bar command."""
    pass


if __name__ == "__main__":
    app()
```

You can generate documentation for this command using the ``typer`` directive
like so:

```rst
.. typer:: examples.example.app
    :prog: example1
    :width: 70
    :preferred: html
```

This would generate html that looks like this:

![Example PNG](https://raw.githubusercontent.com/sphinx-contrib/typer/main/example.html.png)

You could change ``:preferred:`` to svg, to generate svg instead:

![Example SVG](https://raw.githubusercontent.com/sphinx-contrib/typer/main/example.svg)

|

Or to text
                                                                                            
    Usage: example [OPTIONS] COMMAND [ARGS]...                                                  
                                                                                                
    This is the callback function.                                                              
                                                                                                
    ╭─ Options ──────────────────────────────────────────────────────────╮
    │ --flag1    --no-flag1      Flag 1. [default: no-flag1]             │
    │ --flag2    --no-flag2      Flag 2. [default: no-flag2]             │
    │ --help                     Show this message and exit.             │
    ╰────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ─────────────────────────────────────────────────────────╮
    │ bar           This is the bar command.                             │
    │ foo           This is the foo command.                             │
    ╰────────────────────────────────────────────────────────────────────╯


The ``typer`` directive has options for generating docs for all subcommands as well
and optionally generating independent sections for each. There are also mechanisms
for passing options to the underlying console and svg generation functions. See the
official documentation for more information.
