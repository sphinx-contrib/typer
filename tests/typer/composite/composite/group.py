import typer
from composite.echo import echo
from composite.multiply import multiply
from typer.core import TyperGroup


class AlphOrder(TyperGroup):
    def list_commands(self, ctx):
        return reversed(sorted(super().list_commands(ctx)))


app = typer.Typer(help="Subcommands are here.", cls=AlphOrder)

app.command(name="echo", help="Echo the string.")(echo)
app.command(name="multiply", help="Multiply 2 numbers.")(multiply)
