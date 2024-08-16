import typer
import sys
from pprint import pprint
pprint(sys.path)
from composite.group import app as subgroup

app = typer.Typer(help="Lets do stuff with strings.")

app.add_typer(subgroup, name="subgroup")

def repeat(string: str, count: int):
    typer.echo(string*count)

app.command(help="Repeat the string a given number of timesss.")(repeat)

if __name__ == "__main__":
    app()
