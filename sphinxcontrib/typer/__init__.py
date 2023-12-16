r"""
   _____       _     _             _____            _        _ _                  
  / ____|     | |   (_)           / ____|          | |      (_| |                 
 | (___  _ __ | |__  _ _ __ __  _| |     ___  _ __ | |_ _ __ _| |__               
  \___ \| '_ \| '_ \| | '_ \\ \/ | |    / _ \| '_ \| __| '__| | '_ \              
  ____) | |_) | | | | | | | |>  <| |___| (_) | | | | |_| |  | | |_) |             
 |_____/| .__/|_| |_|_|_| |_/_/\_\\_____\___/|_| |_|\__|_|  |_|_.__/              
        | |                                                                       
        |_|                                                                       
                      _______                                                     
                     |__   __|                                                    
                        | |_   _ _ __   ___ _ __                                  
                        | | | | | '_ \ / _ | '__|                                 
                        | | |_| | |_) |  __| |                                    
                        |_|\__, | .__/ \___|_|                                    
                            __/ | |                                               
                           |___/|_|                                               

"""
import base64
import contextlib
import io
import json
import re
import traceback
import typing as t
import os
from html import escape as html_escape
from importlib import import_module
from pathlib import Path
import hashlib
import click
from enum import Enum 
from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from rich.console import Console
from rich.theme import Theme
from sphinx import application
from sphinx.util import logging

from typer import rich_utils as typer_rich_utils
from typer.main import Typer, TyperCommand, TyperGroup
from typer.main import get_command as get_typer_command
from typer.models import Context as TyperContext

VERSION = (0, 1, 0)

__title__ = 'SphinxContrib Typer'
__version__ = '.'.join(str(i) for i in VERSION)
__author__ = 'Brian Kohan'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Brian Kohan'


def _get_lazyload_commands(ctx: TyperContext) -> t.Dict[str, TyperCommand]:
    commands = {}
    for command in ctx.command.list_commands(ctx):
        commands[command] = ctx.command.get_command(ctx, command)

    return commands


def _filter_commands(
    ctx: TyperContext,
    commands: t.Optional[t.List[str]] = None,
) -> t.List[TyperCommand]:
    """Return list of used commands."""
    lookup = getattr(ctx.command, 'commands', {})
    if not lookup and isinstance(ctx.command, click.MultiCommand):
        lookup = _get_lazyload_commands(ctx)

    if commands is None:
        return sorted(lookup.values(), key=lambda item: item.name)

    return [lookup[command] for command in commands if command in lookup]


class RenderTarget(str, Enum):
    HTML = 'html'
    SVG = 'svg'
    TEXT = 'text'

    def __str__(self) -> str:
        return self.value

    @classmethod
    def __missing__(cls, argument) -> str:
        if argument:
            raise ValueError(
                f'"{argument}" is not a valid RenderTarget: '
                f'{[str(target) for target in cls]}'
            )
        return None


Command = t.Union[TyperCommand, TyperGroup]

"""
Callbacks that return a dict of kwargs to pass to various renderer functions
must all have the RenderCallback function signature:
"""
RenderCallback = t.Callable[
    [
        'TyperDirective',  # directive - the TyperDirective instance
        str,  # name - the name of the command
        Command,  # command - the command instance
        TyperContext,  # ctx - the TyperContext instance
        t.Optional[TyperContext],  # parent - the parent TyperContext instance
    ],
    t.Dict[str, t.Any],
]

"""
Custom render options can be provided at a python path that resolves to the
following type. Either a dictionary of kwargs to pass to the relevant function
or a callable that returns a dictionary of kwargs to pass to the relevant function
"""
RenderOptions = t.Union[t.Dict[str, t.Any], RenderCallback]


