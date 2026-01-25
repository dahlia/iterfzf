AGENTS.md
=========

Project Overview
----------------

`iterfzf` is a Pythonic interface to `fzf` (command-line fuzzy finder). It is a
pure Python library with zero runtime dependencies that bundles a prebuilt `fzf`
binary into platform-specific wheels. The core logic lives in a single module:
`iterfzf/__init__.py`. The custom PEP 517 build backend in `build_dist.py`
downloads and bundles the `fzf` binary from GitHub Releases.

License: GPLv3+. Python 3.8+.


Build System
------------

 -  **Build backend**: Custom PEP 517 backend (`build_dist.py`) wrapping `flit_core`
 -  **Build deps**: `flit_core >= 3.2, < 4` and `packaging >= 22`
 -  **Version**: Dynamic, derived from `__version__` in `iterfzf/__init__.py`
 -  **No Makefile, setup.py, or requirements.txt**

### Install for development (editable)

~~~~ sh
pip install -e .
~~~~

This triggers `build_dist.py` which downloads the `fzf` binary for the current
platform. Set `GITHUB_TOKEN` env var to avoid GitHub API rate limits.


Testing
-------

### Framework

Tests use Python's built-in `unittest` module (not pytest).

### Test file

`iterfzf/test_iterfzf.py` — contains `IterFzfTest(unittest.TestCase)` with
unit tests that use `unittest.mock` to patch `subprocess.Popen`.

### Running all tests

~~~~ sh
python -m unittest iterfzf.test_iterfzf
~~~~

### Running a single test

~~~~ sh
python -m unittest iterfzf.test_iterfzf.IterFzfTest.test_no_query
~~~~

### Running with tox (full CI matrix)

~~~~ sh
tox --exit-and-dump-after 60
~~~~

Tox runs integration smoke tests (verifying bundled executable and basic
`iterfzf()` calls) across Python 3.8–3.13 and PyPy 3 in both wheel and
sdist modes. These are separate from the unittest suite.

### Important test notes

 -  Several tests require `fzf` to be installed and accessible as
    `executable="fzf"`. Tests that need real `fzf` interaction will fail
    without it.
 -  The `test_raises_keyboard_interrupt` test uses `@patch("subprocess.Popen")`
    to mock the subprocess — this is the pattern to follow for isolated unit
    tests.
 -  Tests for tmux-related features (`test_support_tmux_bool`,
    `test_support_tmux_str`) require both `fzf` and `tmux` to be available.


Formatting and Linting
----------------------

### Formatter: yapf

The **only** enforced code quality tool is `yapf`. It is checked in CI.

~~~~ sh
yapf --diff --recursive .
yapf --in-place --recursive .    # auto-fix
~~~~

Configuration in `pyproject.toml`:

~~~~ toml
[tool.yapf]
based_on_style = "pep8"
column_limit = 79
dedent_closing_brackets = true
indent_dictionary_value = true
~~~~

The `.tox` directory is ignored via `[tool.yapfignore]`.

### No other linters

There is no mypy, ruff, flake8, black, isort, or pylint enforced in CI.
A `.mypy_cache/` entry in `.gitignore` suggests occasional local mypy use.


Code Style Guidelines
---------------------

### Line length

79 characters for Python files. 80 for other files. Enforced via yapf and
`.editorconfig`.

### String quotes

Single quotes preferred throughout: `'string'`, not `"string"`.

### Imports

1.  `from __future__ import ...` first (if present)
2.  Standard library imports, roughly alphabetical
3.  Third-party imports (only in `build_dist.py`: `from flit_core import buildapi`)
4.  Local imports (`from iterfzf import ...`)

Both `import X` and `from X import Y` forms are used. No `isort` is configured;
follow existing patterns.

### Type annotations

 -  All function parameters should have type annotations (Python 3 style)
 -  Module-level constants use type annotations:
    `INTERRUPT_EXIT_CODE: int = 130`
 -  Uses `typing` module types: `Optional`, `Union`, `Literal`, `AnyStr`,
    `Iterable`, `Mapping`
 -  Return type annotations are optional (the main `iterfzf()` function omits
    its return type due to complex conditional return values)

### Naming conventions

