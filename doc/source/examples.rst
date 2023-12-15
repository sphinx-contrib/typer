
========
Examples
========

If we have a command that looks like this:

.. literalinclude:: ../examples/example1.py
   :language: python

.. code-block:: rst

    .. typer:: examples.example1.app
        :prog: example1
        :width: 60
        :preferred: html

.. typer:: examples.example1.app
    :prog: example1
    :make-sections:
    :show-nested:
    :width: 70
    :preferred: html

.. typer:: examples.example1.app:bar
    :prog: example1 bar
    :width: 65
    :preferred: svg

