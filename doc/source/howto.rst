.. include:: ./refs.rst

How To
======

The examples below all reference this example Typer_ application:

.. literalinclude:: ../examples/example.py
    :language: python
    :linenos:
    :caption: examples/example.py

|

Build to Multiple Formats
-------------------------

:doc:`sphinx:index` caches directive output and reuses the results when building the documentation
to different formats (e.g. html, pdf or text). This causes problems with the way the typer directive
dynamically determines which render target to use based on the active builder. This can mean that if
you run :doc:`sphinx:man/sphinx-build` for html and
:class:`latexpdf <sphinx.builders.latex.LaTeXBuilder>` at the same time the pdf may not render all
typer helps as expected. To work around this you can do one of four things

1. Run :doc:`sphinx:man/sphinx-build` for each format separately.
2. Use the :rst:dir:`sphinx:only` directive in combination with :rst:dir:`typer:preferred` to
   specify builder specific content.
3. Use the :option:`--fresh-env <sphinx-build.--fresh-env>` option to force sphinx to rebuild the
   directive output for each builder.
4. Add the following code to your conf.py to remove the doctree between builders:

    .. code-block:: python

        def setup(app):
            import shutil
            from pathlib import Path
            if Path(app.doctreedir).exists():
                shutil.rmtree(app.doctreedir)



Change the Width
----------------

The :rst:dir:`typer:width` parameter defines the console character length :doc:`rich <rich:index>`
uses when it generates the console output. If your image is too wide, you can reduce the width by
setting the :rst:dir:`typer:width` parameter to a smaller value. For example, for
:doc:`sphinx-rtd-theme <sphinx-rtd-theme:index>` theme a width parameter of 65 works well:

.. code-block:: rst

    .. typer:: examples.example:app
        :width: 65

    .. typer:: examples.example:app
        :width: 100

.. typer:: examples.example:app
    :width: 65
    :convert-png: latex

.. typer:: examples.example:app
    :width: 100
    :convert-png: latex

|

.. _render_structure:

Render Subcommand Structure
---------------------------

Add the :rst:dir:`typer:show-nested` and :rst:dir:`typer:make-sections` options to the typer
directive. This will render all subcommands as sections.

.. code-block:: rst

    .. typer:: examples.example:app
        :width: 65
        :show-nested:
        :make-sections:

.. typer:: examples.example:app
    :width: 65
    :show-nested:
    :make-sections:
    :convert-png: latex

.. tip::

    See :ref:`cross_references` for information on how to cross reference sections.

|

Render a Single Subcommand
--------------------------

Subcommands can be rendered individually:

.. code-block:: rst

    .. typer:: examples.example:app:bar
        :width: 65
        :show-nested:
        :make-sections:

.. typer:: examples.example:app:bar
    :width: 65
    :show-nested:
    :make-sections:
    :convert-png: latex

|

Render as HTML
--------------

By default for html builders, svg output is generated. HTML output is also supported, but requires
rendering the html output into an iframe to isolate the generated css. The iframe heights can be
given directly using the :rst:dir:`typer:iframe-height` option - or dynamically calculated using
:pypi:`playwright` and a headless browser. To use the dynamic height calculation, you must install
the html dependency set:

.. code-block:: bash

    pip install sphinxcontrib-typer[html]

The chromium browser is downloaded automatically the first time it is needed unless
:confval:`typer_playwright_install` is disabled.

Otherwise provide the :rst:dir:`typer:iframe-height` option. Use :rst:dir:`typer:preferred` html to
render the html output

.. code-block:: rst

    .. typer:: examples.example:app
        :preferred: html
        :width: 65
        :iframe-height: 300


.. typer:: examples.example:app
    :preferred: html
    :width: 65
    :iframe-height: 300
    :convert-png: latex

|

Generate Nice PDFs
------------------

By default the latex builder will convert the preferred rendering output to pdf. This may not
render predictably if the necessary fonts are not installed. You will likely need to install
`FiraCode <https://github.com/tonsky/FiraCode>`_. You will also need to install the pdf
dependency set:

.. code-block:: bash

    pip install sphinxcontrib-typer[pdf]

Alternatively you can convert the rendered helps to png format using the
:rst:dir:`typer:convert-png` option and passing it the builders you want to render pngs. You will
also need to install the png dependency set:

.. code-block:: bash

    pip install sphinxcontrib-typer[png]

Any format can be converted to png - even text!

