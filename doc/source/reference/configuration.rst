.. include:: ../refs.rst

.. _configuration:

.. role:: code-py(code)
   :language: Python

=============
Configuration
=============

The following extension scoped configuration parameters are available. These should be added to the
:doc:`Sphinx configuration file <sphinx:usage/configuration>`. For example, to override the
default :func:`~sphinxcontrib.typer.typer_render_html` function our
:doc:`conf.py <sphinx:usage/configuration>` might look like:

.. code-block:: python

    import html

    extensions = [
        'sphinxcontrib.typer',
    ]

    # change the default iframe padding
    typer_iframe_height_padding = 20

    # redfine the default render_html function
    def typer_render_html(
        directive: TyperDirective,
        normal_cmd: str,
        html_page: str
    ) -> str:
        return f'<iframe srcdoc="{html.escape(html_page)}"></iframe>'

Configuration Attributes
------------------------

.. confval:: typer_iframe_height_padding
   :type: :code-py:`int`
   :default: :code-py:`30`

    A number of pixels to use for padding html iframes.

.. confval:: typer_render_html
   :type: :code-py:`str | Callable[[TyperDirective, str, str], str]`
   :default: :code-py:`"sphinxcontrib.typer.typer_render_html"`

    A callable function (or import path to a callable function) that returns the html to embed in an
    html page. Only used if the target format is html. See default implementation
    :func:`~sphinxcontrib.typer.typer_render_html`.

.. confval:: typer_get_iframe_height
   :type: :code-py:`str | Callable[[TyperDirective, str, str], int]`
   :default: :code-py:`"sphinxcontrib.typer.typer_get_iframe_height"`

   A callable function that determines height of the iframe when rendering html format onto an html
   page. The function must return an integer containing the iframe height. See the default
   implementation :func:`~sphinxcontrib.typer.typer_get_iframe_height`.

.. confval:: typer_svg2pdf
   :type: :code-py:`str | Callable[[TyperDirective, str, str], None]`
   :default: :code-py:`"sphinxcontrib.typer.typer_svg2pdf"`

   A callable function to convert svg to pdf. The function must write the converted pdf
   format to the given path. This is only used for latex/pdf builders. See the default
   implementation :func:`~sphinxcontrib.typer.typer_svg2pdf`.

.. confval:: typer_convert_png
   :type: :code-py:`str | Callable[[TyperDirective, str, str | Path, int, int], None]`
   :default: :code-py:`"sphinxcontrib.typer.typer_convert_png"`

   A callable function to convert the given format to png. The function must write the
   converted png format to the given path. This function is used when the builder is
   listed in the :rst:dir:`typer:convert-png:` parameter. See the default implementation
   :func:`~sphinxcontrib.typer.typer_convert_png`.

.. confval:: typer_get_web_driver
    :type: :code-py:`str | Callable[[TyperDirective, int, int], ContextManager[WebDriver]]`
    :default: :code-py:`"sphinxcontrib.typer.typer_get_web_driver"`

    A callable function to get a :pypi:`selenium` web driver. This function must be a context
    manager and it must yield a :pypi:`selenium` web driver. It is used by other workflows that need
    access to a webdriver. See the default implementation
    :func:`~sphinxcontrib.typer.typer_get_web_driver`.


Function Hooks
--------------

These functions may all be redefined in :doc:`conf.py <sphinx:usage/configuration>` to override
default behaviors. Your override functions must conform to these function signatures.

.. warning::

  Sphinx will warn that these functions are not pickleable. This messes up sphinx's caching but
  that wont break the doc build. You can either suppress the warning or specify these configuration
  values as import strings instead.

.. autofunction:: sphinxcontrib.typer.typer_render_html
.. autofunction:: sphinxcontrib.typer.typer_get_iframe_height
.. autofunction:: sphinxcontrib.typer.typer_svg2pdf
.. autofunction:: sphinxcontrib.typer.typer_convert_png
.. autofunction:: sphinxcontrib.typer.typer_get_web_driver

