|MIT license| |PyPI version fury.io| |PyPI pyversions| |PyPI status| |Documentation Status|
|Code Cov| |Test Status|

.. |MIT license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://lbesson.mit-license.org/

.. |PyPI version fury.io| image:: https://badge.fury.io/py/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer/

.. |PyPI status| image:: https://img.shields.io/pypi/status/sphinxcontrib-typer.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-typer

.. |Documentation Status| image:: https://readthedocs.org/projects/sphinxcontrib-typer/badge/?version=latest
   :target: http://sphinxcontrib-typer.readthedocs.io/?badge=latest/

.. |Code Cov| image:: https://codecov.io/gh/bckohan/sphinxcontrib-typer/branch/main/graph/badge.svg?token=0IZOKN2DYL
   :target: https://codecov.io/gh/bckohan/sphinxcontrib-typer

.. |Test Status| image:: https://github.com/bckohan/sphinxcontrib-typer/workflows/test/badge.svg
   :target: https://github.com/bckohan/sphinxcontrib-typer/actions


===================
sphinxcontrib-typer
===================

.. _Typer: https://typer.tiangolo.com/
.. _Click: https://click.palletsprojects.com/
.. _sphinx-click: https://sphinx-click.readthedocs.io/en/latest/

A Sphinx directive for auto generating docs for Typer_ (and Click_ commands!)
using the rich console formatting available in Typer_. This package generates
beautiful command documentation in text, html or svg formats out of the box,
but if your goal is to greatly customize the generated documentation 
sphinx-click_ may be more appropriate and will also work for Typer_ commands.

Installation
============

Install with pip::

    pip install sphinxcontrib-typer

Add ``sphinxcontrib.typer`` to your ``conf.py`` file::

    extensions = [
        ...
        'sphinxcontrib.typer',
        ...
    ]

Usage
=====

Say you have a command in the file ``examples/example.py`` that looks like
this:

.. literalinclude:: ../examples/example.py
   :language: python

You can generate documentation for this command using the ``typer`` directive
like so:

.. code-block:: rst

    .. typer:: examples.example.app
        :prog: example1
        :width: 70
        :preferred: html


This would generate html that looks like this:

