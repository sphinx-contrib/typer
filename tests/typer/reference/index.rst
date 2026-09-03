Reference Tests
---------------

This tests that references to commands like :typer:`python -m cli-ref.py` work. You can also use
a section id style reference: :typer:`python-m-cli-ref-py`. You can also use link text: 
:typer:`command <python -m cli-ref.py>`.

Commands rendered without :make-sections: are also referenceable: :typer:`noref`
and :typer:`no-sections <noref>`.

The any role also resolves commands: :any:`python-m-cli-ref-py`.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   reference
   nosections
