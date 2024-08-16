import typer
from composite.echo import echo
from composite.multiply import multiply

app = typer.Typer(help="Subcommands are here.")

app.command(name="echo", help="Echo the string.")(echo)
app.command(name="multiply", help="Multiply 2 numbers.")(echo)
