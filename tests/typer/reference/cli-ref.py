import typer

app = typer.Typer()


def reference(name: str):
    typer.echo(name)


app.command(help="CLI ref tests.")(reference)

if __name__ == "__main__":
    app()
