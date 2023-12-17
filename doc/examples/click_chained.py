import click

@click.group(chain=True, invoke_without_command=True)
@click.option('-i', '--input', type=click.File('r'))
def cli(input):
    pass

@cli.result_callback()
def process_pipeline(processors, input):
    iterator = (x.rstrip('\r\n') for x in input)
    for processor in processors:
        iterator = processor(iterator)
    for item in iterator:
        click.echo(item)

@cli.command('uppercase')
def make_uppercase():
    def processor(iterator):
        for line in iterator:
            yield line.upper()
    return processor

@cli.command('lowercase')
def make_lowercase():
    def processor(iterator):
        for line in iterator:
            yield line.lower()
    return processor

@cli.command('strip')
def make_strip():
    def processor(iterator):
        for line in iterator:
            yield line.strip()
    return processor

if __name__ == '__main__':
    cli()
