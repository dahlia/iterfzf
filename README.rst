``iterfzf``: Pythonic interface to ``fzf``
==========================================

.. image:: https://img.shields.io/pypi/v/iterfzf
   :target: https://pypi.org/project/iterfzf/
   :alt: Latest PyPI version

.. image:: https://github.com/dahlia/iterfzf/actions/workflows/test.yaml/badge.svg
   :alt: Build status (GitHub Actions)
   :target: https://github.com/dahlia/iterfzf/actions/workflows/test.yaml


Demo session
------------

.. image:: https://asciinema.org/a/121028.png
   :target: https://asciinema.org/a/121028
   :alt: iterfzf demo session

See also the `API reference`_.


Key features
------------

- No dependency but only Python is required.  Prebuilt ``fzf`` binary for
  each platform is bundled into wheels.  Everything is ready by
  ``pip install iterfzf``.  (Note that not wheels of all supported platforms
  are uploaded to PyPI as they don't allow minor platforms e.g. FreeBSD.
  The complete wheels can be found from the `GitHub releases`__.)
- Consumes an iterable rather than a list.  It makes UX way better when the
  input data is long but *streamed* from low latency network.
  It can begin to display items immediately after only *part* of items are
  ready, and *before* the complete items are ready.
- Supports Python 3.8 or higher.

__ https://github.com/dahlia/iterfzf/releases


.. _api reference:

``iterfzf.iterfzf(iterable, *, **options)``
-------------------------------------------

Consumes the given ``iterable`` of strings, and displays them using ``fzf``.
If a user chooses something it immediately returns the chosen things. If the
user cancels the selection, the `KeywordInterrupt` exception will be raised.

The following is the full list of parameters.  Pass them as
**keyword arguments** except for ``iterable`` which comes first:

``iterable`` (required)
   The only required parameter.  Every element which this ``iterable`` yields
   is displayed immediately after each one is produced.  In other words,
   the passed ``iterable`` is lazily consumed.

   It can be an iterable of byte strings (e.g. ``[b'foo', b'bar']``) or of
   Unicode strings (e.g. ``[u'foo', u'bar']``), but must not be
   mixed (e.g. ``[u'foo', b'bar']``).  If they are byte strings the function
   returns bytes.  If they are Unicode strings it returns Unicode strings.
   See also the ``encoding`` parameter.

