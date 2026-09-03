import typer

app = typer.Typer(help="Root app defined in __main__.")
nested = typer.Typer(help="A nested group.")
app.add_typer(nested, name="nested")


@nested.command()
def command(name: str):
    """A nested command."""
    typer.echo(name)


@nested.command()
def other():
    """Another nested command."""


def main():
    app()


if __name__ == "__main__":
    main()
