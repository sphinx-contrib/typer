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

Sphinx caches directive output and reuses the results when building the documentation to
different formats (e.g. html, pdf or text). This causes problems with the way the typer
directive dynamically determines which render target to use based on the active builder.
This can mean that if you run sphinx-build for html and latexpdf at the same time the
pdf may not render all typer helps as expected. To work around this you can do one of
four things

1. Run sphinx-build for each format separately.
2. Use the `only directive <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-only>`_
   in combination with :ref:`:preferred: <directive_options>` to specify builder specific content.
3. Use the `--fresh-env <https://www.sphinx-doc.org/en/master/man/sphinx-build.html#cmdoption-sphinx-build-E>`_
   option to force sphinx to rebuild the directive output for each builder.
4. Add the following code to your conf.py to remove the doctree between builders:

    .. code-block:: python

        def setup(app):
            import shutil
            if app.doctreedir.exists():
                shutil.rmtree(app.doctreedir)


Change the Width
----------------

The `:width:` parameter defines the console character length Rich_ uses when it generates the
console output. If your image is too wide, you can reduce the width by setting the `:width:`
parameter to a smaller value. For example, for read_the_docs_ theme a width parameter of 65
works well:

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

Render Subcommand Structure
---------------------------

Add the `:show-nested:` and `:make-sections:` options to the typer directive. This will render all
subcommands as sections.

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
given directly using the `:iframe-height:` option - or dynamically calculated using selenium and
a web driver. To use the dynamic height calculation, you must install the html dependency set:

.. code-block:: bash

    pip install sphinxcontrib-typer[html]

Otherwise provide the `:iframe-height:` option. Use `:preferred:` html to render the html output

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

Alternatively you can convert the rendered helps to png format using the `:convert-png:`
option and passing it the builders you want to render pngs. You will also need to
install the png dependency set:

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

pdflatex often has issues with unicode characters. You may get better results using the xeLaTeX
engine instead, especially when rendering text.

In your conf.py add:

.. code-block:: python

    latex_engine = "xelatex"


Customize the Rendered Output
-----------------------------

The initialization parameters for the Rich_ `Console <https://rich.readthedocs.io/en/stable/reference/console.html>`_
and export functions can be overridden to provide more fine grained control over the rendered
output. For example, to render a console that looks like Red Sands on OSX we can use the
`:svg-kwargs:` option, and pass an import string to a dictionary of kwargs to pass to
`rich.console.export_svg <https://rich.readthedocs.io/en/latest/reference/console.html#rich.console.Console.export_svg>`_.

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


The preset Console parameters can also be overridden using the `:console-kwargs:` option. Refer to
the Rich_ documentation for more information on the available options.
