.. include:: ../refs.rst

.. _directives:

==========
Directives
==========


.. rst:directive:: typer

  .. code-block:: rst

    .. typer:: import.path.to.module:main
      :prog: script_name
      :make-sections:
      :show-nested:
      :markup-mode: markdown
      :width: 65
      :preferred: html
      :builders: html=html,svg,text:latex=svg,text:text=text
      :iframe-height: 600
      :convert-png: html|latex
      :theme: light
      :console-kwargs: import.path.to.console_kwargs
      :svg-kwargs: import.path.to.svg_kwargs
      :html-kwargs: import.path.to.html_kwargs
      :text-kwargs: import.path.to.text_kwargs

  The only required parameter is the first argument. This is an import path to the Typer_
  or :doc:`Click <click:index>` application to render. It may also include nested subcommands and
  may be delimited by either ``.``, ``:`` or ``::`` characters. For example, to render a subcommand
  called `print` from another subcommand called `add` in a Typer app named `app` in a module called
  `command` in a package called `mypackage`:

  .. code-block:: rst

      .. typer:: mypackage.command.app:add:print

  .. rst:directive:option:: prog: program cli name
      :type: text

      The script invocation name to use in the rendered help text. This parameter is optional,
      the directive will attempt to infer the name but this is not always possible to do reliably
      solely from the source code. If the name cannot be inferred, this parameter should be
      supplied.

  .. rst:directive:option:: make-sections
      :type: flag

      This is a flag parameter. If set, the directive will generate hierarchical sections for
      each command.

  .. rst:directive:option:: show-nested
     :type: flag

     This is a flag parameter. If set, the directive will include all subcommands in the command
     tree.

  .. rst:directive:option:: markup-mode
      :type: text

      Override the Typer rich_markup_mode command configuration value. Supports either ``markdown``
      or ``rich``. See the
      `Typer docs <https://typer.tiangolo.com/tutorial/commands/help/#rich-markdown-and-markup>`_.

  .. rst:directive:option:: width
      :type: integer

      **default**: ``65``

      The width of the terminal window to use when rendering the help through rich.
      65 is a good value for text or html renderings on the read the docs theme

  .. rst:directive:option:: preferred
      :type: text

      The preferred render format. Either ``html``, ``svg`` or ``text``. If not supplied the render
      format will be inferred from the builder's priority supported format list. You can
      replace the default priority lists with the **builders** parameter. The default format for
      the html and latex builders is *svg*.

  .. rst:directive:option:: builders
      :type: text - a colon delimited list of mappings from builder name to priority ordered csv of
        supported formats.

      **default**: html=html,svg,text:latex=svg,text:text=text

      Override the default builder priority render format lists. For example the preset is
      equivalent to::

        html=html,svg,text:latex=svg,text:text=text

      This parameter can be helpful if you're rendering your docs with multiple builders and
      do not want the preset formats.

  .. rst:directive:option:: iframe-height
      :type: integer

      **default**: ``600``

      The height of the iframe to use when rendering to *html*. When *html* rendering is embedded
      in an html page an iframe is used. The height of the iframe can be set with this parameter.
      Alternatively, the height of the iframe can be dynamically determined if :pypi:`selenium` is
      installed. See also iframe height cache.

  .. rst:directive:option:: convert-png
      :type: text - a delimited list of builders

      Convert the rendered help to a png file for this delimited list of builders. The delimiter can
      be any character. For example:

      .. code-block:: rst

        .. typer:: import.path.to.module:main
          :convert-png: html|latex

      All formats, *html*, *text* and *svg* can be converted to png. For some builders, namely
      pdf the *html* and *svg* formats may require non standard fonts to be installed or
      otherwise render unpredictably. The png format is a good alternative for these builders.

  .. rst:directive:option:: theme
      :type: text

      **default**: ``light``

      A named rich terminal theme to use when rendering the help in either html or svg formats.
      Supported themes:

        * light
        * dark
        * monokai
        * dimmed_monokai
        * night_owlish
        * red_sands
        * blue_waves

  .. rst:directive:option:: console-kwargs
      :type: text

      A python import path to a dictionary or callable returning a dictionary containing parameters
      to pass to the rich console before output rendering. The defaults are those defined by the
      Typer library. See :class:`rich.console.Console`.

  .. rst:directive:option:: svg-kwargs
      :type: text

      A python import path to a dictionary or callable returning a dictionary containing parameters
      to pass to the rich console export_svg function. See :meth:`rich.console.Console.export_svg`.

  .. rst:directive:option:: html-kwargs
      :type: text

      A python import path to a dictionary or callable returning a dictionary containing parameters
      to pass to the rich console export_html function. See
      :meth:`rich.console.Console.export_html`.

  .. rst:directive:option:: text-kwargs
      :type: text

      A python import path to a dictionary or callable returning a dictionary containing parameters
      to pass to the rich console export_text function.
      See :meth:`rich.console.Console.export_text`.