class TyperDirective(rst.Directive):
    logger = logging.getLogger('sphinxcontrib.typer')

    has_content = False
    required_arguments = 1
    option_spec = {
        'prog': directives.unchanged_required,
        'make-sections': directives.flag,
        'show-nested': directives.flag,
        'width': directives.nonnegative_int,
        'svg_kwargs': directives.unchanged,
        'text_kwargs': directives.unchanged,
        'html_kwargs': directives.unchanged,
        'console_kwargs': directives.unchanged,
        'preferred': RenderTarget,
        'builders': directives.unchanged,
        'iframe_height': directives.nonnegative_int,
    }

    # resolved options
    prog_name: str
    nested: bool
    make_sections: bool
    width: int
    iframe_height: t.Optional[int] = None

    console: Console

    preferred: t.Optional[RenderTarget] = None

    # the console_kwargs option can be a dict or a callable that returns a dict, the callable
    # must conform to the RenderOptions signature
    console_kwargs: RenderOptions

    html_kwargs: RenderOptions
    svg_kwargs: RenderOptions
    text_kwargs: RenderOptions

    target: RenderTarget

    builder_targets = {
        **{
            builder: [RenderTarget.SVG, RenderTarget.HTML, RenderTarget.TEXT]
            for builder in [
                'html',
                'dirhtml',
                'singlehtml',
                'htmlhelp',
                'qthelp',
                'devhelp',
            ]
        },
        'epub': [RenderTarget.HTML, RenderTarget.SVG, RenderTarget.TEXT],
        **{
            builder: [RenderTarget.SVG, RenderTarget.TEXT]
            for builder in ['latex', 'latexpdf', 'texinfo']
        },
        **{builder: [RenderTarget.TEXT] for builder in ['text', 'gettext']},
    }

    @property
    def builder(self) -> str:
        return self.env.app.builder.name

    def uuid(self, normal_cmd: str) -> str:
        """
        Get a repeatable unique hash id for a given directive instance and command.

        This is used to generate repeatable unique filenames for any build artifacts
        like svg -> pdf conversions.

        :param normal_cmd: The normalized command name
        """
        # Contextual information
        source = self.state_machine.get_source_and_line()[0]
        line_number = self.state_machine.get_source_and_line()[1]
        return hashlib.sha256(
            f"{source}.{line_number}[{normal_cmd}]".encode('utf-8')
        ).hexdigest()[:8]

    def import_object(
        self,
        obj_path: t.Optional[str],
        accessor: t.Callable[[t.Any, str], t.Any] = lambda obj, attr: getattr(
            obj, attr
        ),
    ) -> t.Any:
        """
        Imports an arbitrary object from a python string path.
        Delimiters can be '.', '::' or ':'.

        :param obj_path: The python path to the object, if False, returns None
        """
        if not obj_path:
            return None
        parts = re.split(r'::|[.:]', obj_path)
        tries = 1
        try:
            while True:
                # walk up the import path until we find something importable
                # then walk down the path fetching all the attributes
                # this allows import strings to reach into nested class
                # attributes
                try:
                    tries += 1
                    obj = import_module('.'.join(parts[0 : -(tries - 1)]))
                    for attr in parts[-(tries - 1) :]:
                        obj = accessor(obj, attr)
                    break
                except (ImportError, ModuleNotFoundError):
                    if tries >= len(parts):
                        raise

        except (Exception, SystemExit) as exc:
            err_msg = f'Failed to import "{obj_path}"'
            if isinstance(exc, SystemExit):
                err_msg += 'The module appeared to call sys.exit().'
            else:
                err_msg += 'The following exception was raised:\n{}'.format(
                    traceback.format_exc()
                )

            raise self.error(err_msg)

        return obj

    def load_root_command(
        self, typer_path: str
    ) -> t.Union[TyperCommand, TyperGroup]:
        """
        Load the module.

        :param typer_path: The python path to the Typer app instance.
        """

        def resolve_root_command(obj):
            if isinstance(obj, (TyperCommand, TyperGroup)):
                return obj

            if isinstance(obj, Typer):
                return get_typer_command(obj)

            if callable(obj):
                ret = obj()
                if isinstance(ret, Typer):
                    return get_typer_command(obj)
                if isinstance(ret, (TyperCommand, TyperGroup)):
                    return ret

            raise self.error(
                f'"{typer_path}" of type {type(obj)} is not Typer, TyperCommand or '
                'TyperGroup.'
            )

        def access_command(obj, attr) -> t.Union[TyperCommand, TyperGroup]:
            try:
                return resolve_root_command(getattr(obj, attr))
            except Exception:
                cmds = _filter_commands(
                    TyperContext(resolve_root_command(obj)), [attr]
                )
                if cmds:
                    return cmds[0]
                raise

        return resolve_root_command(
            self.import_object(typer_path, accessor=access_command)
        )

    def generate_nodes(
        self, name: str, command: TyperCommand, parent: t.Optional[TyperContext]
    ) -> t.List[nodes.section]:
        """
        Generate the relevant Sphinx nodes.

        Generate node help for `TyperGroup` or `TyperCommand`.

        :param command: Instance of `TyperGroup` or `TyperCommand`
        :param parent: Instance of `typer.models.Context`, or None
        :returns: A list of nested docutil nodes
        """
        ctx = TyperContext(
            command,
            info_name=name,
            parent=parent,
            terminal_width=self.width,
            max_content_width=self.width,
        )

        if command.hidden:
            return []

        source_name = ctx.command_path
        normal_cmd = ':'.join(source_name.split(' '))

        section = (
            nodes.section(
                '',
                nodes.title(text=name),
                ids=[nodes.make_id(source_name)],
                names=[nodes.fully_normalize_name(source_name)],
            )
            if self.make_sections
            else nodes.container()
        )

        # Summary
        def resolve_options(
            options: RenderOptions, parameter: str
        ) -> t.Dict[str, t.Any]:
            if callable(options):
                options = options(self, name, command, ctx, parent)
            if isinstance(options, dict):
                return options
            raise self.error(
                f'Invalid {parameter}, must be a dict or callable, got {type(options)}'
            )

        def get_console(stderr: bool = False) -> Console:
            self.console = Console(
                theme=Theme(
                    {
                        "option": typer_rich_utils.STYLE_OPTION,
                        "switch": typer_rich_utils.STYLE_SWITCH,
                        "negative_option": typer_rich_utils.STYLE_NEGATIVE_OPTION,
                        "negative_switch": typer_rich_utils.STYLE_NEGATIVE_SWITCH,
                        "metavar": typer_rich_utils.STYLE_METAVAR,
                        "metavar_sep": typer_rich_utils.STYLE_METAVAR_SEPARATOR,
                        "usage": typer_rich_utils.STYLE_USAGE,
                    },
                ),
                highlighter=typer_rich_utils.highlighter,
                color_system=typer_rich_utils.COLOR_SYSTEM,
                force_terminal=typer_rich_utils.FORCE_TERMINAL,
                width=self.width or typer_rich_utils.MAX_WIDTH,
                stderr=stderr,
                # overrides any defaults above
                **resolve_options(self.console_kwargs, 'console_kwargs'),
                record=True,
            )
            return self.console

        # todo
        # typer provides no official way to alter the console that prints out the help
        # command so we have to monkey patch it - revisit in future if this changes!
        orig_getter = typer_rich_utils._get_rich_console
        typer_rich_utils._get_rich_console = get_console
        with contextlib.redirect_stdout(io.StringIO()):
            command.get_help(ctx)
        typer_rich_utils._get_rich_console = orig_getter
        ##############################################################################

        if self.target == RenderTarget.HTML:
            html_page = self.console.export_html(
                **resolve_options(self.html_kwargs, 'html_kwargs'), clear=False
            )
            section += nodes.raw(
                '',
                self.env.app.config.typer_render_html(
                    self, normal_cmd, html_page
                ),
                format='html',
            )
        elif self.target == RenderTarget.SVG:
            svg = self.console.export_svg(
                title=source_name,
                **resolve_options(self.svg_kwargs, 'svg_kwargs'),
                clear=False,
            )
            if 'html' in self.builder:
                section += nodes.raw('', svg, format='html')
            else:
                img_name = f'{normal_cmd.replace(":", "_")}_{self.uuid(normal_cmd)}'
                out_dir = Path(self.env.app.builder.outdir)
                (out_dir / f'{img_name}.svg').write_text(svg)
                pdf_img = out_dir / f'{img_name}.pdf'
                self.env.app.config.typer_svg2pdf(self, svg, pdf_img)
                section += nodes.image(uri=os.path.relpath(pdf_img, Path(self.env.srcdir)), alt=source_name)

        elif self.target == RenderTarget.TEXT:
            section += nodes.literal_block(
                '',
                self.console.export_text(
                    **resolve_options(self.svg_kwargs, 'svg_kwargs'),
                    clear=False,
                ),
            )
        else:
            raise self.error(f'Invalid typer render target: {self.target}')

        # recurse through subcommands if we should
        if self.nested and isinstance(command, click.MultiCommand):
            commands = _filter_commands(ctx, command.list_commands(ctx))
            for command in commands:
                section.extend(
                    self.generate_nodes(command.name, command, parent=ctx)
                )
        return [section]

    def run(self) -> t.Iterable[nodes.section]:
        self.env = self.state.document.settings.env

        command = self.load_root_command(self.arguments[0])

        if 'prog' not in self.options:
            raise self.error(':prog: must be specified')

        self.make_sections = 'make-sections' in self.options
        self.nested = 'show-nested' in self.options
        self.prog_name = self.options.get('prog')
        self.width = self.options.get('width', 80)
        self.iframe_height = self.options.get('iframe_height', None)
        self.console_kwargs = (
            self.import_object(self.options.get('console_kwargs', None)) or {}
        )
        self.html_kwargs = (
            self.import_object(self.options.get('html_kwargs', None)) or {}
        )
        self.svg_kwargs = (
            self.import_object(self.options.get('svg_kwargs', None)) or {}
        )
        self.txt_kwargs = (
            self.import_object(self.options.get('txt_kwargs', None)) or {}
        )
        self.preferred = self.options.get('preferred', None)

        builder_targets = {}
        for builder_target in self.options.get('builders', '').split(':'):
            if builder_target.strip():
                builder, targets = builder_target.split('=')[0:2]
                builder_targets[builder.strip()] = [
                    RenderTarget(target.strip())
                    for target in targets.split(',')
                ]

        builder_targets = {**builder_targets, **self.builder_targets}

        if self.builder not in builder_targets:
            self.target = self.preferred or RenderTarget.TEXT
            self.logger.debug(
                'Unable to resolve render target for builder: %s - using: %s',
                self.builder,
                self.target,
            )
        else:
            supported = builder_targets[self.builder]
            self.target = (
                self.preferred if self.preferred in supported else supported[0]
            )
        return self.generate_nodes(self.prog_name, command, None)


