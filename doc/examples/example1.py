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
