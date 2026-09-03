"""Fixtures exercising directive options and error paths."""

import typer

app = typer.Typer(help="Say [bold]hi[/bold] to everyone.")


@app.command()
def hello(name: str):
    """Say [bold]hello[/bold]."""
    typer.echo(name)


@app.command(hidden=True)
def secret():
    """A hidden command."""


def svg_kwargs(directive, name, command, ctx, parent):
    """A callable render option returning export kwargs."""
    return {"title": f"custom title for {name}"}


def bad_kwargs(directive, name, command, ctx, parent):
    """A callable render option returning the wrong type."""
    return ["not", "a", "dict"]


not_an_app = 42


def command_factory():
    """A callable returning an already converted click command."""
    return typer.main.get_command(app)
