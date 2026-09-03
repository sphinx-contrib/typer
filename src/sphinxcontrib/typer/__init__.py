r"""
::


    ███████╗██████╗ ██╗  ██╗██╗███╗   ██╗██╗  ██╗
    ██╔════╝██╔══██╗██║  ██║██║████╗  ██║╚██╗██╔╝
    ███████╗██████╔╝███████║██║██╔██╗ ██║ ╚███╔╝
    ╚════██║██╔═══╝ ██╔══██║██║██║╚██╗██║ ██╔██╗
    ███████║██║     ██║  ██║██║██║ ╚████║██╔╝ ██╗
    ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝

    ████████╗██╗   ██╗██████╗ ███████╗██████╗
    ╚══██╔══╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
       ██║    ╚████╔╝ ██████╔╝█████╗  ██████╔╝
       ██║     ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗
       ██║      ██║   ██║     ███████╗██║  ██║
       ╚═╝      ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝

"""

import contextlib
import hashlib
import inspect
import io
import os
import re
import subprocess
import sys
import traceback
import typing as t
from contextlib import contextmanager
from enum import Enum
from html import escape as html_escape
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from rich import terminal_theme as rich_theme
from rich.console import Console
from rich.theme import Theme
from sphinx import application
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset_file
from sphinx.util.nodes import make_refnode

# As of typer 0.26 click is vendored into typer (typer._click). Typer commands
# are instances of the vendored click classes, not the standalone click package
# (which typer no longer depends on), so we use the vendored click throughout.
from typer import _click as click
from typer import rich_utils as typer_rich_utils
from typer.core import MarkupMode, TyperCommand, TyperGroup
from typer.main import Typer
from typer.main import get_command as get_typer_command
from typer.models import Context as TyperContext
from typer.models import TyperInfo

VERSION = (0, 10, 0)

__title__ = "SphinxContrib Typer"
__version__ = ".".join(str(i) for i in VERSION)
__author__ = "Brian Kohan"
__license__ = "MIT"
__copyright__ = "Copyright 2023-2026 Brian Kohan"


# html themes known to support switching between light and dark modes using a
# data-theme attribute and the only-light / only-dark classes - when html_theme is
# one of these, typer_dark_theme = "auto" resolves to "dark"
DARK_MODE_THEMES = frozenset({"furo", "pydata_sphinx_theme", "sphinx_book_theme"})

BROWSER_DEFAULT_VIEWPORT_WIDTH = 1920
BROWSER_DEFAULT_VIEWPORT_HEIGHT = 2048


def get_function(function: str | t.Callable[..., t.Any]):
    if callable(function):
        return function
    if isinstance(function, str):
        parts = function.split(".")
        return getattr(import_module(".".join(parts[0:-1])), parts[-1])


def _filter_commands(ctx: click.Context, cmd_filter: list[str]):
    return [ctx.command.get_command(ctx, cmd_name) for cmd_name in cmd_filter]


def _get_app(env):
    """
    Fetch the Sphinx application from the build environment.

    ``BuildEnvironment.app`` was deprecated in Sphinx 9 (removal in 11) and
    Sphinx itself now reaches the application through the private ``_app``
    attribute. Prefer that, falling back to the public attribute on older
    versions.
    """
    return getattr(env, "_app", None) or env.app


def _add_dependency(env, command):
    cb = getattr(command, "callback", None)
    cb = getattr(cb, "__wrapped__", cb)
    if cb:
        env.note_dependency(inspect.getfile(cb))


def _command_path(ctx: click.Context | None):
    parts = []
    while ctx:
        if ctx.info_name:
            parts.append(ctx.info_name)
        ctx = ctx.parent
    return ":".join(reversed(parts))


class RenderTarget(str, Enum):
    HTML = "html"
    SVG = "svg"
    TEXT = "text"

    def __str__(self) -> str:
        return self.value


