
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

### Install Just

We provide a platform independent justfile with recipes for all the development tasks. You should [install just](https://just.systems/man/en/installation.html) if it is not on your system already.

`sphinxcontrib-typer` uses [uv](https://docs.astral.sh/uv) for environment, package and dependency management:

```bash
    just install-uv
```

Next, initialize and install the development environment:

```bash
    just setup <optional python version>
    just install
```

## Documentation

`sphinxcontrib-typer` documentation is generated using [Sphinx](https://www.sphinx-doc.org/en/master/). Any new feature PRs must provide updated documentation for the features added. To build the docs run:

```bash
    just docs
```

You can run a live documentation server that will automatically update during editing using:

```bash
    just docs-live
```

To build the pdf documentation:

```bash
    just build-docs-pdf
```

## Static Analysis

Before any PR is accepted the following must be run, and static analysis
tools should not produce any errors or warnings. Disabling certain errors
or warnings where justified is acceptable:


```bash
    just check
```


## Running Tests

`sphinxcontrib-typer` is setup to use [pytest](https://docs.pytest.org/en/stable/) to run unit tests. All the tests are housed in tests/tests.py. Before a PR is accepted, all tests must be passing and the code coverage must be at as high as it was before. A small number of exempted error handling branches are acceptable.

To run the full suite:

```bash
    just test
```

To run a single test, or group of tests in a class:


```bash
    just test <path_to_tests_file>::ClassName::FunctionName
```

For instance to run the docs test you would do:

```bash
    just test tests/tests.py::test_sphinx_html_build
```


## Just Recipes

```bash
    build                    # build src package and wheel
    build-docs               # build the docs
    build-docs-html          # build html documentation
    build-docs-pdf           # build pdf documentation
    check                    # run all static checks
    check-docs               # lint the documentation
    check-docs-links         # check the documentation links for broken links
    check-format             # check if the code needs formatting
    check-lint               # lint the code
    check-package            # run package checks
    check-readme             # check that the readme renders
    check-types              # run static type checking
    clean                    # remove all non repository artifacts
    clean-docs               # remove doc build artifacts
    clean-env                # remove the virtual environment
    clean-git-ignored        # remove all git ignored files
    coverage                 # generate the test coverage report
    coverage-erase           # erase any coverage data
    docs                     # build and open the documentation
    docs-live                # serve the documentation, with auto-reload
    fetch-refs LIB           # fetch the intersphinx references for the given package
    fix                      # fix formatting, linting issues and import sorting
    format                   # format the code and sort imports
    install *OPTS            # update and install development dependencies
    install-basic            # install without extra dependencies
    install-precommit        # install git pre-commit hooks
    install-uv               # install the uv package manager
    lint                     # sort the imports and fix linting issues
    open-docs                # open the html documentation
    precommit                # run the pre-commit checks
    release VERSION          # issue a relase for the given semver string (e.g. 2.1.0)
    run +ARGS                # run the command in the virtual environment
    setup python="python"    # setup the venv and pre-commit hooks
    sort-imports             # sort the python imports
    test *TESTS              # run tests
    test-lock +PACKAGES      # lock to specific python and versions of given dependencies
    validate_version VERSION # validate the given version string against the lib version
```