.. list-table:: Keyword arguments
   :widths: 12 12 12 50
   :header-rows: 1

   * - Keyword
     - Default
     - CLI option
     - Description
   * - ``ansi``
     - ``None``
     - ``--ansi``
     - ``True`` to enable ansi colors mode.

       *New in version 1.0.0.*
   * - ``bind``
     -
     - ``--bind``
     - The key/event bindings to pass to ``fzf``.

       Dictionary of the form {KEY: ACTION} or {EVENT: ACTION}.

       *New in version 1.4.0.*
   * - ``case_sensitive``
     - ``None``
     - ``--smart-case``
     - ``True`` for case sensitivity, and ``False`` for case insensitivity.
       ``None``, the default, for smart-case match.

       ``True`` corresponds to ``+i`` option and ``False`` corresponds to
       ``-i`` option.
   * - ``color``
     - ``None``
     - ``--color``
     - Accepts color scheme name or a dictionary in the form of {element:
       color}.

       *New in version 1.6.0.*
   * - ``cycle``
     - ``False``
     - ``--cycle``
     - ``True`` to enable cycling scrolling.

       *New in version 1.1.0.*
   * - ``encoding``
     - ``sys.getdefaultencoding()``
     - ``--encoding``
     - The text encoding name (e.g. ``'utf-8'``, ``'ascii'``) to be used for
       encoding ``iterable`` values and decoding return values.  It's ignored
       when the ``iterable`` values are byte strings.
   * - ``exact``
     - ``False``
     - ``--exact``
     - ``False`` for fuzzy matching, and ``True`` for exact matching.
   * - ``extended``
     - ``True``
     - ``--extended``
       ``--no-extended``
     - ``True`` for extended-search mode.  ``False`` to turn it off.

       ``True`` corresponds to ``-x``/``--extended`` option, and
       ``False`` corresponds to ``+x``/``--no-extended`` option.
   * - ``header``
     - ``None``
     - ``--header``
     - Sticky header printed below prompt.

       *New in version 1.6.0.*
   * - ``mouse``
     - ``True``
     - ``--no-mouse``
     -  ``False`` to disable mouse.
   * - ``multi``
     - ``False``
     - ``--multi``
     - ``True`` to let the user to choose more than one.  A user can select
       items with tab/shift-tab.  If ``multi=True`` the function returns a list of
       strings rather than a string.

       ``False`` to make a user possible to choose only one.  If ``multi=False``
       it returns a string rather than a list.

       For both modes, the function returns ``None`` if nothing is matched.
   * - ``preview``
     - ``None``
     - ``--preview``
     - *New in version 0.5.0.*
   * - ``print_query``
     - ``False``
     - ``--print-query``
     - If ``True`` the return type is a tuple where the first element is the query
       the user actually typed, and the second element is the selected output as
       described above and depending on the state of ``multi``.

       *New in version 0.3.0.*
   * - ``prompt``
     - ``" >"``
     - ``--prompt``
     -
   * - ``query``
     - ``""`` (empty string)
     - ``--query``
     - The query string to be filled at first.  (It can be removed by a user.)
   * - ``sort``
     - ``False``
     - ``--sort``
     - Sorts the result if ``True``.  ``False`` by default.

       *New in version 1.3.0.*
   * - ``tmux``
     - ``False``
     - ``--tmux[=OPTS]``
     - Start fzf in a tmux popup if ``tmux=True`` or the config string is
       provided (requires tmux 3.3+).

       The format of the option is like
       ``[center|top|bottom|left|right][,SIZE[%]][,SIZE[%]][,border-native]``
       (default: ``center,50%``).

       *New in version 1.7.0.*
   * - ``__extra__``
     - ``[]``
     -
     - The iterable of extra raw options/arguments to pass to ``fzf``.

       This is how you pass extra options that are not already defined
       as keyword arguments.

       *New in version 1.1.0.*


Author and license
------------------

The ``iterfzf`` library is written by `Hong Minhee`__ and distributed under
GPLv3_ or later.

The ``fzf`` program is written by `Junegunn Choi`__ and distributed under
MIT license.

__ https://hongminhee.org/
.. _GPLv3: https://www.gnu.org/licenses/gpl-3.0.html
__ https://junegunn.kr/


Changelog
---------

Versioning scheme
~~~~~~~~~~~~~~~~~

Note that ``iterfzf`` does *not* follow `Semantic Versioning`_.  The version
consists of its own major and minor number followed by the version of bundled
``fzf``.  For example, 1.2.3.4.5 means that ``iterfzf``'s own major version
is 1, and its own minor version is 2, plus the version of ``fzf`` it bundles
is 3.4.5.

.. code-block:: text

   /---------- 1. iterfzf's major version
   |   /------ 3. bundled fzf's major version
   |   |   /-- 5. bundled fzf's patch version
   |   |   |
   v   v   v
   1.2.3.4.5
     ^   ^
     |   |
     |   \---- 4. bundled fzf's minor version
     \-------- 2. iterfzf's minor version

.. _Semantic Versioning: http://semver.org/


Version 1.9.0.62.0
~~~~~~~~~~~~~~~~~~

To be released.   Bundles ``fzf`` `0.62.0`__.

__ https://github.com/junegunn/fzf/releases/tag/v0.62.0


Version 1.8.0.62.0
~~~~~~~~~~~~~~~~~~

Released on May 15, 2025.  Bundles ``fzf`` `0.62.0`__.

- Fixed an error when the ``iterfzf()`` function was invoked with
  the ``tmux=True`` option. [`#45`__ by Peter Rebrun]

