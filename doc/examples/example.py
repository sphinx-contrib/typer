import typer
import typing as t
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)

class Kind(StrEnum):

    ONE = "one"
    TWO = "two"


@app.callback()
def callback(
    arg: Annotated[Kind, typer.Argument(help="An argument.")],
    flag: Annotated[bool, typer.Option(help="Flagged.")] = False,
    switch: Annotated[
        bool,
        typer.Option("--switch", "-s", help="Switch.")
    ] = False
):
    """This is the callback function."""
    pass


@app.command()
def foo(
    name: Annotated[
        str,
        typer.Option(..., help="The name of the item to foo.")
    ]
):
    """This is the foo command."""
    pass


@app.command()
def bar(
    names: Annotated[
        t.List[str],
        typer.Option(..., help="The names of the items to bar.")
    ],
):
    """This is the bar command."""
    pass


if __name__ == "__main__":
    app()