class RenderTheme(str, Enum):
    LIGHT = "light"
    MONOKAI = "monokai"
    DIMMED_MONOKAI = "dimmed_monokai"
    NIGHT_OWLISH = "night_owlish"
    DARK = "dark"
    RED_SANDS = "red_sands"
    BLUE_WAVES = "blue_waves"

    def __str__(self) -> str:
        return self.value

    @property
    def terminal_theme(self) -> rich_theme.TerminalTheme:
        return {
            RenderTheme.LIGHT: rich_theme.DEFAULT_TERMINAL_THEME,
            RenderTheme.MONOKAI: rich_theme.MONOKAI,
            RenderTheme.DIMMED_MONOKAI: rich_theme.DIMMED_MONOKAI,
            RenderTheme.NIGHT_OWLISH: rich_theme.NIGHT_OWLISH,
            RenderTheme.DARK: rich_theme.SVG_EXPORT_THEME,
            RenderTheme.RED_SANDS: rich_theme.TerminalTheme(
                (132, 42, 38),  # background
                (210, 193, 159),  # text
                [
                    (210, 193, 159),
                    (0, 0, 0),  # required
                    (77, 218, 77),  # option on short name
                    (227, 189, 57),  # Usage/metavar
                    (210, 193, 159),
                    (0, 18, 140),  # option off
                    (75, 214, 225),  # option on/command names
                    (210, 193, 159),
                ],
            ),
            RenderTheme.BLUE_WAVES: rich_theme.TerminalTheme(
                (20, 118, 247),  # background
                (250, 240, 250),  # text
                [
                    (250, 240, 250),
                    (0, 0, 0),  # required
                    (0, 255, 0),  # option on short name
                    (227, 189, 57),  # Usage/metavar
                    (250, 240, 250),
                    (2, 2, 214),  # option off
                    (146, 226, 252),  # option on/command names
                    (250, 240, 250),
                ],
            ),
        }[self]


Command = TyperCommand | TyperGroup

"""
Callbacks that return a dict of kwargs to pass to various renderer functions
must all have the RenderCallback function signature:
"""
RenderCallback = t.Callable[
    [
        "TyperDirective",  # directive - the TyperDirective instance
        str,  # name - the name of the command
        Command,  # command - the command instance
        click.Context,  # ctx - the click.Context instance
        click.Context | None,  # parent - the parent click.Context instance
    ],
    dict[str, t.Any],
]

