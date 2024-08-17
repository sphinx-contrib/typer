import typer
from composite.group import app as subgroup, AlphOrder

app = typer.Typer(help="Lets do stuff with strings.", cls=AlphOrder)

app.add_typer(subgroup, name="subgroup")


def repeat(string: str, count: int):
    typer.echo(string * count)


app.command(help="Repeat the string a given number of times.")(repeat)

if __name__ == "__main__":
    app()
