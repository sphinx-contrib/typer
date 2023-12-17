.. include:: ./refs.rst

Click
=====

Because Typer_ is built with Click_ sphinxcontrib-typer_ will also
work on click apps!

For example consider this complex example from the Click_ docs:

.. literalinclude:: ../examples/click/hello.py
   :language: python
   :linenos:

We could generate the docs for this app with the following command:

.. code-block:: rst

    .. typer:: examples.click.hello:hello
        :make-sections:


Which results in:

.. typer:: examples.click.hello:hello
    :make-sections:
    :convert-png: latex


Command Collections
-------------------

Collections of commands also work:

.. literalinclude:: ../examples/click/collection.py
   :language: python
   :linenos:


We could generate the docs for this app with the following command:

.. code-block:: rst

    .. typer:: examples.click.collection:cli
        :prog: collection
        :show-nested:
        :make-sections:


Which results in:

.. typer:: examples.click.collection:cli
    :prog: collection
    :make-sections:
    :show-nested:
    :convert-png: latex
