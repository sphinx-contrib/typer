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
import hashlib
import io
import json
import os
import re
import traceback
import typing as t
from contextlib import contextmanager
from enum import Enum
from html import escape as html_escape
from importlib import import_module
from pathlib import Path

import click
from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from rich import terminal_theme as rich_theme
from rich.console import Console
from rich.theme import Theme
from sphinx import application
from sphinx.util import logging
from typer import rich_utils as typer_rich_utils
from typer.main import Typer, TyperGroup
from typer.main import get_command as get_typer_command
from typer.models import Context as TyperContext

VERSION = (0, 1, 4)

__title__ = 'SphinxContrib Typer'
__version__ = '.'.join(str(i) for i in VERSION)
__author__ = 'Brian Kohan'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Brian Kohan'


def _get_lazyload_commands(ctx: click.Context) -> t.Dict[str, click.Command]:
    commands = {}
    for command in ctx.command.list_commands(ctx):
        commands[command] = ctx.command.get_command(ctx, command)

    return commands


def _filter_commands(
    ctx: click.Context,
    commands: t.Optional[t.List[str]] = None,
) -> t.List[click.Command]:
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


class RenderTheme(str, Enum):
    LIGHT = 'light'
    MONOKAI = 'monokai'
    DIMMED_MONOKAI = 'dimmed_monokai'
    NIGHT_OWLISH = 'night_owlish'
    DARK = 'dark'

    def __str__(self) -> str:
        return self.value

    @classmethod
    def __missing__(cls, argument) -> str:
        if argument:
            raise ValueError(
                f'"{argument}" is not a valid RenderTheme: '
                f'{[str(target) for target in cls]}'
            )
        return None

    @property
    def terminal_theme(self) -> rich_theme.TerminalTheme:
        return {
            RenderTheme.LIGHT: rich_theme.DEFAULT_TERMINAL_THEME,
            RenderTheme.MONOKAI: rich_theme.MONOKAI,
            RenderTheme.DIMMED_MONOKAI: rich_theme.DIMMED_MONOKAI,
            RenderTheme.NIGHT_OWLISH: rich_theme.NIGHT_OWLISH,
            RenderTheme.DARK: rich_theme.SVG_EXPORT_THEME,
        }[self]


Command = t.Union[click.Command, click.Group]

