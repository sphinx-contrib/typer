
# Contributing

Contributions are encouraged! Please use the issue page to submit feature
requests or bug reports. Issues with attached PRs will be given priority and
have a much higher likelihood of acceptance. Please also open an issue and
associate it with any submitted PRs. That said, the aim is to keep this library
as lightweight as possible. Only features with broad based use cases will be
considered.

We are actively seeking additional maintainers. If you're interested, please
[contact me](https://github.com/bckohan).


## Installation

`sphinxcontrib-typer` uses [Poetry](https://python-poetry.org/) for environment, package and dependency
management:

```shell
poetry install
```

## Documentation

`sphinxcontrib-typer`  documentation is generated using [Sphinx](https://www.sphinx-doc.org/en/master/) with the [readthedocs](https://readthedocs.org/) theme. Any new feature PRs must provide updated documentation for
the features added. To build the docs run:

```bash
cd ./doc
poetry run doc8 --ignore-path build --max-line-length 100
poetry run make html latexpdf text
```

## Static Analysis

Before any PR is accepted the following must be run, and static analysis
tools should not produce any errors or warnings. Disabling certain errors
or warnings where justified is acceptable:

```bash
poetry run isort sphinxcontrib/typer
poetry run black sphinxcontrib/typer
poetry run doc8 -q doc
poetry check
poetry run pip check
poetry run python -m readme_renderer ./README.rst
```


## Running Tests

`sphinxcontrib-typer` is setup to use [pytest](https://docs.pytest.org/en/stable/)
to run unit tests. All the tests are housed in tests/tests.py. Before a PR is accepted,
all tests must be passing and the code coverage must be at 100%. A small number of
exempted error handling branches are acceptable.

To run the full suite:

```shell
poetry run pytest
```

To run a single test, or group of tests in a class:


```shell
poetry run pytest <path_to_tests_file>::ClassName::FunctionName
```

For instance to run the docs test you would do:

```shell
poetry run pytest tests/tests.py::test_sphinx_html_build
```