.. raw:: html

    <iframe style="border: none;" width="100%" height="328px" srcdoc="<!DOCTYPE html>
    <html>
    <head>
    <meta charset=&quot;UTF-8&quot;>
    <style>
    .r1 {font-weight: bold}
    .r2 {color: #808000; text-decoration-color: #808000; font-weight: bold}
    .r3 {color: #7f7f7f; text-decoration-color: #7f7f7f}
    .r4 {color: #008080; text-decoration-color: #008080; font-weight: bold}
    .r5 {color: #800080; text-decoration-color: #800080; font-weight: bold}
    body {
        color: #000000;
        background-color: #ffffff;
    }
    </style>
    </head>
    <body>
        <pre style=&quot;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace&quot;><code style=&quot;font-family:inherit&quot;><span class=&quot;r1&quot;>                                                                      </span>
    <span class=&quot;r1&quot;> </span><span class=&quot;r2&quot;>Usage: </span><span class=&quot;r1&quot;>example [OPTIONS] COMMAND [ARGS]...                           </span>
    <span class=&quot;r1&quot;>                                                                      </span>
    This is the callback function.                                       
                                                                        
    <span class=&quot;r3&quot;>╭─ Options ──────────────────────────────────────────────────────────╮</span>
    <span class=&quot;r3&quot;>│</span> <span class=&quot;r4&quot;>--flag1</span>    <span class=&quot;r5&quot;>--no-flag1</span>      Flag 1. <span class=&quot;r3&quot;>[default: no-flag1]</span>             <span class=&quot;r3&quot;>│</span>
    <span class=&quot;r3&quot;>│</span> <span class=&quot;r4&quot;>--flag2</span>    <span class=&quot;r5&quot;>--no-flag2</span>      Flag 2. <span class=&quot;r3&quot;>[default: no-flag2]</span>             <span class=&quot;r3&quot;>│</span>
    <span class=&quot;r3&quot;>│</span> <span class=&quot;r4&quot;>--help</span>                     Show this message and exit.             <span class=&quot;r3&quot;>│</span>
    <span class=&quot;r3&quot;>╰────────────────────────────────────────────────────────────────────╯</span>
    <span class=&quot;r3&quot;>╭─ Commands ─────────────────────────────────────────────────────────╮</span>
    <span class=&quot;r3&quot;>│</span> <span class=&quot;r4&quot;>bar       </span> This is the bar command.                                <span class=&quot;r3&quot;>│</span>
    <span class=&quot;r3&quot;>│</span> <span class=&quot;r4&quot;>foo       </span> This is the foo command.                                <span class=&quot;r3&quot;>│</span>
    <span class=&quot;r3&quot;>╰────────────────────────────────────────────────────────────────────╯</span>
    </code></pre>
    </body>
    </html>
    "></iframe>


You could change ``:preferred:`` to svg, to generate svg instead:

.. raw:: html

    <svg class="rich-terminal" viewBox="0 0 994 391.59999999999997" xmlns="http://www.w3.org/2000/svg">
    <!-- Generated with Rich https://www.textualize.io -->
    <style>

    @font-face {
        font-family: "Fira Code";
        src: local("FiraCode-Regular"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
        font-style: normal;
        font-weight: 400;
    }
    @font-face {
        font-family: "Fira Code";
        src: local("FiraCode-Bold"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
        font-style: bold;
        font-weight: 700;
    }

    .terminal-1650207396-matrix {
        font-family: Fira Code, monospace;
        font-size: 20px;
        line-height: 24.4px;
        font-variant-east-asian: full-width;
    }

    .terminal-1650207396-title {
        font-size: 18px;
        font-weight: bold;
        font-family: arial;
    }

    .terminal-1650207396-r1 { fill: #c5c8c6;font-weight: bold }
    .terminal-1650207396-r2 { fill: #c5c8c6 }
    .terminal-1650207396-r3 { fill: #d0b344;font-weight: bold }
    .terminal-1650207396-r4 { fill: #868887 }
    .terminal-1650207396-r5 { fill: #68a0b3;font-weight: bold }
    .terminal-1650207396-r6 { fill: #98729f;font-weight: bold }
        </style>

        <defs>
        <clipPath id="terminal-1650207396-clip-terminal">
        <rect x="0" y="0" width="975.0" height="340.59999999999997"></rect>
        </clipPath>
        <clipPath id="terminal-1650207396-line-0">
        <rect x="0" y="1.5" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-1">
        <rect x="0" y="25.9" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-2">
        <rect x="0" y="50.3" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-3">
        <rect x="0" y="74.7" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-4">
        <rect x="0" y="99.1" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-5">
        <rect x="0" y="123.5" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-6">
        <rect x="0" y="147.9" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-7">
        <rect x="0" y="172.3" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-8">
        <rect x="0" y="196.7" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-9">
        <rect x="0" y="221.1" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-10">
        <rect x="0" y="245.5" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-11">
        <rect x="0" y="269.9" width="976" height="24.65"></rect>
                </clipPath>
    <clipPath id="terminal-1650207396-line-12">
        <rect x="0" y="294.3" width="976" height="24.65"></rect>
                </clipPath>
        </defs>

        <rect fill="#292929" stroke="rgba(255,255,255,0.35)" stroke-width="1" x="1" y="1" width="992" height="389.6" rx="8"></rect><text class="terminal-1650207396-title" fill="#c5c8c6" text-anchor="middle" x="496" y="27">example</text>
                <g transform="translate(26,22)">
                <circle cx="0" cy="0" r="7" fill="#ff5f57"></circle>
                <circle cx="22" cy="0" r="7" fill="#febc2e"></circle>
                <circle cx="44" cy="0" r="7" fill="#28c840"></circle>
                </g>
            
        <g transform="translate(9, 41)" clip-path="url(#terminal-1650207396-clip-terminal)">
        
        <g class="terminal-1650207396-matrix">
        <text class="terminal-1650207396-r2" x="976" y="20" textLength="12.2" clip-path="url(#terminal-1650207396-line-0)">
    </text><text class="terminal-1650207396-r3" x="12.2" y="44.4" textLength="85.4" clip-path="url(#terminal-1650207396-line-1)">Usage:&nbsp;</text><text class="terminal-1650207396-r1" x="97.6" y="44.4" textLength="427" clip-path="url(#terminal-1650207396-line-1)">example&nbsp;[OPTIONS]&nbsp;COMMAND&nbsp;[ARGS]...</text><text class="terminal-1650207396-r2" x="976" y="44.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-1)">
    </text><text class="terminal-1650207396-r2" x="976" y="68.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-2)">
    </text><text class="terminal-1650207396-r2" x="12.2" y="93.2" textLength="366" clip-path="url(#terminal-1650207396-line-3)">This&nbsp;is&nbsp;the&nbsp;callback&nbsp;function.</text><text class="terminal-1650207396-r2" x="976" y="93.2" textLength="12.2" clip-path="url(#terminal-1650207396-line-3)">
    </text><text class="terminal-1650207396-r2" x="976" y="117.6" textLength="12.2" clip-path="url(#terminal-1650207396-line-4)">
    </text><text class="terminal-1650207396-r4" x="0" y="142" textLength="24.4" clip-path="url(#terminal-1650207396-line-5)">╭─</text><text class="terminal-1650207396-r4" x="24.4" y="142" textLength="109.8" clip-path="url(#terminal-1650207396-line-5)">&nbsp;Options&nbsp;</text><text class="terminal-1650207396-r4" x="134.2" y="142" textLength="817.4" clip-path="url(#terminal-1650207396-line-5)">───────────────────────────────────────────────────────────────────</text><text class="terminal-1650207396-r4" x="951.6" y="142" textLength="24.4" clip-path="url(#terminal-1650207396-line-5)">─╮</text><text class="terminal-1650207396-r2" x="976" y="142" textLength="12.2" clip-path="url(#terminal-1650207396-line-5)">
    </text><text class="terminal-1650207396-r4" x="0" y="166.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-6)">│</text><text class="terminal-1650207396-r5" x="24.4" y="166.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-6)">-</text><text class="terminal-1650207396-r5" x="36.6" y="166.4" textLength="73.2" clip-path="url(#terminal-1650207396-line-6)">-flag1</text><text class="terminal-1650207396-r6" x="158.6" y="166.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-6)">-</text><text class="terminal-1650207396-r6" x="170.8" y="166.4" textLength="36.6" clip-path="url(#terminal-1650207396-line-6)">-no</text><text class="terminal-1650207396-r6" x="207.4" y="166.4" textLength="73.2" clip-path="url(#terminal-1650207396-line-6)">-flag1</text><text class="terminal-1650207396-r2" x="353.8" y="166.4" textLength="85.4" clip-path="url(#terminal-1650207396-line-6)">Flag&nbsp;1.</text><text class="terminal-1650207396-r4" x="451.4" y="166.4" textLength="231.8" clip-path="url(#terminal-1650207396-line-6)">[default:&nbsp;no-flag1]</text><text class="terminal-1650207396-r4" x="963.8" y="166.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-6)">│</text><text class="terminal-1650207396-r2" x="976" y="166.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-6)">
    </text><text class="terminal-1650207396-r4" x="0" y="190.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-7)">│</text><text class="terminal-1650207396-r5" x="24.4" y="190.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-7)">-</text><text class="terminal-1650207396-r5" x="36.6" y="190.8" textLength="73.2" clip-path="url(#terminal-1650207396-line-7)">-flag2</text><text class="terminal-1650207396-r6" x="158.6" y="190.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-7)">-</text><text class="terminal-1650207396-r6" x="170.8" y="190.8" textLength="36.6" clip-path="url(#terminal-1650207396-line-7)">-no</text><text class="terminal-1650207396-r6" x="207.4" y="190.8" textLength="73.2" clip-path="url(#terminal-1650207396-line-7)">-flag2</text><text class="terminal-1650207396-r2" x="353.8" y="190.8" textLength="85.4" clip-path="url(#terminal-1650207396-line-7)">Flag&nbsp;2.</text><text class="terminal-1650207396-r4" x="451.4" y="190.8" textLength="231.8" clip-path="url(#terminal-1650207396-line-7)">[default:&nbsp;no-flag2]</text><text class="terminal-1650207396-r4" x="963.8" y="190.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-7)">│</text><text class="terminal-1650207396-r2" x="976" y="190.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-7)">
    </text><text class="terminal-1650207396-r4" x="0" y="215.2" textLength="12.2" clip-path="url(#terminal-1650207396-line-8)">│</text><text class="terminal-1650207396-r5" x="24.4" y="215.2" textLength="12.2" clip-path="url(#terminal-1650207396-line-8)">-</text><text class="terminal-1650207396-r5" x="36.6" y="215.2" textLength="61" clip-path="url(#terminal-1650207396-line-8)">-help</text><text class="terminal-1650207396-r2" x="353.8" y="215.2" textLength="329.4" clip-path="url(#terminal-1650207396-line-8)">Show&nbsp;this&nbsp;message&nbsp;and&nbsp;exit.</text><text class="terminal-1650207396-r4" x="963.8" y="215.2" textLength="12.2" clip-path="url(#terminal-1650207396-line-8)">│</text><text class="terminal-1650207396-r2" x="976" y="215.2" textLength="12.2" clip-path="url(#terminal-1650207396-line-8)">
    </text><text class="terminal-1650207396-r4" x="0" y="239.6" textLength="976" clip-path="url(#terminal-1650207396-line-9)">╰──────────────────────────────────────────────────────────────────────────────╯</text><text class="terminal-1650207396-r2" x="976" y="239.6" textLength="12.2" clip-path="url(#terminal-1650207396-line-9)">
    </text><text class="terminal-1650207396-r4" x="0" y="264" textLength="24.4" clip-path="url(#terminal-1650207396-line-10)">╭─</text><text class="terminal-1650207396-r4" x="24.4" y="264" textLength="122" clip-path="url(#terminal-1650207396-line-10)">&nbsp;Commands&nbsp;</text><text class="terminal-1650207396-r4" x="146.4" y="264" textLength="805.2" clip-path="url(#terminal-1650207396-line-10)">──────────────────────────────────────────────────────────────────</text><text class="terminal-1650207396-r4" x="951.6" y="264" textLength="24.4" clip-path="url(#terminal-1650207396-line-10)">─╮</text><text class="terminal-1650207396-r2" x="976" y="264" textLength="12.2" clip-path="url(#terminal-1650207396-line-10)">
    </text><text class="terminal-1650207396-r4" x="0" y="288.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-11)">│</text><text class="terminal-1650207396-r5" x="24.4" y="288.4" textLength="122" clip-path="url(#terminal-1650207396-line-11)">bar&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</text><text class="terminal-1650207396-r2" x="170.8" y="288.4" textLength="780.8" clip-path="url(#terminal-1650207396-line-11)">This&nbsp;is&nbsp;the&nbsp;bar&nbsp;command.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</text><text class="terminal-1650207396-r4" x="963.8" y="288.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-11)">│</text><text class="terminal-1650207396-r2" x="976" y="288.4" textLength="12.2" clip-path="url(#terminal-1650207396-line-11)">
    </text><text class="terminal-1650207396-r4" x="0" y="312.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-12)">│</text><text class="terminal-1650207396-r5" x="24.4" y="312.8" textLength="122" clip-path="url(#terminal-1650207396-line-12)">foo&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</text><text class="terminal-1650207396-r2" x="170.8" y="312.8" textLength="780.8" clip-path="url(#terminal-1650207396-line-12)">This&nbsp;is&nbsp;the&nbsp;foo&nbsp;command.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</text><text class="terminal-1650207396-r4" x="963.8" y="312.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-12)">│</text><text class="terminal-1650207396-r2" x="976" y="312.8" textLength="12.2" clip-path="url(#terminal-1650207396-line-12)">
    </text><text class="terminal-1650207396-r4" x="0" y="337.2" textLength="976" clip-path="url(#terminal-1650207396-line-13)">╰──────────────────────────────────────────────────────────────────────────────╯</text><text class="terminal-1650207396-r2" x="976" y="337.2" textLength="12.2" clip-path="url(#terminal-1650207396-line-13)">
    </text>
        </g>
        </g>
    </svg>

|

Or to text:

.. raw:: html

    <pre><span></span>                                                                                             
    Usage: example [OPTIONS] COMMAND [ARGS]...                                                  
                                                                                                
    This is the callback function.                                                              
                                                                                                
    ╭─ Options ─────────────────────────────────────────────────────────────────────────────────╮
    │ --flag1    --no-flag1      Flag 1. [default: no-flag1]                                    │
    │ --flag2    --no-flag2      Flag 2. [default: no-flag2]                                    │
    │ --help                     Show this message and exit.                                    │
    ╰───────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ────────────────────────────────────────────────────────────────────────────────╮
    │ bar           This is the bar command.                                                    │
    │ foo           This is the foo command.                                                    │
    ╰───────────────────────────────────────────────────────────────────────────────────────────╯
    </pre>


The ``typer`` directive has options for generating docs for all subcommands as well
and optionally generating independent sections for each. There are also mechanisms
for passing options to the underlying console and svg generation functions. See the
official documentation for more information.