"""
Custom render options can be provided at a python path that resolves to the
following type. Either a dictionary of kwargs to pass to the relevant function
or a callable that returns a dictionary of kwargs to pass to the relevant function
"""
RenderOptions = dict[str, t.Any] | RenderCallback


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

    logger = logging.getLogger("sphinxcontrib.typer")

    has_content = False
    required_arguments = 1
    option_spec: t.ClassVar[dict[str, t.Any]] = {
        "prog": directives.unchanged_required,
        "make-sections": directives.flag,
        "show-nested": directives.flag,
        "markup-mode": directives.unchanged,
        "width": directives.nonnegative_int,
        "theme": RenderTheme,
        "dark-theme": RenderTheme,
        "svg-kwargs": directives.unchanged,
        "text-kwargs": directives.unchanged,
        "html-kwargs": directives.unchanged,
        "console-kwargs": directives.unchanged,
        "preferred": RenderTarget,
        "builders": directives.unchanged,
        "iframe-height": directives.nonnegative_int,
        "convert-png": directives.unchanged,
    }

    # resolved options
    prog_name: str
    nested: bool
    make_sections: bool
    width: int
    iframe_height: int | None = None
    typer_convert_png: bool = False

    console: Console
    parent: click.Context

    theme: RenderTheme = RenderTheme.LIGHT
    dark_theme: RenderTheme | None = None
    preferred: RenderTarget | None = None

    markup_mode: MarkupMode

    # the console_kwargs option can be a dict or a callable that returns a dict, the callable
    # must conform to the RenderOptions signature
    console_kwargs: RenderOptions
    html_kwargs: RenderOptions
    svg_kwargs: RenderOptions
    text_kwargs: RenderOptions

    target: RenderTarget

    builder_targets: t.ClassVar[dict[str, list[RenderTarget]]] = {
        **{
            builder: [RenderTarget.SVG, RenderTarget.HTML, RenderTarget.TEXT]
            for builder in [
                "html",
                "dirhtml",
                "singlehtml",
                "htmlhelp",
                "qthelp",
                "devhelp",
            ]
        },
        "epub": [RenderTarget.HTML, RenderTarget.SVG, RenderTarget.TEXT],
        **{
            builder: [RenderTarget.SVG, RenderTarget.TEXT]
            for builder in ["latex", "latexpdf", "texinfo"]
        },
        **{builder: [RenderTarget.TEXT] for builder in ["text", "gettext"]},
    }

    @property
    def builder(self) -> str:
        return _get_app(self.env).builder.name

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
        source = os.path.relpath(source, self.env.srcdir)
        return hashlib.sha256(
            f"{source}.{line_number}[{normal_cmd}]".encode()
        ).hexdigest()[:8]

    def import_object(
        self,
        obj_path: str | None,
        accessor: t.Callable[[t.Any, str, t.Any], t.Any] = lambda obj, attr, _: getattr(
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
        parts = re.split(r"::|[.:]", obj_path)
        tries = 1
        try:
            while True:
                # walk up the import path until we find something importable
                # then walk down the path fetching all the attributes
                # this allows import strings to reach into nested class
                # attributes
                try:
                    tries += 1
                    try_path = ".".join(parts[0 : -(tries - 1)])
                    obj = import_module(try_path)
                    file_spec = getattr(find_spec(try_path), "origin", None)
                    if file_spec:
                        self.env.note_dependency(file_spec)
                    for attr in parts[-(tries - 1) :]:
                        obj = accessor(obj, attr, try_path)
                    break
                except (ImportError, ModuleNotFoundError):
                    if tries >= len(parts):
                        raise

        except (Exception, SystemExit) as exc:  # noqa: BLE001
            err_msg = f'Failed to import "{obj_path}"'
            if isinstance(exc, SystemExit):
                err_msg += "The module appeared to call sys.exit()."
            else:
                err_msg += (
                    f"The following exception was raised:\n{traceback.format_exc()}"
                )

            raise self.severe(err_msg)

        return obj

    def load_root_command(self, typer_path: str) -> Command:
        """
        Load the module.

        :param typer_path: The python path to the Typer app instance.
        """

        def resolve_root_command(obj):
            if isinstance(obj, (TyperCommand, TyperGroup)):
                return obj

            # use lenient duck typing check incase obj is a proxy for a Typer instance
            if isinstance(obj, Typer) or isinstance(
                getattr(obj, "info", None), TyperInfo
            ):
                return get_typer_command(obj)

            if callable(obj):
                ret = obj()
                if isinstance(ret, Typer) or isinstance(
                    getattr(ret, "info", None), TyperInfo
                ):
                    return get_typer_command(ret)
                if isinstance(ret, (TyperCommand, TyperGroup)):
                    return ret

            raise self.error(
                f'"{typer_path}" of type {type(obj)} is not a Typer app or command.'
            )

        def access_command(obj, attr, imprt_path) -> Command:
            attr_obj = None
            try:
                attr_obj = getattr(obj, attr)
                return resolve_root_command(attr_obj)
            except Exception:
                try:
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
                                getattr(obj, "name", "")
                                if getattr(self, "parent", None)
                                else ""
                            )
                            or imprt_path.split(".")[-1]
                        ),
                        parent=getattr(self, "parent", None),
                    )
                    cmds = _filter_commands(self.parent, [attr])
                    if cmds:
                        return cmds[0]
                except (IndexError, rst.DirectiveError):
                    if attr_obj:
                        return attr_obj
                raise

        return resolve_root_command(
            self.import_object(typer_path, accessor=access_command)
        )

    def get_html(self, **options):
        return self.console.export_html(
            **{"theme": self.theme.terminal_theme, **options, "clear": False}
        )

    def get_svg(self, **options):
        return self.console.export_svg(
            **{"theme": self.theme.terminal_theme, **options, "clear": False}
        )

    def get_text(self, **options):
        return self.console.export_text(**{**options, "clear": False})

    def themed_nodes(
        self,
        rendered: str,
        export_options: dict[str, t.Any],
        wrap: t.Callable[[str], nodes.Node],
    ) -> list[nodes.Node]:
        """
        Wrap the rendered output for an html builder. When a dark theme is configured
        the help is exported a second time with the dark theme and both renderings are
        emitted inside containers that the theme (or our stylesheet) shows or hides
        based on the active light/dark mode.

        https://github.com/sphinx-contrib/typer/issues/62

        :param rendered: The output rendered with the primary theme
        :param export_options: The options the primary rendering was exported with
        :param wrap: A callable producing the docutils node for a rendering
        """
        if not self.dark_theme or "html" not in self.builder:
            return [wrap(rendered)]
        dark_options = {**export_options, "theme": self.dark_theme.terminal_theme}
        if self.target is RenderTarget.SVG:
            dark_options["unique_id"] = f"{export_options['unique_id']}-dark"
        dark = getattr(self, f"get_{self.target}")(**dark_options)
        return [
            nodes.container(
                "", wrap(rendered), classes=["only-light", "typer-only-light"]
            ),
            nodes.container("", wrap(dark), classes=["only-dark", "typer-only-dark"]),
        ]

    def generate_nodes(
        self,
        name: str,
        command: click.Command,
        parent: click.Context | None,
    ) -> list[nodes.section]:
        """
        Generate the relevant Sphinx nodes.

        Generate node help for a Typer command or group.

        :param command: Instance of a Typer command or group
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

        _add_dependency(self.env, command)

        if command.hidden:
            return []

        normal_cmd = section_title = _command_path(ctx).replace(":", " ")
        section_id = nodes.make_id(section_title)
        if not getattr(self, "parent", None):
            section_title = section_title.split(" ")[-1]

        section = (
            nodes.section(
                "",
                nodes.title(text=section_title),
                ids=[section_id],
                names=[nodes.fully_normalize_name(section_title)],
            )
            if self.make_sections
            else nodes.container(ids=[section_id])
        )
        t.cast(TyperDomain, self.env.get_domain(TyperDomain.name)).note_command(
            section_id, normal_cmd
        )

        # Summary
        def resolve_options(options: RenderOptions, parameter: str) -> dict[str, t.Any]:
            if callable(options):
                options = options(self, name, command, ctx, parent)
            if isinstance(options, dict):
                return options
            raise self.severe(
                f"Invalid {parameter}, must be a dict or callable, got {type(options)}"
            )

        def get_console(stderr: bool = False) -> Console:
            self.console = Console(
                **{
                    "theme": Theme(
                        {
                            "option": typer_rich_utils.STYLE_OPTION,
                            "switch": typer_rich_utils.STYLE_SWITCH,
                            "negative_option": typer_rich_utils.STYLE_NEGATIVE_OPTION,
                            "negative_switch": typer_rich_utils.STYLE_NEGATIVE_SWITCH,
                            "types": typer_rich_utils.STYLE_TYPES,
                            "types_sep": typer_rich_utils.STYLE_TYPES_SEPARATOR,
                            "usage": typer_rich_utils.STYLE_USAGE,
                        },
                    ),
                    "highlighter": typer_rich_utils.highlighter,
                    "color_system": None
                    if self.target is RenderTarget.TEXT
                    else typer_rich_utils.COLOR_SYSTEM,
                    "force_terminal": typer_rich_utils.FORCE_TERMINAL,
                    "width": self.width or typer_rich_utils.MAX_WIDTH,
                    "stderr": stderr,
                    # overrides any defaults above
                    **resolve_options(self.console_kwargs, "console-kwargs"),
                    "record": True,
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
            self, "markup_mode", getattr(command, "rich_markup_mode", "markdown")
        )
        command.format_help = TyperGroup.format_help.__get__(command, command.__class__)
        typer_rich_utils._get_rich_console = get_console
        with contextlib.redirect_stdout(io.StringIO()):
            command.get_help(ctx)
        typer_rich_utils._get_rich_console = orig_getter
        command.format_help = orig_format_help
        ##############################################################################

        export_options = resolve_options(
            getattr(self, f"{self.target}_kwargs", {}), f"{self.target}-kwargs"
        )

        if self.target is RenderTarget.SVG:
            export_options = {
                "title": section_title,
                # rich derives the svg css class prefix from a hash of the content,
                # so two renderings of the same command that differ only by theme
                # would share class names and restyle each other when embedded in
                # the same page - use a prefix unique to this directive instance.
                # https://github.com/sphinx-contrib/typer/issues/32
                "unique_id": f"typer-{self.uuid(normal_cmd)}",
                **export_options,
            }

        rendered = getattr(self, f"get_{self.target}")(**export_options)

        def to_path(name: str, ext: str) -> Path:
            return (
                Path(_get_app(self.env).builder.outdir)
                / f"{name.replace(':', '_').replace(' ', '_')}_{self.uuid(name)}.{ext}"
            )

        # Image URIs must be relative to the document's directory, not srcdir,
        # so that Sphinx can locate the file when the directive appears in a
        # document nested inside a subdirectory (e.g. via autodoc).
        # See https://github.com/sphinx-contrib/typer/issues/58
        doc_dir = Path(self.env.srcdir) / Path(self.env.docname).parent

        if self.typer_convert_png:
            png_path = to_path(normal_cmd, "png")
            get_function(self.env.config.typer_convert_png)(self, rendered, png_path)
            section += nodes.image(
                uri=os.path.relpath(png_path, doc_dir),
                alt=section_title,
            )
        elif self.target == RenderTarget.HTML:
            section.extend(
                self.themed_nodes(
                    rendered,
                    export_options,
                    lambda html_page: nodes.raw(
                        "",
                        get_function(self.env.config.typer_render_html)(
                            self, normal_cmd, html_page
                        ),
                        format="html",
                    ),
                )
            )
        elif self.target == RenderTarget.SVG:
            if "html" in self.builder:
                section.extend(
                    self.themed_nodes(
                        rendered,
                        export_options,
                        lambda svg: nodes.raw("", svg, format="html"),
                    )
                )
            else:
                svg_path = to_path(normal_cmd, "svg")
                pdf_path = to_path(normal_cmd, "pdf")
                svg_path.write_text(rendered)
                get_function(self.env.config.typer_svg2pdf)(self, rendered, pdf_path)
                section += nodes.image(
                    uri=os.path.relpath(pdf_path, doc_dir),
                    alt=section_title,
                )

        elif self.target == RenderTarget.TEXT:
            section += nodes.literal_block("", rendered)
        else:
            raise self.severe(f"Invalid typer render target: {self.target}")

        # recurse through subcommands if we should
        if isinstance(command, TyperGroup):
            commands = _filter_commands(ctx, command.list_commands(ctx))
            for cmd in commands:
                if self.nested:
                    section.extend(self.generate_nodes(cmd.name, cmd, parent=ctx))
                else:
                    _add_dependency(self.env, cmd)
        return [section]

    def run(self) -> t.Iterable[nodes.section]:
        self.env = self.state.document.settings.env

        command = self.load_root_command(self.arguments[0])

        self.make_sections = "make-sections" in self.options
        self.nested = "show-nested" in self.options
        self.prog_name = self.options.get("prog", "")
        if "markup-mode" in self.options:
            self.markup_mode = self.options["markup-mode"]

        if not self.prog_name:
            try:
                self.prog_name = (
                    command.callback.__module__.split(".")[-1]
                    if hasattr(command, "callback") and not hasattr(self, "parent")
                    else re.split(r"::|[.:]", self.arguments[0])[-1]
                )
            except Exception as err:
                raise self.severe(
                    "Unable to determine program name, please specify using :prog:"
                ) from err

        self.prog_name = self.prog_name.strip()

        self.width = self.options.get("width", 65)
        self.iframe_height = self.options.get("iframe-height", None)

        # if no builders supplied but convert-png is set,
        # force png for all builders, otherwise require the builder
        # to be in the list of typer_convert_png builders
        self.typer_convert_png = "convert-png" in self.options
        if self.typer_convert_png:
            builders = self.options["convert-png"].strip()
            self.typer_convert_png = self.builder in builders if builders else True

        for trg in ["console", *list(RenderTarget)]:
            setattr(
                self,
                f"{trg}_kwargs",
                self.import_object(self.options.get(f"{trg}-kwargs", None)) or {},
            )

        self.preferred = self.options.get("preferred", None)
        self.theme = self.options.get("theme", self.theme)
        dark_theme = self.options.get("dark-theme", self.env.config.typer_dark_theme)
        if dark_theme == "auto":
            dark_theme = (
                RenderTheme.DARK
                if self.env.config.html_theme in DARK_MODE_THEMES
                else None
            )
        self.dark_theme = RenderTheme(dark_theme) if dark_theme else None

        builder_targets = {}
        for builder_target in self.options.get("builders", "").split(":"):
            if builder_target.strip():
                builder, targets = builder_target.split("=")[0:2]
                builder_targets[builder.strip()] = [
                    RenderTarget(target.strip()) for target in targets.split(",")
                ]

        builder_targets = {**self.builder_targets, **builder_targets}

        if self.typer_convert_png:
            self.target = (
                self.preferred
                or (builder_targets.get(self.builder, []) or [RenderTarget.SVG])[0]
            )
        elif self.builder not in builder_targets:
            self.target = self.preferred or RenderTarget.TEXT
            self.logger.debug(
                "Unable to resolve render target for builder: %s - using: %s",
                self.builder,
                self.target,
            )
        else:
            supported = builder_targets[self.builder]
            self.target = (
                self.preferred if self.preferred in supported else supported[0]
            )

        parent = getattr(self, "parent", None)
        if parent and self.options.get("prog", None):
            # :prog: is the full invocation, so blank out the names of all
            # ancestor contexts - otherwise the (unreliable) inferred name of
            # the root app leaks into the usage line for nested commands
            # https://github.com/sphinx-contrib/typer/issues/24
            # https://github.com/sphinx-contrib/typer/issues/23
            ancestor: click.Context | None = parent
            while ancestor:
                ancestor.info_name = ""
                ancestor = ancestor.parent
        return self.generate_nodes(self.prog_name, command, parent)


def typer_get_iframe_height(
    directive: TyperDirective, normal_cmd: str, html_page: str
) -> int:
    """
    The default iframe height calculation function. The iframe height resolution proceeds as
    follows:

    1) Return the global iframe-height parameter if one was supplied as a parameter on the
       directive.
    2) Check for a cached height value.
    3) Render the page in a headless browser (see :func:`typer_get_page`) to dynamically
       determine the height of the iframe. Padding will be added from the
       config.typer_iframe_height_padding configuration value. The resulting height is then
       cached.

    :param directive: The TyperDirective instance
    :param normal_cmd: The normalized name of the command.
        (Subcommands are delimited by :)
    :param html_page: The full html document that will be rendered in the iframe
    """
    if directive.iframe_height is not None:
        return directive.iframe_height

    if not hasattr(directive.env, "iframe_heights"):
        directive.env.iframe_heights = {}

    if height := directive.env.iframe_heights.get(normal_cmd, None):
        return height

    with get_function(directive.env.config.typer_get_page)(directive) as page:
        page.set_content(html_page)
        height = (
            int(
                page.evaluate("document.documentElement.getBoundingClientRect().height")
            )
            + directive.env.config.typer_iframe_height_padding
        )
    directive.env.iframe_heights[normal_cmd] = height
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

    height = get_function(directive.env.config.typer_get_iframe_height)(
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
    except ImportError as err:
        raise directive.severe(
            "cairosvg must be installed to render SVG in pdfs. "
            "Install the pdf extra: pip install sphinxcontrib-typer[pdf]"
        ) from err


@contextmanager
def typer_install_browser(directive: TyperDirective) -> None:
    """
    Install the chromium browser used by playwright by running
    ``python -m playwright install chromium`` in a subprocess with the active interpreter.

    This is invoked automatically by :func:`typer_get_page` when the browser is missing
    and the ``typer_playwright_install`` configuration value is enabled.

    :param directive: The TyperDirective instance
    """
    directive.logger.info(
        "sphinxcontrib-typer: installing the playwright chromium browser..."
    )
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"], check=True
    )


@contextmanager
def typer_get_page(
    directive: TyperDirective,
    width: int = BROWSER_DEFAULT_VIEWPORT_WIDTH,
    height: int = BROWSER_DEFAULT_VIEWPORT_HEIGHT,
) -> t.Iterator[t.Any]:
    """
    The default get_page function. This function yields a headless :pypi:`playwright`
    chromium :class:`~playwright.sync_api.Page`. It requires playwright to be installed. If
    the chromium browser has not been installed it will be installed on first use unless
    the ``typer_playwright_install`` configuration value is False.

    To override this function with a custom function see the ``typer_get_page``
    configuration parameter.

    .. note::

        This must be implemented as a context manager that yields the page instance and
        cleans it up on exit!

    :param directive: The TyperDirective instance
    :param width: The width of the browser viewport in pixels
    :param height: The height of the browser viewport in pixels
    """
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError as err:
        raise directive.severe(
            "This feature requires playwright to be installed. "
            "Install the html or png extra: pip install sphinxcontrib-typer[html]"
        ) from err

    def missing_browser(err: Exception) -> bool:
        msg = str(err)
        return "playwright install" in msg or "Executable doesn't exist" in msg

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Error as err:
            if not missing_browser(err):
                raise
            if not directive.env.config.typer_playwright_install:
                raise directive.severe(
                    "The playwright chromium browser is not installed, run: "
                    "playwright install chromium"
                ) from err
            typer_install_browser(directive)
            browser = playwright.chromium.launch()
        try:
            yield browser.new_page(viewport={"width": width, "height": height})
        finally:
            browser.close()


def typer_convert_png(
    directive: TyperDirective,
    rendered: str,
    png_path: str | Path,
    width: int = BROWSER_DEFAULT_VIEWPORT_WIDTH,
    height: int = BROWSER_DEFAULT_VIEWPORT_HEIGHT,
):
    """
    The default typer_convert_png function. This function writes a png file to the given
    path by taking a screenshot of the rendered help in a headless browser (see
    :func:`typer_get_page`). It requires playwright to be installed.

    To override this function with a custom function see the ``typer_convert_png``
    configuration parameter.

    :param directive: The TyperDirective instance
    :param rendered: The rendered command help. May be html, svg, or text.
    :param png_path: The path to write the png to
    :param width: The width of the browser viewport, the screenshot is of the rendered
        element only so this just needs to be larger than the help output.
    :param height: The height of the browser viewport.
    """
    tag = "code"
    if directive.target is RenderTarget.TEXT:
        tag = "pre"
        # inline-block so the element shrinks to the width of the text
        rendered = (
            "<html><body><pre style='display: inline-block; margin: 0;'>"
            f"{rendered}</pre></body></html>"
        )
    elif directive.target is RenderTarget.SVG:
        tag = "svg"
        rendered = f"<html><body>{rendered}</body></html>"

    with get_function(directive.env.config.typer_get_page)(
        directive, width, height
    ) as page:
        page.set_content(rendered)
        page.locator(tag).first.screenshot(path=str(png_path))


class TyperXRefRole(XRefRole):
    """
    The ``:typer:`` cross-reference role. Accepts either the section id form
    (``prog-subcommand``) or the invocation form (``prog subcommand``) and
    normalizes both to the id that :class:`TyperDirective` registers. When
    no explicit link text is given the rendered link shows the full command
    invocation.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # route the short ``:typer:`` form into the typer domain
        self.name = f"{TyperDomain.name}:command"
        return super().run()

    def process_link(
        self,
        env: BuildEnvironment,
        refnode: nodes.Element,
        has_explicit_title: bool,
        title: str,
        target: str,
    ) -> tuple[str, str]:
        return title.strip(), nodes.make_id(target.strip())