"""
Callbacks that return a dict of kwargs to pass to various renderer functions
must all have the RenderCallback function signature:
"""
RenderCallback = t.Callable[
    [
        'TyperDirective',  # directive - the TyperDirective instance
        str,  # name - the name of the command
        Command,  # command - the command instance
        click.Context,  # ctx - the click.Context instance
        t.Optional[click.Context],  # parent - the parent click.Context instance
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
    """
    A directive that renders a Typer app or Click command help text as either
    an html, text literal or svg image node depending on the builder and
    configuraton.

    Ex usage.

    .. code-block:: rst

        .. typer:: import.path.to.typer.app:subcommand
            :prog: script_name
    """

    logger = logging.getLogger('sphinxcontrib.typer')

    has_content = False
    required_arguments = 1
    option_spec = {
        'prog': directives.unchanged_required,
        'make-sections': directives.flag,
        'show-nested': directives.flag,
        'markup-mode': directives.unchanged,
        'width': directives.nonnegative_int,
        'theme': RenderTheme,
        'svg-kwargs': directives.unchanged,
        'text-kwargs': directives.unchanged,
        'html-kwargs': directives.unchanged,
        'console-kwargs': directives.unchanged,
        'preferred': RenderTarget,
        'builders': directives.unchanged,
        'iframe-height': directives.nonnegative_int,
        'convert-png': directives.unchanged,
    }

    # resolved options
    prog_name: str
    nested: bool
    make_sections: bool
    width: int
    iframe_height: t.Optional[int] = None
    typer_convert_png: bool = False

    console: Console
    parent: click.Context

    theme: RenderTheme = RenderTheme.LIGHT
    preferred: t.Optional[RenderTarget] = None

    markup_mode: typer_rich_utils.MarkupMode

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
        source = os.path.relpath(source, self.env.app.builder.srcdir)
        return hashlib.sha256(
            f"{source}.{line_number}[{normal_cmd}]".encode('utf-8')
        ).hexdigest()[:8]

    def import_object(
        self,
        obj_path: t.Optional[str],
        accessor: t.Callable[
            [t.Any, str], t.Any
        ] = lambda obj, attr, _: getattr(obj, attr),
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
                    try_path = '.'.join(parts[0 : -(tries - 1)])
                    obj = import_module(try_path)
                    for attr in parts[-(tries - 1) :]:
                        obj = accessor(obj, attr, try_path)
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

            raise self.severe(err_msg)

        return obj

    def load_root_command(
        self, typer_path: str
    ) -> t.Union[click.Command, click.Group]:
        """
        Load the module.

        :param typer_path: The python path to the Typer app instance.
        """

        def resolve_root_command(obj):
            if isinstance(obj, (click.Command, click.Group)):
                return obj

            if isinstance(obj, Typer):
                return get_typer_command(obj)

            if callable(obj):
                ret = obj()
                if isinstance(ret, Typer):
                    return get_typer_command(obj)
                if isinstance(ret, (click.Command, click.Group)):
                    return ret

            raise self.error(
                f'"{typer_path}" of type {type(obj)} is not Typer, click.Command or '
                'click.Group.'
            )

        def access_command(
            obj, attr, imprt_path
        ) -> t.Union[click.Command, click.Group]:
            try:
                return resolve_root_command(getattr(obj, attr))
            except Exception:
                self.parent = TyperContext(
                    resolve_root_command(obj),
                    # we can't trust the name attribute for the first
                    # command - but it is probably the best bet for
                    # subsequent commands - so if this is a nested
                    # import pull out the name attribute if it exists
                    # otherwise we use the last successful import path
                    # part because it is probably the module with main
                    info_name=(
                        (
                            getattr(obj, 'name', '')
                            if getattr(self, 'parent', None)
                            else ''
                        )
                        or imprt_path.split('.')[-1]
                    ),
                    parent=getattr(self, 'parent', None),
                )
                cmds = _filter_commands(self.parent, [attr])
                if cmds:
                    return cmds[0]
                raise

        return resolve_root_command(
            self.import_object(typer_path, accessor=access_command)
        )

    def get_html(self, **options):
        return self.console.export_html(
            **{'theme': self.theme.terminal_theme, **options, 'clear': False}
        )

    def get_svg(self, **options):
        return self.console.export_svg(
            **{'theme': self.theme.terminal_theme, **options, 'clear': False}
        )

    def get_text(self, **options):
        return self.console.export_text(**{**options, 'clear': False})

    def generate_nodes(
        self,
        name: str,
        command: click.Command,
        parent: t.Optional[click.Context],
    ) -> t.List[nodes.section]:
        """
        Generate the relevant Sphinx nodes.

        Generate node help for `click.Group` or `click.Command`.

        :param command: Instance of `click.Group` or `click.Command`
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
                nodes.title(
                    text=(
                        name
                        if not getattr(self, 'parent', None)
                        else f'{self.parent.command_path} {name}'
                    )
                ),
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
            raise self.severe(
                f'Invalid {parameter}, must be a dict or callable, got {type(options)}'
            )

        def get_console(stderr: bool = False) -> Console:
            self.console = Console(
                **{
                    'theme': Theme(
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
                    'highlighter': typer_rich_utils.highlighter,
                    'color_system': typer_rich_utils.COLOR_SYSTEM,
                    'force_terminal': typer_rich_utils.FORCE_TERMINAL,
                    'width': self.width or typer_rich_utils.MAX_WIDTH,
                    'stderr': stderr,
                    # overrides any defaults above
                    **resolve_options(self.console_kwargs, 'console-kwargs'),
                    'record': True,
                }
            )
            return self.console

        # todo
        # typer provides no official way to alter the console that prints out the help
        # command so we have to monkey patch it - revisit in future if this changes!
        # we also monkey patch get_help incase its a click command
        orig_getter = typer_rich_utils._get_rich_console
        orig_format_help = command.format_help
        command.rich_markup_mode = getattr(
            self, 'markup_mode', getattr(command, 'rich_markup_mode', None)
        )
        command.format_help = TyperGroup.format_help.__get__(
            command, command.__class__
        )
        typer_rich_utils._get_rich_console = get_console
        with contextlib.redirect_stdout(io.StringIO()):
            command.get_help(ctx)
        typer_rich_utils._get_rich_console = orig_getter
        command.format_help = orig_format_help
        ##############################################################################

        export_options = resolve_options(
            getattr(self, f'{self.target}_kwargs', {}), f'{self.target}-kwargs'
        )

        rendered = getattr(self, f'get_{self.target}')(
            **(
                {'title': source_name}
                if self.target is RenderTarget.SVG
                else {}
            ),
            **export_options,
        )

        if self.typer_convert_png:
            png_path = Path(self.env.app.builder.outdir) / (
                f'{normal_cmd.replace(":", "_")}_{self.uuid(normal_cmd)}.png'
            )
            self.env.app.config.typer_convert_png(self, rendered, png_path)
            section += nodes.image(
                uri=os.path.relpath(png_path, Path(self.env.srcdir)),
                alt=source_name,
            )
        elif self.target == RenderTarget.HTML:
            section += nodes.raw(
                '',
                self.env.app.config.typer_render_html(
                    self, normal_cmd, rendered
                ),
                format='html',
            )
        elif self.target == RenderTarget.SVG:
            if 'html' in self.builder:
                section += nodes.raw('', rendered, format='html')
            else:
                img_name = (
                    f'{normal_cmd.replace(":", "_")}_{self.uuid(normal_cmd)}'
                )
                out_dir = Path(self.env.app.builder.outdir)
                (out_dir / f'{img_name}.svg').write_text(rendered)
                pdf_img = out_dir / f'{img_name}.pdf'
                self.env.app.config.typer_svg2pdf(self, rendered, pdf_img)
                section += nodes.image(
                    uri=os.path.relpath(pdf_img, Path(self.env.srcdir)),
                    alt=source_name,
                )

        elif self.target == RenderTarget.TEXT:
            section += nodes.literal_block('', rendered)
        else:
            raise self.severe(f'Invalid typer render target: {self.target}')

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

        self.make_sections = 'make-sections' in self.options
        self.nested = 'show-nested' in self.options
        self.prog_name = self.options.get('prog', None)
        if 'markup-mode' in self.options:
            self.markup_mode = self.options['markup-mode']

        if not self.prog_name:
            try:
                self.prog_name = (
                    command.callback.__module__.split('.')[-1]
                    if hasattr(command, 'callback')
                    and not hasattr(self, 'parent')
                    else re.split(r'::|[.:]', self.arguments[0])[-1]
                )
            except Exception as err:
                raise self.severe(
                    'Unable to determine program name, please specify using '
                    ':prog:'
                ) from err

        self.width = self.options.get('width', 65)
        self.iframe_height = self.options.get('iframe-height', None)

        # if no builders supplied but convert-png is set,
        # force png for all builders, otherwise require the builder
        # to be in the list of typer_convert_png builders
        self.typer_convert_png = 'convert-png' in self.options
        if self.typer_convert_png:
            builders = self.options['convert-png'].strip()
            self.typer_convert_png = (
                self.builder in builders if builders else True
            )

        for trg in ['console', *list(RenderTarget)]:
            setattr(
                self,
                f'{trg}_kwargs',
                self.import_object(self.options.get(f'{trg}-kwargs', None))
                or {},
            )

        self.preferred = self.options.get('preferred', None)
        self.theme = self.options.get('theme', self.theme)

        builder_targets = {}
        for builder_target in self.options.get('builders', '').split(':'):
            if builder_target.strip():
                builder, targets = builder_target.split('=')[0:2]
                builder_targets[builder.strip()] = [
                    RenderTarget(target.strip())
                    for target in targets.split(',')
                ]

        builder_targets = {**self.builder_targets, **builder_targets}

        if self.typer_convert_png:
            self.target = (
                self.preferred
                or (
                    builder_targets.get(self.builder, []) or [RenderTarget.SVG]
                )[0]
            )
        elif self.builder not in builder_targets:
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

        return self.generate_nodes(
            self.prog_name, command, getattr(self, 'parent', None)
        )


def typer_get_iframe_height(
    directive: TyperDirective, normal_cmd: str, html_page: str
) -> int:
    """
    The default iframe height calculation function. The iframe height resolution proceeds as
    follows:

    1) Return the global iframe-height parameter if one was supplied as a parameter on the
       directive.
    2) Check for a cached height value using the file at config.typer_iframe_height_cache_path
       and return one if it exists.
    3) Attempt to use Selenium to dynamically determine the height of the iframe. Padding will
       be added from the config.typer_iframe_height_padding configuration value. The resulting
       height is then cached back to config.typer_iframe_height_cache_path if that path is not
       None. If the attempt to use Selenium fails (it is not installed) a warning is issued and
       a default height of 600 is returned.

    :param directive: The TyperDirective instance
    :param normal_cmd: The normalized name of the command.
        (Subcommands are delimited by :)
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

    with directive.env.app.config.typer_get_web_driver(directive) as driver:
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


