.. include:: ./refs.rst

How To
======

The examples below all reference this example Typer_ application:

.. literalinclude:: ../examples/example.py
    :language: python
    :linenos:


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


Render Subcommand Structure
---------------------------

Add the `:show-nested:` and `:make-sections:` options to the typer directive. This will render all
subcommands as sections.



Render as HTML
--------------

By default for html builders, svg output is generated. HTML output is also supported, but requires
rendering the html output into an iframe to isolate the generated css. 



Generate Nice PDFs
------------------

By default the latex builder will convert the preferred rendering output to pdf. This may 


