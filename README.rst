``iterfzf``: Pythonic interface to ``fzf``
==========================================

Supports Python 2.6, 2.7, 3.3 or higher.


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
   ``True`` to make a user possible to choose more than one.  A user can select
   items with tab/shift-tab.  If ``multi=True`` the function returns a list of
   strings rather than a string.

   ``False`` to make a user possible to choose only one.  If ``multi=False``
   it returns a string rather than a list.

   For both modes, the function returns ``None`` if nothing is matched or
   a user cancelled.

   ``False`` by default.

   Corresponds to ``-m``/``--multi`` option.

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
