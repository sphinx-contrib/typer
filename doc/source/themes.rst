.. include:: ./refs.rst

Themes
======

You can always create and use custom themes with the :rst:dir:`typer:svg-kwargs`,
:rst:dir:`typer:html-kwargs`, and :rst:dir:`typer:console-kwargs` options but there are also
predefined named themes available that can be swapped in using the :rst:dir:`typer:theme` option.

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
    :width: 63
    :convert-png: latex

|

Dark
----

.. code-block:: rst

    :theme: dark

.. typer:: examples.example:app
    :theme: dark
    :width: 64
    :convert-png: latex

|

Monokai
-------

.. code-block:: rst

    :theme: monokai

.. typer:: examples.example:app
    :theme: monokai
    :width: 65
    :convert-png: latex

|

Dimmed Monokai
--------------

.. code-block:: rst

    :theme: dimmed_monokai

.. typer:: examples.example:app
    :theme: dimmed_monokai
    :width: 66
    :convert-png: latex

|

Night Owlish
------------

.. code-block:: rst

    :theme: night_owlish

.. typer:: examples.example:app
    :theme: night_owlish
    :width: 67
    :convert-png: latex

|

Red Sands
---------

.. code-block:: rst

    :theme: red_sands

.. typer:: examples.example:app
    :theme: red_sands
    :width: 68
    :convert-png: latex

|

Blue Waves
----------

.. code-block:: rst

    :theme: blue_waves

.. typer:: examples.example:app
    :theme: blue_waves
    :width: 69
    :convert-png: latex
