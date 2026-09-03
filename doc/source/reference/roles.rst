.. include:: ../refs.rst

.. _directive_roles:

=====
Roles
=====

The ``typer`` role allows you to cross reference a Typer command or subcommand in your
documentation. The syntax is:

.. code-block:: rst

    :typer:`progname-subcommand1-subcomand2`

You can also use a string identical to the :prog: setting to make the reference. For example if
``:prog:`` is ``python -m progname.py subcommand1 subcommand2`` this will also work:

.. code-block:: rst

    :typer:`python -m progname.py subcommand1 subcommand2`

Explicit link text may be given using the usual Sphinx syntax:

.. code-block:: rst

    :typer:`link text <progname-subcommand1>`

Commands are registered in the ``typer`` domain. This means references are also
resolvable through the :rst:role:`any` role and are exported to the objects
inventory, so other projects can link to your commands using
:mod:`sphinx.ext.intersphinx`:

.. code-block:: rst

    :typer:`other-project-command`

.. note::

  Every command rendered by the :rst:dir:`typer` directive is a valid reference
  target, whether or not :rst:dir:`typer:make-sections` is used. When sections
  are not made the link resolves to the container holding the rendered help.
