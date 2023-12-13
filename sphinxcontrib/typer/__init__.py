import inspect
import functools
import re
import traceback
import typing as ty
import warnings

import typer
from typer.main import TyperCommand, TyperGroup
from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils import statemachine
from sphinx import application
from sphinx.util import logging
from sphinx.util import nodes as sphinx_nodes

LOG = logging.getLogger(__name__)


class TyperDirective(rst.Directive):
    has_content = False
    required_arguments = 1
    option_spec = {
        'prog': directives.unchanged_required,
        'commands': directives.unchanged,
        'show-nested': directives.flag,
    }

    def load_module(self, module_path: str) -> ty.Union[TyperCommand, TyperGroup]:
        """Load the module."""

        try:
            module_name, attr_name = module_path.split(':', 1)
        except ValueError:  # noqa
            raise self.error(
                '"{}" is not of format "module:parser"'.format(module_path)
            )

        try:
            with mock(self.env.config.sphinx_click_mock_imports):
                mod = __import__(module_name, globals(), locals(), [attr_name])
        except (Exception, SystemExit) as exc:  # noqa
            err_msg = 'Failed to import "{}" from "{}". '.format(attr_name, module_name)
            if isinstance(exc, SystemExit):
                err_msg += 'The module appeared to call sys.exit()'
            else:
                err_msg += 'The following exception was raised:\n{}'.format(
                    traceback.format_exc()
                )

            raise self.error(err_msg)

        if not hasattr(mod, attr_name):
            raise self.error(
                'Module "{}" has no attribute "{}"'.format(module_name, attr_name)
            )

        parser = getattr(mod, attr_name)

        if not isinstance(parser, (TyperCommand, TyperGroup)):
            raise self.error(
                '"{}" of type "{}" is not click.Command or click.Group.'
                '"click.BaseCommand"'.format(type(parser), module_path)
            )
        return parser

    def _generate_nodes(
        self,
        name: str,
        command: TyperCommand,
        parent: ty.Optional[TyperContext],
        nested: str,
        commands: ty.Optional[ty.List[str]] = None,
        semantic_group: bool = False,
    ) -> ty.List[nodes.section]:
        """Generate the relevant Sphinx nodes.

        Format a `click.Group` or `click.Command`.

        :param name: Name of command, as used on the command line
        :param command: Instance of `click.Group` or `click.Command`
        :param parent: Instance of `click.Context`, or None
        :param nested: The granularity of subcommand details.
        :param commands: Display only listed commands or skip the section if
            empty
        :param semantic_group: Display command as title and description for
            `click.CommandCollection`.
        :returns: A list of nested docutil nodes
        """
        ctx = click.Context(command, info_name=name, parent=parent)

        if command.hidden:
            return []

        # Title

        section = nodes.section(
            '',
            nodes.title(text=name),
            ids=[nodes.make_id(ctx.command_path)],
            names=[nodes.fully_normalize_name(ctx.command_path)],
        )

        # Summary
        source_name = ctx.command_path
        result = statemachine.ViewList()

        ctx.meta["sphinx-click-env"] = self.env
        if semantic_group:
            lines = _format_description(ctx)
        else:
            lines = _format_command(ctx, nested, commands)

        for line in lines:
            LOG.debug(line)
            result.append(line, source_name)

        sphinx_nodes.nested_parse_with_titles(self.state, result, section)

        # Subcommands

        if nested == NESTED_FULL:
            if isinstance(command, click.CommandCollection):
                for source in command.sources:
                    section.extend(
                        self._generate_nodes(
                            source.name,
                            source,
                            parent=ctx,
                            nested=nested,
                            semantic_group=True,
                        )
                    )
            else:
                commands = _filter_commands(ctx, commands)
                for command in commands:
                    parent = ctx if not semantic_group else ctx.parent
                    section.extend(
                        self._generate_nodes(
                            command.name, command, parent=parent, nested=nested
                        )
                    )

        return [section]

    def run(self) -> ty.Iterable[nodes.section]:
        self.env = self.state.document.settings.env

        command = self._load_module(self.arguments[0])

        if 'prog' not in self.options:
            raise self.error(':prog: must be specified')

        prog_name = self.options.get('prog')
        show_nested = 'show-nested' in self.options
        nested = self.options.get('nested')

        if show_nested:
            if nested:
                raise self.error(
                    "':nested:' and ':show-nested:' are mutually exclusive"
                )
            else:
                warnings.warn(
                    "':show-nested:' is deprecated; use ':nested: full'",
                    DeprecationWarning,
                )
                nested = NESTED_FULL if show_nested else NESTED_SHORT

        commands = None
        if self.options.get('commands'):
            commands = [
                command.strip() for command in self.options.get('commands').split(',')
            ]

        return self._generate_nodes(prog_name, command, None, nested, commands)


def setup(app: application.Sphinx) -> t.Dict[str, t.Any]:
    # Need autodoc to support mocking modules
    app.setup_extension('sphinx.ext.autodoc')
    app.add_directive('click', ClickDirective)


    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
