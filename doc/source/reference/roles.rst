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

.. note::

  This is only works when you've made sections for your commands using the
  :rst:dir:`typer:make-sections` option.