def visit_fixed_text_element_html(self, node):
    # Get the text of the node
    text = node.astext()

    # Wrap the text in <pre> tags and create a new raw node
    raw_node = nodes.raw('', f'<pre>{text}</pre>', format='html')

    # Replace the FixedTextElement node with the raw node
    node.replace_self(raw_node)


def get_iframe_height(
    directive: TyperDirective, normal_cmd: str, html_page: str
) -> int:
    """
    The default iframe height calculation function. The iframe height resolution proceeds as follows:

    1) Return the global iframe_height parameter if one was supplied as a parameter on the directive.
    2) Check for a cached height value using the file at config.typer_iframe_height_cache_path and return
       one if it exists.
    3) Attempt to use Selenium to dynamically determine the height of the iframe. Padding will be added
       from the config.typer_iframe_height_padding configuration value. The resulting height is then
       cached back to config.typer_iframe_height_cache_path if that path is not None. If the attempt
       to use Selenium fails (it is not installed) a warning is issued and a default height of 600 is
       returned.

    :param config: The SphinxConfig instance
    :param html_page: The full html document that will be rendered in the iframe
    """
    if directive.iframe_height is not None:
        return directive.iframe_height

    cache = {'iframe_heights': {}}
    cache_path = (
        None
        if not directive.env.app.config.typer_iframe_height_cache_path
        else Path(directive.env.app.config.typer_iframe_height_cache_path)
    )
    if cache_path and cache_path.is_file():
        cache = json.loads(cache_path.read_text())
        cache.setdefault('iframe_heights', {})

    if cache['iframe_heights'].get(normal_cmd):
        return cache['iframe_heights'][normal_cmd]

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        directive.logger.warning(
            f'Unable to dynimcally determine iframe height for {normal_cmd} '
            f'either supply an iframe_height parameter or see instructions at: '
            f'https://sphinxcontrib-typer.readthedocs.io. Using a default value '
            f'of 600.'
        )
        return 600

    # Set up headless browser options
    options = Options()
    options.headless = True

    # Initialize WebDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # use base64 to avoid issues with special characters
    driver.get(
        f'data:text/html;base64,'
        f'{base64.b64encode(html_page.encode("utf-8")).decode()}'
    )
    height = (
        int(
            driver.execute_script(
                'return document.documentElement.getBoundingClientRect().height'
            )
        )
        + directive.env.app.config.typer_iframe_height_padding
    )
    cache['iframe_heights'][normal_cmd] = height
    if cache_path:
        cache_path.write_text(json.dumps(cache, indent=4))
    return height


