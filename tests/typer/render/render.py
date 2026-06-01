import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command()
def render(
    count: Annotated[int, typer.Option(help="A positive even number.")] = 2,
    foo: Annotated[str, typer.Option(help="A mysterious parameter.")] = "",
    url: Annotated[str, typer.Option(help="A URL.")] = "",
):
    """
    Render.

    This example exercises the html (iframe), svg, text and png renderings of a
    Typer app, along with the configurable render hooks (typer_render_html,
    typer_get_iframe_height, typer_svg2pdf and typer_convert_png).
    """
    typer.echo(f"count: {count}")
    typer.echo(f"foo: {foo}")
    typer.echo(f"url: {url!r}")


if __name__ == "__main__":
    app()
