.. include:: ./refs.rst

Themes
======

You can always create and use custom themes with the `:svg-kwargs:`, `:html-kwargs:`, and
`:console-kwargs:` options but there are also predefined named themes available that can be swapped
in using the `:theme:` option.

.. code-block:: rst

    .. typer:: examples.example:app
        :theme: dark

|

Light (default)
---------------

.. code-block:: rst

    :theme: light

.. typer:: examples.example:app
    :theme: light
    :width: 60
    :convert-png: latex

|

Dark
----

.. code-block:: rst

    :theme: dark

.. typer:: examples.example:app
    :theme: dark
    :width: 61
    :convert-png: latex

|

Monokai
-------

.. code-block:: rst

    :theme: monokai

.. typer:: examples.example:app
    :theme: monokai
    :width: 62
    :convert-png: latex

|

Dimmed Monokai
--------------

.. code-block:: rst

    :theme: dimmed_monokai

.. typer:: examples.example:app
    :theme: dimmed_monokai
    :width: 63
    :convert-png: latex

|

Night Owlish
------------

.. code-block:: rst

    :theme: night_owlish

.. typer:: examples.example:app
    :theme: night_owlish
    :width: 64
    :convert-png: latex