def render_html_iframe(
    directive: TyperDirective, normal_cmd: str, html_page: str
) -> str:
    """
    The default html rendering function. This function returns the html console
    output wrapped in an iframe. The height of the iframe is dynamically determined
    by calling the configured typer_get_iframe_height function.
    """

    height = directive.env.app.config.typer_get_iframe_height(
        directive, normal_cmd, html_page
    )
    return (
        f'<iframe style="border: none;" width="100%" height="'
        f'{height}px"'
        f' srcdoc="{html_escape(html_page)}"></iframe>'
    )


def svg2pdf(directive: TyperDirective, svg_contents: str, pdf_path: str):
    """
    The default svg2pdf function. This function uses the cairosvg package to
    convert svg to pdf.

    .. note::

        You will likely need to install fonts locally on your machine for the output
        of these conversions to look correct. The default font used by the svg
        export from rich is `FiraCode <https://github.com/tonsky/FiraCode/wiki/Installing>`_.
    """
    try:
        import cairosvg
        cairosvg.svg2pdf(bytestring=svg_contents, write_to=str(pdf_path))
    except ImportError:
        directive.error(f'cairosvg must be installed to render SVG in pdfs')


def setup(app: application.Sphinx) -> t.Dict[str, t.Any]:
    # Need autodoc to support mocking modules
    app.add_directive('typer', TyperDirective)

    # todo - why doesn't this already work like this?
    app.add_node(
        nodes.FixedTextElement, html=(visit_fixed_text_element_html, None)
    )

    app.add_config_value(
        'typer_render_html', lambda _: render_html_iframe, 'env'
    )
    app.add_config_value(
        'typer_get_iframe_height', lambda _: get_iframe_height, 'env'
    )
    app.add_config_value(
        'typer_svg2pdf', lambda _: svg2pdf, 'env'
    )
    app.add_config_value('typer_iframe_height_padding', 30, 'env')
    app.add_config_value(
        'typer_iframe_height_cache_path',
        Path(app.confdir) / 'typer_cache.json',
        'env',
    )

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
