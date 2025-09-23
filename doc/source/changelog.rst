.. include:: ./refs.rst

==========
Change Log
==========

v0.6.0 (2025-09-22)
===================

* Implemented `Use intersphinx for better integration with the sphinx ecosystem <https://github.com/sphinx-contrib/typer/issues/51>`_
* Implemented `Support python 3.14. <https://github.com/sphinx-contrib/typer/issues/50>`_
* Implemented `Switch from poetry to uv. <https://github.com/sphinx-contrib/typer/issues/48>`_

v0.5.1 (2024-10-14)
===================

* Fixed `Spaces in image filenames can cause problems with pdf builds. <https://github.com/sphinx-contrib/typer/issues/46>`_

v0.5.0 (2024-08-24)
===================

* Implemented `Support Sphinx 8 <https://github.com/sphinx-contrib/typer/issues/45>`_
* Implemented `Support Python 3.13 <https://github.com/sphinx-contrib/typer/issues/44>`_
* Fixed `typer 0.12.5+ breaks click compatibility <https://github.com/sphinx-contrib/typer/issues/43>`_

v0.4.2 (2024-08-22)
====================

* Fixed `:typer: role default link text has colon where space expected <https://github.com/sphinx-contrib/typer/issues/42>`_
* Fixed `:typer: role does not allow link text <https://github.com/sphinx-contrib/typer/issues/41>`_

v0.4.1 (2024-08-22)
====================

* Fixed `:typer: role does not work if processed before the definition. <https://github.com/sphinx-contrib/typer/issues/40>`_
* Fixed `:typer: role link text does not reflect the actual command invocation. <https://github.com/sphinx-contrib/typer/issues/39>`_

v0.4.0 (2024-08-19)
====================

* Implemented `Use builtin sphinx cache to cache iframe heights instead of custom file. <https://github.com/sphinx-contrib/typer/issues/38>`_
* Implemented `Allow cross-referencing <https://github.com/sphinx-contrib/typer/issues/34>`_

v0.3.5 (2024-08-17)
====================

* Fixed `Lazily loaded commands throw an exception. <https://github.com/sphinx-contrib/typer/issues/37>`_
* Fixed `Changes are not detected across sphinx-build <https://github.com/sphinx-contrib/typer/issues/35>`_

v0.3.4 (2024-08-15)
====================

* Fixed `list_commands order should be honored when generated nested sections for subcommands. <https://github.com/sphinx-contrib/typer/issues/36>`_

v0.3.3 (2024-07-15)
====================

* Removed errant deepcopy introduced in last release.

v0.3.2 (yanked)
===============

* Implemented `Add blue waves theme. <https://github.com/sphinx-contrib/typer/issues/31>`_
* Implemented `Add red sands theme. <https://github.com/sphinx-contrib/typer/issues/30>`_

v0.3.1 (2024-06-11)
====================

* Fixed `ruff dependency should be dev dependency only. <https://github.com/sphinx-contrib/typer/issues/29>`_

v0.3.0 (2024-06-01)
====================

* Implemented `Allow function hooks to be specified as import strings. <https://github.com/sphinx-contrib/typer/issues/28>`_
* Fixed `pdf builds are broken. <https://github.com/sphinx-contrib/typer/issues/27>`_


v0.2.5 (2024-05-29)
====================

* Fixed `Proxied Typer object check is broken. <https://github.com/sphinx-contrib/typer/issues/26>`_

v0.2.4 (2024-05-29)
====================

* Fixed `Support more flexible duck typing for detecting Typer objects <https://github.com/sphinx-contrib/typer/issues/25>`_

v0.2.3 (2024-05-22)
====================

* Fixed `when :prog: is supplied and a subcommand help is generated the usage string includes incorrect prefix to prog <https://github.com/sphinx-contrib/typer/issues/24>`_

v0.2.2 (2024-05-14)
====================

* Fixed `Move to ruff for tooling <https://github.com/sphinx-contrib/typer/issues/22>`_
* Fixed `Fix WARNING: cannot cache unpickable configuration value <https://github.com/sphinx-contrib/typer/issues/21>`_

v0.2.1 (2024-04-11)
====================

* Implemented `Convert README and CONTRIBUTING to markdown. <https://github.com/sphinx-contrib/typer/issues/20>`_
* Fixed `typer-slim[all] no longer works to bring in rich <https://github.com/sphinx-contrib/typer/issues/19>`_

v0.2.0 (2024-04-03)
====================

* Fixed `typer 0.12.0 package split breaks upgrades. <https://github.com/sphinx-contrib/typer/issues/18>`_

v0.1.12 (2024-03-05)
=====================

* Fixed `Typer with sphinx-autobuild going on infinite loop <https://github.com/sphinx-contrib/typer/issues/17>`_

v0.1.11 (2024-02-22)
=====================

* Fixed `Typer dependency erroneously downgraded. <https://github.com/sphinx-contrib/typer/issues/15>`_

v0.1.10 (2024-02-21)
=====================

* Fixed `Pillow version not specified for png optional dependency. <https://github.com/sphinx-contrib/typer/issues/14>`_

v0.1.9 (2024-02-21)
====================

* Fixed `Some dependencies have unnecessarily recent version requirements. <https://github.com/sphinx-contrib/typer/issues/13>`_

v0.1.8 (2024-02-20)
====================

* Fixed `When using convert-png sometimes the pngs images are cutoff too short. <https://github.com/sphinx-contrib/typer/issues/12>`_

v0.1.7 (2024-01-31)
====================

* Fixed reopened issue: `nested class attribute import paths for typer apps are broken. <https://github.com/sphinx-contrib/typer/issues/11>`_

v0.1.6 (2024-01-31)
====================

* Fixed `nested class attribute import paths for typer apps are broken. <https://github.com/sphinx-contrib/typer/issues/11>`_


v0.1.5 (2024-01-30)
====================

* Fixed `When the sphinx app is an attribute on a class the import fails. <https://github.com/sphinx-contrib/typer/issues/10>`_

v0.1.4 (2023-12-21)
====================

* Meta data updated reflecting repository move into the sphinx-contrib organization.

v0.1.3 (2023-12-19)
====================

* Fixed repository location in package meta data.

v0.1.2 (2023-12-19)
====================

* Try big 4 web browser managers before giving up when :pypi:`selenium` features are used.
* Fixed pypi.org rendering of the readme, and rtd documentation build.

v0.1.1 (2023-12-19)
====================

* Fixed pypi.org rendering of the readme.

v0.1.0 (2023-12-19)
====================

* Initial Release
