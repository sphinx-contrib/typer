import typer
from typing_extensions import Annotated


def get_app() -> typer.Typer:
    """A factory callable that builds and returns a Typer app."""
    app = typer.Typer(add_completion=False)

    @app.command()
    def main(name: Annotated[str, typer.Option(help="Who to greet.")] = "world"):
        """Greet someone."""
        typer.echo(f"Hello {name}")

    return app


if __name__ == "__main__":
    get_app()()