class TyperDomain(Domain):
    """
    Sphinx domain holding the cross-reference targets registered by the
    :class:`TyperDirective` so that references survive parallel reads,
    are cleared on incremental rebuilds, and are exported to the
    intersphinx inventory.
    """

    name = "typer"
    label = "Typer"

    object_types: t.ClassVar[dict[str, ObjType]] = {
        "command": ObjType("Typer command", "command")
    }
    roles: t.ClassVar[dict[str, t.Any]] = {"command": TyperXRefRole(warn_dangling=True)}
    initial_data: t.ClassVar[dict[str, dict[str, tuple[str, str, str]]]] = {
        # command id -> (docname, anchor, display name)
        "commands": {}
    }

    @property
    def commands(self) -> dict[str, tuple[str, str, str]]:
        return self.data.setdefault("commands", {})

    def note_command(self, command_id: str, display_name: str) -> None:
        self.commands[command_id] = (self.env.docname, command_id, display_name)

    def clear_doc(self, docname: str) -> None:
        for command_id, (doc, _, _) in list(self.commands.items()):
            if doc == docname:
                del self.commands[command_id]

    def merge_domaindata(self, docnames: set[str], otherdata: dict[str, t.Any]) -> None:
        for command_id, entry in otherdata.get("commands", {}).items():
            if entry[0] in docnames:
                self.commands[command_id] = entry

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: t.Any,
        typ: str,
        target: str,
        node: nodes.Element,
        contnode: nodes.Element,
    ) -> nodes.reference | None:
        entry = self.commands.get(target)
        if not entry:
            return None
        docname, anchor, display_name = entry
        if not node.get("refexplicit"):
            contnode = nodes.literal(
                display_name, display_name, classes=contnode.get("classes", [])
            )
        return make_refnode(
            builder, fromdocname, docname, anchor, contnode, display_name
        )

    def resolve_any_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: t.Any,
        target: str,
        node: nodes.Element,
        contnode: nodes.Element,
    ) -> list[tuple[str, nodes.reference]]:
        refnode = self.resolve_xref(
            env, fromdocname, builder, "command", nodes.make_id(target), node, contnode
        )
        return [(f"{self.name}:command", refnode)] if refnode else []

    def get_objects(self) -> t.Iterator[tuple[str, str, str, str, str, int]]:
        for command_id, (docname, anchor, display_name) in self.commands.items():
            yield command_id, display_name, "command", docname, anchor, 1


