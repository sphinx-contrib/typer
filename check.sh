poetry run ruff format sphinxcontrib/typer
poetry run ruff check --fix --select I sphinxcontrib/typer
poetry run ruff check --fix sphinxcontrib/typer
poetry check
poetry run pip check