def typer_render_html(
    directive: TyperDirective, normal_cmd: str, html_page: str
) -> str:
    """
    The default html rendering function. This function returns the html console
    output wrapped in an iframe. The height of the iframe is dynamically determined
    by calling the configured typer_get_iframe_height function.

    :param directive: The TyperDirective instance
    :param normal_cmd: The normalized name of the command.
        (Subcommands are delimited by :)
    :param html_page: The html page rendered by console.export_html
    """

    height = directive.env.app.config.typer_get_iframe_height(
        directive, normal_cmd, html_page
    )
    return (
        f'<iframe style="border: none;" width="100%" height="'
        f'{height}px"'
        f' srcdoc="{html_escape(html_page)}"></iframe>'
    )


def typer_svg2pdf(directive: TyperDirective, svg_contents: str, pdf_path: str):
    """
    The default typer_svg2pdf function. This function uses the cairosvg package to
    convert svg to pdf.

    .. note::

        You will likely need to install fonts locally on your machine for the output
        of these conversions to look correct. The default font used by the svg
        export from rich is `FiraCode <https://github.com/tonsky/FiraCode/wiki/Installing>`_.

    :param directive: The TyperDirective instance
    :param svg_contents: The svg contents to convert to pdf
    :param pdf_path: The path to write the pdf to
    """
    try:
        import cairosvg

        cairosvg.svg2pdf(bytestring=svg_contents, write_to=str(pdf_path))
    except ImportError:
        directive.severe(f'cairosvg must be installed to render SVG in pdfs')


