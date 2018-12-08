``iterfzf``: Pythonic interface to ``fzf``
==========================================

.. image:: https://badge.fury.io/py/iterfzf.svg
   :target: https://pypi.python.org/pypi/iterfzf
   :alt: Latest PyPI version

.. image:: https://travis-ci.org/dahlia/iterfzf.svg
   :alt: Build status (Travis CI)
   :target: https://travis-ci.org/dahlia/iterfzf

.. image:: https://ci.appveyor.com/api/projects/status/cf2eiuymdffvybl7?svg=true
   :target: https://ci.appveyor.com/project/dahlia/iterfzf
   :alt: Build status (AppVeyor)


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
- Supports Python 2.7, 3.4 or higher.

__ https://github.com/dahlia/iterfzf/releases


.. _api reference:

``iterfzf.iterfzf(iterable, **options)``
----------------------------------------

Consumes the given ``iterable`` of strings, and displays them using ``fzf``.
If a user chooses something it immediately returns the chosen things.

The following is the full list of parameters.  Please pass them as
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

``multi``
   ``True`` to let the user to choose more than one.  A user can select
   items with tab/shift-tab.  If ``multi=True`` the function returns a list of
   strings rather than a string.

   ``False`` to make a user possible to choose only one.  If ``multi=False``
   it returns a string rather than a list.

   For both modes, the function returns ``None`` if nothing is matched or
   a user cancelled.

   ``False`` by default.

   Corresponds to ``-m``/``--multi`` option.

``print_query``
   If ``True`` the return type is a tuple where the first element is the query
   the user actually typed, and the second element is the selected output as
   described above and depending on the state of ``multi``.

   ``False`` by default.

   Corresponds to ``--print-query`` option.

   *New in version 0.3.0.*

``encoding``
   The text encoding name (e.g. ``'utf-8'``, ``'ascii'``) to be used for
   encoding ``iterable`` values and decoding return values.  It's ignored
   when the ``iterable`` values are byte strings.

   The Python's default encoding (i.e. ``sys.getdefaultencoding()``) is used
   by default.

``extended``
   ``True`` for extended-search mode.  ``False`` to turn it off.

   ``True`` by default.

   ``True`` corresponds to ``-x``/``--extended`` option, and
   ``False`` corresponds to ``+x``/``--no-extended`` option.

``exact``
   ``False`` for fuzzy matching, and ``True`` for exact matching.

   ``False`` by default.

   Corresponds to ``-e``/``--exact`` option.

``case_sensitive``
   ``True`` for case sensitivity, and ``False`` for case insensitivity.
   ``None``, the default, for smart-case match.

   ``True`` corresponds to ``+i`` option and ``False`` corresponds to
   ``-i`` option.

``query``
   The query string to be filled at first.  (It can be removed by a user.)

   Empty string by default.

   Corresponds to ``-q``/``--query`` option.

``prompt``
   The prompt sequence.  ``' >'`` by default.

   Corresponds to ``--prompt`` option.

``mouse``
   ``False`` to disable mouse.  ``True`` by default.

   Corresponds to ``--no-mouse`` option.


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


Version 0.5.0.17.3
~~~~~~~~~~~~~~~~~~

To be released.  Bundles ``fzf`` 0.17.5.

- Dropped Python 2.6 and 3.3 supports.
- Officially support Python 3.7 (it anyway had worked though).
- Marked the package as supporting type checking by following `PEP 561`_.

.. _PEP 561: https://www.python.org/dev/peps/pep-0561/


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