__ https://github.com/junegunn/fzf/releases/tag/v0.62.0
__ https://github.com/dahlia/iterfzf/pull/45


Version 1.7.0.62.0
~~~~~~~~~~~~~~~~~~

Released on May 10, 2025.  Bundles ``fzf`` `0.62.0`__.

- Added ``tmux`` option.  [`#44`__ by Peter Rebrun]

__ https://github.com/junegunn/fzf/releases/tag/v0.62.0
__ https://github.com/dahlia/iterfzf/pull/44


Version 1.6.0.60.3
~~~~~~~~~~~~~~~~~~

Released on March 11, 2025.  Bundles ``fzf`` `0.60.3`__.

- Added ``header`` option.  [`#42`__ by Phred Lane]
- Added ``color`` option.  [`#43`__ by Phred Lane]

__ https://github.com/junegunn/fzf/releases/tag/v0.60.3
__ https://github.com/dahlia/iterfzf/pull/42
__ https://github.com/dahlia/iterfzf/pull/43


Version 1.5.0.60.2
~~~~~~~~~~~~~~~~~~

Released on March 5, 2025.  Bundles ``fzf`` `0.60.2`__.

- Added support for raising ``KeyboardInterrupt``.  [`#40`__ by Phred Lane]
- Officially support Python 3.13.

__ https://github.com/junegunn/fzf/releases/tag/v0.60.2
__ https://github.com/dahlia/iterfzf/pull/40


Version 1.4.0.60.2
~~~~~~~~~~~~~~~~~~

Released on March 1, 2025.  Bundles ``fzf`` `0.60.2`__.

__ https://github.com/junegunn/fzf/releases/tag/v0.60.2


Version 1.4.0.54.3
~~~~~~~~~~~~~~~~~~

Released on August 24, 2024.  Bundles ``fzf`` `0.54.3`__.

__ https://github.com/junegunn/fzf/releases/tag/v0.54.3


Version 1.4.0.51.0
~~~~~~~~~~~~~~~~~~

Released on May 7, 2024.  Bundles ``fzf`` `0.51.0`__.

- Added ``bind`` option. [`#21`__, `#36`__ by Gregory.K]

__ https://github.com/junegunn/fzf/releases/tag/0.51.0
__ https://github.com/dahlia/iterfzf/issues/21
__ https://github.com/dahlia/iterfzf/pull/36


Version 1.3.0.51.0
~~~~~~~~~~~~~~~~~~

Released on May 6, 2024.  Bundles ``fzf`` `0.51.0`__.

- Added ``sort`` option.  [`#18`__, `#35`__ by Gregory.K]
- Officially support Python 3.12.

__ https://github.com/junegunn/fzf/releases/tag/0.51.0
__ https://github.com/dahlia/iterfzf/issues/18
__ https://github.com/dahlia/iterfzf/pull/35


Version 1.2.0.46.1
~~~~~~~~~~~~~~~~~~

Released on March 6, 2024.  Bundles ``fzf`` `0.46.1`__.

- Close stdin before waiting to allow ``--select-1`` to work.
  [`#34`__ by Alex Wood]

__ https://github.com/junegunn/fzf/releases/tag/0.46.1
__ https://github.com/dahlia/iterfzf/pull/34


Version 1.1.0.44.0
~~~~~~~~~~~~~~~~~~

Released on November 18, 2023.  Bundles ``fzf`` `0.44.0`__.

- Added ``cycle`` option.  [`#33`__ by Daniele Trifirò]
- Added ``__extra__`` option.  [`#32`__]

__ https://github.com/junegunn/fzf/releases/tag/0.44.0
__ https://github.com/dahlia/iterfzf/pull/33
__ https://github.com/dahlia/iterfzf/issues/32


Version 1.0.0.42.0
~~~~~~~~~~~~~~~~~~

Released on September 18, 2023.  Bundles ``fzf`` `0.42.0`__.