@contextmanager
def typer_get_web_driver(directive: TyperDirective) -> t.Any:
    """
    The default get_web_driver function. This function yields a selenium web driver
    instance. It requires selenium to be installed.

    To override this function with a custom function see the ``typer_get_web_driver``
    configuration parameter.

    .. note::

        This must be implemented as a context manager that yields the webdriver
        instance and cleans it up on exit!

    :param directive: The TyperDirective instance
    """
    import platform

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
    except ImportError:
        raise directive.severe(
            f'This feature requires selenium and webdriver-manager to be '
            'installed.'
        )

    # Set up headless browser options
    def opts(options=ChromeOptions()):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        return options

    def chrome():
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts()
        )

    def chromium():
        from selenium.webdriver.chrome.service import Service as ChromiumService
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType

        return webdriver.Chrome(
            service=ChromiumService(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=opts(),
        )

    def firefox():
        from selenium.webdriver.firefox.options import Options
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager

        return webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=opts(Options()),
        )

    def edge():
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager

        options = Options()
        options.use_chromium = True
        return webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=opts(options),
        )

    services = [
        chrome,
        edge if platform.system().lower() == 'windows' else chromium,
        firefox,
    ]

    driver = None
    for service in services:
        try:
            driver = service()
            break  # use the first one that works!
        except Exception as err:
            directive.debug(
                f'Unable to initialize webdriver {service.__name__}: {err}'
            )

    if driver:
        yield driver
        driver.quit()
    else:
        raise directive.severe(f'Unable to initialize any webdriver.')