.. code-block:: rst

    .. typer:: examples.example:app
        :preferred: text
        :width: 90

    .. typer:: examples.example:app
        :preferred: text
        :width: 90
        :convert-png: latex|html


.. typer:: examples.example:app
    :preferred: text
    :width: 75

.. typer:: examples.example:app
    :preferred: text
    :width: 90
    :convert-png: latex|html

|

:class:`latexpdf <sphinx.builders.latex.LaTeXBuilder>` often has issues with unicode characters.
You may get better results using the xeLaTeX engine instead, especially when rendering text.

In your conf.py add:

.. code-block:: python

    latex_engine = "xelatex"


Customize the Rendered Output
-----------------------------

The initialization parameters for the :doc:`rich console <rich:reference/console>` and export
functions can be overridden to provide more fine grained control over the rendered output. For
example, to render a console that looks like Red Sands on OSX we can use the
:rst:dir:`typer:svg-kwargs` option, and pass an import string to a dictionary of kwargs to pass to
:meth:`rich.console.export_svg`.

.. literalinclude:: ../examples/themes.py
    :language: python
    :linenos:
    :caption: examples/themes.py

.. code-block:: rst

    .. typer:: examples.example:app
        :width: 60
        :preferred: svg
        :svg-kwargs: examples.themes.red_sands


.. typer:: examples.example:app
    :width: 60
    :preferred: svg
    :svg-kwargs: examples.themes.red_sands
    :convert-png: latex


The preset Console parameters can also be overridden using the :rst:dir:`typer:console-kwargs`
option. Refer to the :doc:`rich <rich:index>` documentation for more information on the available
options.


.. _howto_light_dark:

Render for Light and Dark Modes
-------------------------------

Many Sphinx themes (Furo, pydata-sphinx-theme, sphinx-book-theme) let the reader switch between
light and dark modes in the browser. Since the mode is chosen at view time it cannot be detected
when the documentation is built, instead the help can be rendered once for each mode using the
:rst:dir:`typer:dark-theme` option. Only the rendering that matches the active mode is shown:

.. code-block:: rst

    .. typer:: examples.example:app
        :theme: light
        :dark-theme: dark

.. typer:: examples.example:app
    :theme: light
    :dark-theme: dark
    :width: 65
    :convert-png: latex

.. note::

    If your ``html_theme`` is one that is known to support light and dark modes (currently
    ``furo``, ``pydata_sphinx_theme`` and ``sphinx_book_theme``) this happens automatically: the
    default value of :confval:`typer_dark_theme` is ``"auto"`` which resolves to ``"dark"`` for
    those themes, so you do not need to do anything.

Any of the named :doc:`themes <themes>` may be used for either mode. To use a different dark
theme, or to enable dual rendering for a theme that is not recognized automatically, set
:confval:`typer_dark_theme` in ``conf.py`` rather than repeating the option on every directive.
Set it to ``None`` to switch dual rendering off:

.. code-block:: python

    typer_dark_theme = "monokai"

This works for both the svg and html (iframe) render targets. Themes that do not define the
``only-light`` and ``only-dark`` classes are covered by a small stylesheet installed by the
extension that follows the ``data-theme`` attribute and the browser's color scheme preference.
Builders other than html render the primary :rst:dir:`typer:theme` only.

|

.. _cross_references:

Cross-Referencing Commands
--------------------------

Every command rendered by the :rst:dir:`typer` directive can be cross referenced using the
``:typer:`` role. When the :rst:dir:`typer:make-sections` option is used the reference links to
the generated section, otherwise it links to the rendered help output. For example, to
reference the :typer:`example-bar` subcommand from the :ref:`render_structure` section above:

.. code-block:: rst

    :typer:`example-bar`


The format for the reference is ``prog(-subcommand)``

.. _markdown:

Use from Markdown
-----------------

If your documentation is written in Markdown using MyST_, the typer directive and role are
available with MyST's directive and role syntax. The directive options are given as ``:option:``
lines at the top of the fence:

.. code-block:: markdown

    ```{typer} examples.example:app
    :prog: example
    :width: 65
    :show-nested:
    :make-sections:
    ```

The colon fence form works as well if you have enabled the ``colon_fence`` extension in
``myst_enable_extensions``:

.. code-block:: markdown

    :::{typer} examples.example:app:bar
    :prog: example bar
    :::

Cross references use the MyST role syntax, with the same target formats and optional link text
as the ``:typer:`` role:

.. code-block:: markdown

    See {typer}`example-bar` or {typer}`the bar subcommand <example-bar>`.
