.. include:: ./refs.rst

Reference
=========

Directive Options
-----------------

.. code-block:: rst

    .. typer:: import.path.to.module:main
        :prog: script_name
        :make-sections:
        :show-nested:
        :markup-mode: markdown
        :width: 80
        :preferred: html
        :builders: html=html,svg,text:latex=svg,text:text=text
        :iframe-height: 600
        :convert-png: html|latex
        :console-kwargs: import.path.to.console_kwargs
        :svg-kwargs: import.path.to.svg_kwargs
        :html-kwargs: import.path.to.html_kwargs
        :text-kwargs: import.path.to.text_kwargs

The only required parameter is the first argument. This is an import path to the Typer_
or Click_ application to render. It may also include nested subcommands and may be delimited
by either ``.``, ``:`` or ``::`` characters. For example, to render a subcommand called `print`
from another subcommand called `add` in a Typer app named `app` in a module called `command` in a
package called `mypackage`:

.. code-block:: rst

    .. typer:: mypackage.command.app:add:print


.. list-table::
   :widths: 20 10 70
   :header-rows: 1

   * - Parameter
     - Type
     - Description
   * - **prog**
     - ``string``
     - The script invocation name to use in the rendered help text. This parameter is optional,
       the directive will attempt to infer the name but this is not always possible to do reliably
       solely from the source code. If the name cannot be inferred, this parameter should be
       supplied.
   * - **make-sections**
     - ``flag``
     - This is a flag parameter. If set, the directive will generate hierarchical sections for
       each command.
   * - **show-nested**
     - ``flag``
     - This is a flag parameter. If set, the directive will include all subcommands in the command
       tree.
   * - **markup-mode**
     - ``string``
     - Override the Typer rich_markup_mode command configuration value. Supports either 'markdown'
       or 'rich'. See the `Typer docs <https://typer.tiangolo.com/tutorial/commands/help/#rich-markdown-and-markup>`_.
   * - **width**
     - ``int``
     - The width of the terminal window to use when rendering the help through rich. Default: 80.
       65 is a good value for text or html renderings on the read the docs theme.
   * - **preferred**
     - ``string``
     - The preferred render format. Either *html*, *svg* or *text*. If not supplied the render
       format will be inferred from the builder's priority supported format list. You can
       replace the default priority lists with the **builders** parameter. The default format for
       the html and latex builders is *svg*.
   * - **builders**
     - ``string``
     - Override the default builder priority render format lists. For example the preset is 
       equivalent to::
        
        html=html,svg,text:latex=svg,text:text=text
      
       This parameter can be helpful if you're rendering your docs with multiple builders and
       do not want the preset formats.
   * - **iframe-height**
     - ``int``
     - The height of the iframe to use when rendering to *html*. When *html* rendering is embedded
       in an html page an iframe is used. The height of the iframe can be set with this parameter.
       Alternatively, the height of the iframe can be dynamically determined if selenium_ is installed.
       Default: 600. See also iframe height cache.
   * - **convert-png**
     - ``string``
     - Convert the rendered help to a png file for this delimited list of builders. The delimiter can
       be any character. For example:
       
        .. code-block:: rst
          
          .. typer:: import.path.to.module:main
            :convert-png: html|latex

       All formats, *html*, *text* and *svg* can be converted to png. For some builders, namely
       pdf the *html* and *svg* formats may require non standard fonts to be installed or
       otherwise render unpredictably. The png format is a good alternative for these builders.
   * - **console-kwargs**
     - ``string``
     - A python import path to a dictionary or callable returning a dictionary containing parameters to
       pass to the rich console before output rendering. The defaults are those defined by the
       Typer library. See `rich.console <https://rich.readthedocs.io/en/latest/reference/console.html#rich.console.Console>`_.
   * - **svg-kwargs**
     - ``string``
     - A python import path to a dictionary or callable returning a dictionary containing parameters to
       pass to the rich console export_svg function. 
       See `rich.console.export_svg <https://rich.readthedocs.io/en/latest/reference/console.html#rich.console.Console.export_svg>`_.
   * - **html-kwargs**
     - ``string``
     - A python import path to a dictionary or callable returning a dictionary containing parameters to
       pass to the rich console export_html function. 
       See `rich.console.export_html <https://rich.readthedocs.io/en/latest/reference/console.html#rich.console.Console.export_html>`_.
   * - **text-kwargs**
     - ``string``
     - A python import path to a dictionary or callable returning a dictionary containing parameters to
       pass to the rich console export_text function. 
       See `rich.console.export_text <https://rich.readthedocs.io/en/latest/reference/console.html#rich.console.Console.export_text>`_.



Configuration Parameters
------------------------

The following extension scoped configuration parameters are available. These should be added to the
`conf.py` Sphinx configuration file. For example, to override the default typer_render_html
function our `conf.py` might look like:

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


.. list-table::
   :widths: 40 10 50
   :header-rows: 1

   * - Parameter
     - Type
     - Description
   * - **typer_iframe_height_padding**
     - ``int``
     - A number of pixels to use for padding html iframes. Default: 30
   * - **typer_iframe_height_cache_path**
     - ``path``
     - A path to a file to use to cache dynamically determined iframe heights.
       Default: ``<conf dir>/typer_cache.json``
   * - **typer_render_html**
     - ``callable``
     - A callable function that returns the html to embed in an html page. Only used
       if the target format is html.
       See the default implementation:  :func:`sphinxcontrib.typer.typer_render_html`
   * - **typer_get_iframe_height**
     - ``callable``
     - A callable function that determines height of the iframe when rendering html format
       onto an html page. The function must return an integer containing the iframe height.
       See the default implementation:  :func:`sphinxcontrib.typer.typer_get_iframe_height`
   * - **typer_svg2pdf**
     - ``callable``
     - A callable function to convert svg to pdf. The function must write the converted pdf
       format to the given path. This is only used for latex/pdf builders.
       See the default implementation: :func:`sphinxcontrib.typer.typer_svg2pdf`
   * - **typer_convert_png**
     - ``callable``
     - A callable function to convert the given format to png. The function must write the
       converted png format to the given path. This function is used when the builder is
       listed in the ``:convert-png:`` parameter.
       See the default implementation: :func:`sphinxcontrib.typer.typer_convert_png`
   * - **typer_get_web_driver**
     - ``callable``
     - A callable function to get a selenium web driver. This function must be a context manager
       and it must yield a selenium web driver. It is used by other workflows that need access to
       a webdriver. See the default implementation: :func:`sphinxcontrib.typer.typer_get_web_driver`


Function Hooks
~~~~~~~~~~~~~~

These functions may all be redefined in `conf.py` to override default behaviors. Your override
functions must conform to these function signatures.

.. autofunction:: sphinxcontrib.typer.typer_render_html
.. autofunction:: sphinxcontrib.typer.typer_get_iframe_height
.. autofunction:: sphinxcontrib.typer.typer_svg2pdf
.. autofunction:: sphinxcontrib.typer.typer_convert_png
.. autofunction:: sphinxcontrib.typer.typer_get_web_driver