def typer_convert_png(
    directive: TyperDirective, rendered: str, png_path: t.Union[str, Path]
):
    """
    The default typer_convert_png function. This function writes a png file to the given
    path by taking a selenium screen shot. It requires selenium to be installed.
    To override this function with a custom function see the ``typer_convert_png``
    configuration parameter.

    :param directive: The TyperDirective instance
    :param rendered: The rendered command help. May be html, svg, or text.
    :param png_path: The path to write the png to
    """
    import tempfile
    from io import BytesIO

    from PIL import Image
    from selenium.webdriver.common.by import By

    tag = 'code'
    with directive.env.app.config.typer_get_web_driver(directive) as driver:
        with tempfile.NamedTemporaryFile(suffix='.html') as tmp:
            if directive.target is RenderTarget.TEXT:
                tag = 'pre'
                rendered = f'<html><body><pre>{rendered}</pre></body></html>'
            elif directive.target is RenderTarget.SVG:
                tag = 'svg'
                rendered = f'<html><body>{rendered}</body></html>'

            tmp.write(rendered.encode('utf-8'))
            tmp.flush()
            driver.get(f"file://{tmp.name}")
            png = driver.get_screenshot_as_png()
            # Find the element you want a screenshot of
            element = driver.find_element(By.CSS_SELECTOR, tag)
            pixel_ratio = driver.execute_script(
                "return window.devicePixelRatio"
            )
            # Get the element's location and size
            location = element.location
            size = element.size

            # Open the screenshot and crop it to the element
            im = Image.open(BytesIO(png))
            left = location['x'] * pixel_ratio
            top = location['y'] * pixel_ratio
            if directive.target is RenderTarget.TEXT:
                # getting the width of the text is actually a bit tricky
                script = """
                    const pre = arguments[0];
                    const textContent = pre.textContent || pre.innerText;
                    const temporarySpan = document.createElement('span');
                    document.body.appendChild(temporarySpan);

                    // Copy styles to match formatting
                    const preStyle = window.getComputedStyle(pre);
                    temporarySpan.style.fontFamily = preStyle.fontFamily;
                    temporarySpan.style.fontSize = preStyle.fontSize;
                    temporarySpan.style.whiteSpace = 'pre';
                    temporarySpan.textContent = textContent;

                    return temporarySpan.offsetWidth;
                """
                width = driver.execute_script(script, element)
                right = left + width * pixel_ratio
            else:
                right = left + size['width'] * pixel_ratio
            bottom = top + size['height'] * pixel_ratio
            im = im.crop((left, top, right, bottom))  # Defines crop points
            im.save(str(png_path))  # Saves the screenshot


def setup(app: application.Sphinx) -> t.Dict[str, t.Any]:
    # Need autodoc to support mocking modules
    app.add_directive('typer', TyperDirective)

    app.add_config_value(
        'typer_render_html', lambda _: typer_render_html, 'env'
    )
    app.add_config_value(
        'typer_get_iframe_height', lambda _: typer_get_iframe_height, 'env'
    )
    app.add_config_value('typer_svg2pdf', lambda _: typer_svg2pdf, 'env')
    app.add_config_value('typer_iframe_height_padding', 30, 'env')
    app.add_config_value(
        'typer_iframe_height_cache_path',
        Path(app.confdir) / 'typer_cache.json',
        'env',
    )

    app.add_config_value(
        'typer_convert_png', lambda _: typer_convert_png, 'env'
    )
    app.add_config_value(
        'typer_get_web_driver', lambda _: typer_get_web_driver, 'env'
    )

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