| Kind                | Convention         | Example                          |
| ------------------- | ------------------ | -------------------------------- |
| Module constants    | `UPPER_SNAKE_CASE` | `BUNDLED_EXECUTABLE`             |
| Functions           | `snake_case`       | `iterfzf`, `format_option`       |
| Classes             | `PascalCase`       | `IterFzfTest`                    |
| Test methods        | `test_snake_case`  | `test_no_query`                  |
| Internal parameters | `__dunder__`       | `__extra__`                      |
| Version variables   | `__dunder__`       | `__version__`, `__fzf_version__` |

### Module exports

Always define `__all__` explicitly in modules that expose a public API.
See `iterfzf/__init__.py` and `build_dist.py`.

### Function signatures

 -  Use `*` separator to enforce keyword-only arguments (see `iterfzf()`)
 -  Group related parameters with inline comments:

    ~~~~ python
    def iterfzf(
        iterable: Iterable[AnyStr],
        *,
        # Sorting:
        sort: bool = False,
        # Search mode:
        extended: bool = True,
    ~~~~

### Error handling

 -  `ValueError` for invalid input (bad types, disallowed characters)
 -  `KeyboardInterrupt` for user interrupt (fzf exit code 130)
 -  `IOError` with `errno.EPIPE` silently caught for broken pipe scenarios
 -  `RuntimeError` for build/environment failures (rate limits, bad tokens,
    unsupported platforms)
 -  `HTTPError` caught with specific handling for 403 (rate limit) and 401
    (bad token)

### Formatting details

 -  **Indentation**: 4 spaces, no tabs
 -  **Line endings**: LF only
 -  **Final newline**: Always present
 -  **Closing brackets**: Dedented (yapf `dedent_closing_brackets = true`):

    ~~~~ python
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None
    )
    ~~~~
 -  **Line continuation**: Backslash `\` is used for multi-line assignments:

    ~~~~ python
    EXECUTABLE_NAME: Literal['fzf', 'fzf.exe'] = \
        WINDOWS_EXECUTABLE_NAME \
        if sys.platform == 'win32' \
        else POSIX_EXECUTABLE_NAME
    ~~~~
 -  **yapf suppression**: Use `# yapf: disable` comment on lines/blocks that
    should not be auto-formatted (e.g., alignment-sensitive mapping literals)

### YAML files

 -  2-space indentation (per `.editorconfig`)


Versioning
----------

Non-semver composite format:
`ITERFZF_MAJOR.ITERFZF_MINOR.FZF_MAJOR.FZF_MINOR.FZF_PATCH`
(e.g., `1.9.0.62.0` = iterfzf 1.9 + fzf 0.62.0). Defined in
`iterfzf/__init__.py` as `__version__`.


Architecture
------------

 -  `iterfzf/__init__.py` — Entire public API: `iterfzf()` function,
    `BUNDLED_EXECUTABLE`, version constants. Streams iterable input to fzf
    subprocess via stdin pipe, parses stdout for results.
 -  `build_dist.py` — Custom PEP 517 backend. Downloads fzf binary from GitHub,
    bundles it into platform-specific wheels. Maps Python platforms to Go
    OS/ARCH pairs.
 -  `iterfzf/test_iterfzf.py` — Unit tests (`unittest.TestCase`).
 -  `tox.ini` — Integration smoke tests across Python 3.8–3.13 + PyPy, verifying
    bundled executable and basic calls.


Project Structure
-----------------

~~~~
iterfzf/
  __init__.py          # Main module: iterfzf() function and all public API
  test_iterfzf.py      # Unit tests (unittest.TestCase)
  fzf-*-release.json   # Cached fzf GitHub release metadata
build_dist.py          # Custom PEP 517 build backend (downloads/bundles fzf)
pyproject.toml         # Project metadata, build config, yapf config
tox.ini                # Tox test environments
examples/              # Usage examples
~~~~


CI/CD
-----

GitHub Actions workflows in `.github/workflows/`:

 -  **test.yaml**: Runs on push/PR. Matrix: ubuntu + windows, Python 3.8–3.13 +
    PyPy 3.10. Runs `tox` with 60s timeout. Also runs `yapf` format check.
 -  **release.yaml**: Builds wheels for 12 platform combinations, publishes to
    PyPI on tagged releases via trusted publishing.