STATIC_CSS = Path(__file__).parent / "static" / "sphinxcontrib_typer.css"


def _copy_static_css(app: application.Sphinx, exception: Exception | None) -> None:
    if exception is None and app.builder.format == "html":
        copy_asset_file(str(STATIC_CSS), str(Path(app.outdir) / "_static"))


def setup(app: application.Sphinx) -> dict[str, t.Any]:
    # Need autodoc to support mocking modules
    app.add_directive("typer", TyperDirective)
    app.add_domain(TyperDomain)
    app.add_role("typer", TyperXRefRole(warn_dangling=True))

    app.add_config_value(
        "typer_render_html", "sphinxcontrib.typer.typer_render_html", "env"
    )

    app.add_config_value(
        "typer_get_iframe_height", "sphinxcontrib.typer.typer_get_iframe_height", "env"
    )
    app.add_config_value("typer_svg2pdf", "sphinxcontrib.typer.typer_svg2pdf", "env")
    app.add_config_value("typer_iframe_height_padding", 30, "env")

    app.add_config_value(
        "typer_convert_png", "sphinxcontrib.typer.typer_convert_png", "env"
    )
    app.add_config_value("typer_get_page", "sphinxcontrib.typer.typer_get_page", "env")
    app.add_config_value("typer_playwright_install", True, "env")
    app.add_config_value("typer_dark_theme", "auto", "env")

    app.add_css_file(STATIC_CSS.name)
    app.connect("build-finished", _copy_static_css)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
