# `mkbak-iterfzf`: Pythonic interface to `fzf`

[![Latest PyPI version](https://badge.fury.io/py/iterfzf.svg)](https://pypi.python.org/pypi/iterfzf)

[![Build status (Travis CI)](https://travis-ci.org/dahlia/iterfzf.svg)](https://travis-ci.org/dahlia/iterfzf)

[![Build status (AppVeyor)](https://ci.appveyor.com/api/projects/status/cf2eiuymdffvybl7?svg=true)](https://ci.appveyor.com/project/dahlia/iterfzf)

## `mkbak-iterfzf` is a fork of [iterfzf](https://github.com/dahlia/iterfzf/releases)

All credit goes to [dahlia](https://hongminhee.org/), all I did was add the
`--height` option

## Demo session

[![iterfzf demo session](https://asciinema.org/a/121028.png)](https://asciinema.org/a/121028)

See also the [API reference](#api reference).

## Key features

- No dependency but only Python is required. Prebuilt `fzf` binary for
    each platform is bundled into wheels. Everything is ready by
    `pip install iterfzf`. (Note that not wheels of all supported
    platforms are uploaded to PyPI as they don't allow minor platforms
    e.g. FreeBSD. The complete wheels can be found from the [GitHub
    releases](https://junegunn.kr/).)
- Consumes an iterable rather than a list. It makes UX way better when
    the input data is long but *streamed* from low latency network. It
    can begin to display items immediately after only *part* of items
    are ready, and *before* the complete items are ready.
- Supports Python 2.7, 3.5 or higher.

## `iterfzf.iterfzf(iterable, **options)`

Consumes the given `iterable` of strings, and displays them using `fzf`.
If a user chooses something it immediately returns the chosen things.

The following is the full list of parameters. Please pass them as
**keyword arguments** except for `iterable` which comes first:

`iterable` (required)  
The only required parameter. Every element which this `iterable` yields
is displayed immediately after each one is produced. In other words, the
passed `iterable` is lazily consumed.

It can be an iterable of byte strings (e.g. `[b'foo', b'bar']`) or of
Unicode strings (e.g. `[u'foo', u'bar']`), but must not be mixed (e.g.
`[u'foo', b'bar']`). If they are byte strings the function returns
bytes. If they are Unicode strings it returns Unicode strings. See also
the `encoding` parameter.

`multi`  
`True` to let the user to choose more than one. A user can select items
with tab/shift-tab. If `multi=True` the function returns a list of
strings rather than a string.

`False` to make a user possible to choose only one. If `multi=False` it
returns a string rather than a list.

For both modes, the function returns `None` if nothing is matched or a
user cancelled.

`False` by default.

Corresponds to `-m`/`--multi` option.

`print_query`  
If `True` the return type is a tuple where the first element is the
query the user actually typed, and the second element is the selected
output as described above and depending on the state of `multi`.

`False` by default.

Corresponds to `--print-query` option.

*New in version 0.3.0.*

`encoding`  
The text encoding name (e.g. `'utf-8'`, `'ascii'`) to be used for
encoding `iterable` values and decoding return values. It's ignored when
the `iterable` values are byte strings.

The Python's default encoding (i.e. `sys.getdefaultencoding()`) is used
by default.

`extended`  
`True` for extended-search mode. `False` to turn it off.

`True` by default.

`True` corresponds to `-x`/`--extended` option, and `False` corresponds
to `+x`/`--no-extended` option.

`exact`  
`False` for fuzzy matching, and `True` for exact matching.

`False` by default.

Corresponds to `-e`/`--exact` option.

`case_sensitive`  
`True` for case sensitivity, and `False` for case insensitivity. `None`,
the default, for smart-case match.

`True` corresponds to `+i` option and `False` corresponds to `-i`
option.

`query`  
The query string to be filled at first. (It can be removed by a user.)

Empty string by default.

Corresponds to `-q`/`--query` option.

`height`  
Set the height of the prompt. `'100%'` by default.

Corresponds to `--height` option.

`prompt`  
The prompt sequence. `' >'` by default.

Corresponds to `--prompt` option.

`preview`  
The preview command to execute. `None` by default.

Corresponds to `--preview` option.

`mouse`  
`False` to disable mouse. `True` by default.

Corresponds to `--no-mouse` option.

`ansi`  
`True` to enable ansi colors mode. `None` by default.

Corresponds to `--ansi` option.

## Author and license

The `iterfzf` library is written by [Hong
Minhee](https://github.com/dahlia/iterfzf/pull/6) and distributed under
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html) or later.

The `fzf` program is written by [Junegunn
Choi](https://github.com/dahlia/iterfzf/pull/3) and distributed under
MIT license.

## Changelog

### Versioning scheme

Note that `mkbak-iterfzf` does *not* follow [Semantic
Versioning](http://semver.org/). The version consists of its own major
and minor number followed by the version of bundled `fzf`. For example,
1.2.3.4.5.6 means that `iterfzf`'s own major version is 1, and its own
minor version is 2, its on patch 3, plus the version of `fzf` it bundles is 4.5.6.

``` text
/---------- 1. iterfzf's major version
|     /------ 4. bundled fzf's major version
|     |   /-- 6. bundled fzf's patch version
|     |   |
v     v   v
1.2.3.4.5.6
  ^ ^   ^
  | |   |
  | |   \---- 5. bundled fzf's minor version
  | |
  | \-------3. mkbak-iterfzf's patch version
  \-------- 2. iterfzf's minor version
```

### Version 0.6.0.20.0

To be released. Bundles `fzf` 0.20.0.

Added `ansi` option. \[[#16](https://github.com/dahlia/iterfzf/pull/16) by Erik Lilja\]

### Version 0.5.0.20.0

Released on February 9, 2020. Bundles `fzf` 0.20.0.

- Dropped Python 2.6, 3.3, and 3.4 supports.
- Officially support Python 3.7 (it anyway had worked though).
- Marked the package as supporting type checking by following [PEP
    561](https://www.python.org/dev/peps/pep-0561/).
- Added `preview` option.
    \[[\#6](https://github.com/dahlia/iterfzf/pull/1) by Marc
    Weistroff\]
- Fixed a bug which had raised `IOError` by selecting an option before
    finished to load all options on Windows. \[#3 by Jeff Rimko\]

### Version 0.4.0.17.3

Released on December 4, 2017. Bundles `fzf` 0.17.3.

### Version 0.4.0.17.1

Released on October 19, 2017. Bundles `fzf` 0.17.1.

- Added missing binary wheels for macOS again. (These were missing
    from 0.3.0.17.1, the previous release.)

### Version 0.3.0.17.1

Released on October 16, 2017. Bundles `fzf` 0.17.1.

- Added `print_query` option. \[[#1](https://github.com/dahlia/iterfzf/pull/1)
by George Kettleborough\]

### Version 0.2.0.17.0

Released on August 27, 2017. Bundles `fzf` 0.17.0.

### Version 0.2.0.16.11

Released on July 23, 2017. Bundles `fzf` 0.16.11.

### Version 0.2.0.16.10

Released on July 23, 2017. Bundles `fzf` 0.16.10.

### Version 0.2.0.16.8

Released on June 6, 2017. Bundles `fzf` 0.16.8.

- Upgraded `fzf` from 0.16.7 to 0.16.8.

### Version 0.2.0.16.7

Released on May 20, 2017. Bundles `fzf` 0.16.7.

- Made sdists (source distributions) possible to be correctly
    installed so that older `pip`, can't deal with wheels, also can
    install `iterfzf`.

### Version 0.1.0.16.7

Released on May 19, 2017. Bundles `fzf` 0.16.7. The initial release.
