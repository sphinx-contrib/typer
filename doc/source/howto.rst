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
:pypi:`selenium` and a web driver. To use the dynamic height calculation, you must install the html
dependency set:

.. code-block:: bash

    pip install sphinxcontrib-typer[html]

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


.. _cross_references:

Cross-Reference with :make-sections:
------------------------------------

When using the :rst:dir:`typer:make-sections` option, a section will be generated for each
subcommand. You can cross reference these sections using the ``:typer:`` role. For example, to
reference the :typer:`example-bar` subcommand from the :ref:`render_structure` section above:

.. code-block:: rst

    :typer:`example-bar`


The format for the reference is ``prog(-subcommand)``
