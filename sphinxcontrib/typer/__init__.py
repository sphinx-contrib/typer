import inspect
import functools
from importlib import import_module
import re
import traceback
import typing as t
import click
import typer
import io
import contextlib
from html import escape as html_escape
from types import ModuleType
from typer.main import TyperCommand, TyperGroup
from typer.models import Context as TyperContext
from enum import StrEnum
from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils import statemachine
from sphinx import application
from sphinx.util import logging
from sphinx.util import nodes as sphinx_nodes
from rich.console import Console
from rich.theme import Theme

__version__ = '0.0.1'


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


class RenderTarget(StrEnum):

    HTML = 'html'
    SVG = 'svg'
    TEXT = 'text'

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
        'TyperDirective',        # directive - the TyperDirective instance
        str,                     # name - the name of the command
        Command,                 # command - the command instance
        TyperContext,            # ctx - the TyperContext instance
        t.Optional[TyperContext] # parent - the parent TyperContext instance
    ],
    t.Dict[str, t.Any]
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
        'builders': directives.unchanged
    }

    # resolved options
    prog_name: str
    nested: bool
    make_sections: bool
    width: int

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
            builder: [
                RenderTarget.HTML,
                RenderTarget.SVG,
                RenderTarget.TEXT
            ] for builder in [
                'html', 'dirhtml', 'singlehtml',
                'htmlhelp', 'qthelp', 'devhelp'
            ]
        },
        'epub': [RenderTarget.SVG, RenderTarget.HTML, RenderTarget.TEXT],
        **{
            builder: [RenderTarget.SVG, RenderTarget.TEXT]
            for builder in ['latex', 'texinfo']
        },
        **{
            builder: [RenderTarget.TEXT]
            for builder in ['text', 'gettext']
        },
    }

    @property
    def builder(self) -> str:
        return self.env.app.builder.name

    def import_object(
            self,
            obj_path: t.Optional[str],
            accessor: t.Callable[
                [t.Any, str], t.Any
            ] = lambda obj, attr: getattr(obj, attr)
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
                    obj = import_module('.'.join(parts[0:-(tries-1)]))
                    for attr in parts[-(tries-1):]:
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

    def load_root_command(self, typer_path: str) -> t.Union[TyperCommand, TyperGroup]:
        """
        Load the module.

        :param typer_path: The python path to the Typer app instance.
        """
        def resolve_root_command(obj):
            if isinstance(obj, (TyperCommand, TyperGroup)):
                return obj
            
            if isinstance(obj, typer.Typer):
                return typer.main.get_command(obj)
            
            if callable(obj):
                ret = obj()
                if isinstance(ret, typer.Typer):
                    return typer.main.get_command(obj)
                if isinstance(ret, (TyperCommand, TyperGroup)):
                    return ret
                
            raise self.error(
                f'"{typer_path}" of type {type(obj)} is not Typer, TyperCommand or '
                'TyperGroup.'
            )

        def access_command(
            obj,
            attr
        ) -> t.Union[TyperCommand, TyperGroup]:
            try:
                return resolve_root_command(getattr(obj, attr))
            except Exception:
                cmds = _filter_commands(
                    TyperContext(
                        resolve_root_command(obj)
                    ),
                    [attr]
                )
                if cmds:
                    return cmds[0]
                raise

        return resolve_root_command(
            self.import_object(typer_path, accessor=access_command)
        )

    def generate_nodes(
        self,
        name: str,
        command: TyperCommand,
        parent: t.Optional[TyperContext]
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
            max_content_width=self.width
        )

        if command.hidden:
            return []

        source_name = ctx.command_path

        section = nodes.section(
            '',
            nodes.title(text=name),
            ids=[nodes.make_id(source_name)],
            names=[nodes.fully_normalize_name(source_name)],
        ) if self.make_sections else nodes.container()

        # Summary
        def resolve_options(
                options: RenderOptions,
                parameter: str
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
                        "option": typer.rich_utils.STYLE_OPTION,
                        "switch": typer.rich_utils.STYLE_SWITCH,
                        "negative_option": typer.rich_utils.STYLE_NEGATIVE_OPTION,
                        "negative_switch": typer.rich_utils.STYLE_NEGATIVE_SWITCH,
                        "metavar": typer.rich_utils.STYLE_METAVAR,
                        "metavar_sep": typer.rich_utils.STYLE_METAVAR_SEPARATOR,
                        "usage": typer.rich_utils.STYLE_USAGE,
                    },
                ),
                highlighter=typer.rich_utils.highlighter,
                color_system=typer.rich_utils.COLOR_SYSTEM,
                force_terminal=typer.rich_utils.FORCE_TERMINAL,
                width=self.width or typer.rich_utils.MAX_WIDTH,
                stderr=stderr,
                # overrides any defaults above
                **resolve_options(self.console_kwargs, 'console_kwargs'),
                record=True
            )
            return self.console
               
        # todo
        # typer provides no official way to alter the console that prints out the help
        # command so we have to monkey patch it - revisit in future if this changes!
        orig_getter = typer.rich_utils._get_rich_console
        typer.rich_utils._get_rich_console = get_console
        with contextlib.redirect_stdout(io.StringIO()):
            command.get_help(ctx)
        typer.rich_utils._get_rich_console = orig_getter
        ##############################################################################

        if self.target == RenderTarget.HTML:
            html_page = self.console.export_html(
                **resolve_options(self.html_kwargs, 'html_kwargs'),
                clear=False
            )
            section += nodes.raw(
                '',
                f'<iframe style="border: none; overflow: auto;" width="100%" height="{16*(html_page.count('\n')+1)}px" srcdoc="{html_escape(html_page)}"></iframe>',
                format='html'
            )
        elif self.target == RenderTarget.SVG:
            svg = self.console.export_svg(
                title=source_name,
                **resolve_options(self.svg_kwargs, 'svg_kwargs'),
                clear=False
            )
            section += (
                nodes.raw('', svg, format='html')
                if 'html' in self.builder else
                nodes.image('', svg)
            )
        elif self.target == RenderTarget.TEXT:
            section += nodes.literal_block(
                '',
                self.console.export_text(
                    **resolve_options(self.svg_kwargs, 'svg_kwargs'),
                    clear=False
                )
            )
        else:
            raise self.error(
                f'Invalid typer render target: {self.target}'
            )

        # recurse through subcommands if we should
        if self.nested and isinstance(command, click.MultiCommand):
            commands = _filter_commands(ctx, command.list_commands(ctx))
            for command in commands:
                section.extend(
                    self.generate_nodes(
                        command.name,
                        command,
                        parent=ctx
                    )
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
        self.console_kwargs = self.import_object(
            self.options.get('console_kwargs', None)
        ) or {}
        self.html_kwargs = self.import_object(
            self.options.get('html_kwargs', None)
        ) or {}
        self.svg_kwargs = self.import_object(
            self.options.get('svg_kwargs', None)
        ) or {}
        self.txt_kwargs = self.import_object(
            self.options.get('txt_kwargs', None)
        ) or {}
        self.preferred = self.options.get('preferred', None)

        builder_targets = {}
        for builder_target in self.options.get('builders', '').split(':'):
            if builder_target.strip():
                builder, targets = builder_target.split('=')[0:2]
                builder_targets[builder.strip()] = [
                    RenderTarget(target.strip())
                    for target in targets.split(',')
                ]

        builder_targets = {
            **builder_targets,
            **self.builder_targets
        }

        if self.builder not in builder_targets:
            self.target = self.preferred or RenderTarget.TEXT
            self.logger.debug(
                'Unable to resolve render target for builder: %s - using: %s',
                self.builder,
                self.target
            )
        else:
            supported = builder_targets[self.builder]
            self.target = (
                self.preferred
                if self.preferred in supported
                else supported[0]
            )
        return self.generate_nodes(self.prog_name, command, None)


def visit_fixed_text_element_html(self, node):
    # Get the text of the node
    text = node.astext()

    # Wrap the text in <pre> tags and create a new raw node
    raw_node = nodes.raw('', f'<pre>{text}</pre>', format='html')

    # Replace the FixedTextElement node with the raw node
    node.replace_self(raw_node)


def setup(app: application.Sphinx) -> t.Dict[str, t.Any]:
    # Need autodoc to support mocking modules
    app.add_directive('typer', TyperDirective)
    
    # todo - why doesn't this already work like this?
    app.add_node(nodes.FixedTextElement, html=(visit_fixed_text_element_html, None))

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
