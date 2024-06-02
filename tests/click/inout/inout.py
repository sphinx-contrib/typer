import click


@click.command()
@click.argument("input", type=click.File("rb"), nargs=-1)
@click.argument("output", type=click.File("wb"))
def cli(input, output):
    """This script works similar to the Unix `cat` command but it writes
    into a specific file (which could be the standard output as denoted by
    the ``-`` sign).

    Copy stdin to stdout:
    ```bash
        inout - -
    ```

    Copy foo.txt and bar.txt to stdout:
    ```bash
        inout foo.txt bar.txt -
    ```

    Write stdin into the file foo.txt
    ```bash
        inout - foo.txt
    ```
    """
    for f in input:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            output.write(chunk)
            output.flush()


if __name__ == "__main__":
    cli()