- Dropped Python 2.7, 3.5, 3.6, and 3.7 supports.
- Officially support Python 3.8, 3.9, 3.10, and 3.11.
- Dropped FreeBSD i386, Linux i686, Linux armv8l, OpenBSD i386, and Windows
  32-bit supports as fzf no longer supports them.
- Dropped OpenBSD amd64 support.
- Except the first parameter ``iterable``, all parameters are enforced to be
  keyword-only.  (Note that it's always been the recommended way to pass
  options, although it was not enforced.)
- Added ``ansi`` option.  [`#16`__ by Erik Lilja]
- The ``executable`` parameter now takes ``os.PathLike`` instead of ``str``,
  which is backward compatible.
- Added ``__version__`` and ``__fzf_version__`` attributes to the module.
- Added ``POSIX_EXECUTABLE_NAME`` and ``WINDOWS_EXECUTABLE_NAME`` attributes
  to the module.
- Module attribute ``EXECUTABLE_NAME`` is now a ``Literal['fzf', 'fzf.exe']``
  type, which is backward compatible with the previous ``str`` type.
- Module attribute ``BUNDLED_EXECUTABLE`` is now ``Optional[pathlib.Path]``
  type.

__ https://github.com/junegunn/fzf/releases/tag/0.42.0
__ https://github.com/dahlia/iterfzf/pull/16


Version 0.5.0.20.0
~~~~~~~~~~~~~~~~~~

Released on February 9, 2020.  Bundles ``fzf`` 0.20.0.

- Dropped Python 2.6, 3.3, and 3.4 supports.
- Officially support Python 3.7 (it anyway had worked though).
- Marked the package as supporting type checking by following `PEP 561`_.
- Added ``preview`` option.  [`#6`__ by Marc Weistroff]
- Fixed a bug which had raised ``IOError`` by selecting an option before
  finished to load all options on Windows.  [`#3`__ by Jeff Rimko]

.. _PEP 561: https://www.python.org/dev/peps/pep-0561/
__ https://github.com/dahlia/iterfzf/pull/6
__ https://github.com/dahlia/iterfzf/pull/3


Version 0.4.0.17.3
~~~~~~~~~~~~~~~~~~

Released on December 4, 2017.  Bundles ``fzf`` 0.17.3.


Version 0.4.0.17.1
~~~~~~~~~~~~~~~~~~

Released on October 19, 2017.  Bundles ``fzf`` 0.17.1.

- Added missing binary wheels for macOS again.  (These were missing from
  0.3.0.17.1, the previous release.)


Version 0.3.0.17.1
~~~~~~~~~~~~~~~~~~

Released on October 16, 2017.  Bundles ``fzf`` 0.17.1.

- Added ``print_query`` option.  [`#1`__ by George Kettleborough]

__ https://github.com/dahlia/iterfzf/pull/1


Version 0.2.0.17.0
~~~~~~~~~~~~~~~~~~

Released on August 27, 2017.  Bundles ``fzf`` 0.17.0.


Version 0.2.0.16.11
~~~~~~~~~~~~~~~~~~~

Released on July 23, 2017.  Bundles ``fzf`` 0.16.11.


Version 0.2.0.16.10
~~~~~~~~~~~~~~~~~~~

Released on July 23, 2017.  Bundles ``fzf`` 0.16.10.


Version 0.2.0.16.8
~~~~~~~~~~~~~~~~~~

Released on June 6, 2017.  Bundles ``fzf`` 0.16.8.

- Upgraded ``fzf`` from 0.16.7 to 0.16.8.


Version 0.2.0.16.7
~~~~~~~~~~~~~~~~~~

Released on May 20, 2017.  Bundles ``fzf`` 0.16.7.

- Made sdists (source distributions) possible to be correctly installed
  so that older ``pip``, can't deal with wheels, also can install ``iterfzf``.


Version 0.1.0.16.7
~~~~~~~~~~~~~~~~~~

Released on May 19, 2017.  Bundles ``fzf`` 0.16.7.  The initial release.
