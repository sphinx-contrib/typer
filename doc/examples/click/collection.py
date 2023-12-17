import click

@click.group()
def cli1():
    pass

@cli1.command()
def cmd1():
    """Command1 on cli1"""

@click.group()
def cli2():
    pass

@cli2.command()
def cmd2():
    """Command2 on cli2"""

@cli2.command()
def cmd3():
    """Command3 on cli2"""

cli = click.CommandCollection(sources=[cli1, cli2])

if __name__ == "__main__":
    cli()
