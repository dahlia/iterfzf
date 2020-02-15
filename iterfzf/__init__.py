from __future__ import print_function

import errno
import os.path
import subprocess
import sys
from itertools import chain

from pkg_resources import resource_exists, resource_filename

__all__ = 'BUNDLED_EXECUTABLE', 'iterfzf'

EXECUTABLE_NAME = 'fzf.exe' if sys.platform == 'win32' else 'fzf'
BUNDLED_EXECUTABLE = (
    resource_filename(__name__, EXECUTABLE_NAME)
    if resource_exists(__name__, EXECUTABLE_NAME)
    else (
        os.path.join(os.path.dirname(__file__), EXECUTABLE_NAME)
        if os.path.isfile(
            os.path.join(os.path.dirname(__file__), EXECUTABLE_NAME)
        )
        else None
    )
)


def iterfzf(
    # CHECK: When the signature changes, __init__.pyi file should also change.
    iterable,
    # Search mode:
    extended=True, exact=False, case_sensitive=None,
    # Interface:
    multi=False, mouse=True, print_query=False, cycle=False,
    # Layout:
    prompt='> ',
    preview=None,
    # Misc:
    query='', encoding=None, executable=BUNDLED_EXECUTABLE or EXECUTABLE_NAME
):
    cmd = [executable, '--no-sort', '--prompt=' + prompt]
    if not extended:
        cmd.append('--no-extended')
    if case_sensitive is not None:
        cmd.append('+i' if case_sensitive else '-i')
    if exact:
        cmd.append('--exact')
    if cycle:
        cmd.append('--cycle')
    if multi:
        cmd.append('--multi')
    if not mouse:
        cmd.append('--no-mouse')
    if query:
        cmd.append('--query=' + query)
    if preview:
        cmd.append('--preview=' + preview)
    # always use --print-query: makes things simpler later
    # as return values are always the same
    cmd.append('--print-query')
    query_results = _exec_cmd(cmd, iterable, encoding, executable)
    query, results = query_results[0], query_results[1:]
    if len(results) > 0 and results[0] is not None:
        return_value = results if multi else results[0]
    else:
        return_value = None
    if print_query:
        return query, return_value
    else:
        return return_value


def _exec_cmd(cmd, iterable, encoding, executable):
    """Create subprocess with fzf and return its output to the caller.
    Most of the work here is related to making sure that the encodings
    in both directions are correct.
    In either case returns a tuple where the first element is the query
    which will be returned if query_result=True as well as the chosen items

    Arguments:
        cmd List[str] -- Command to be executed via subprocess
        ... -- just passed through from function call above

    Raises:
        ValueError: If iterable contains unsuitable elements

    Returns:
        str,List[str] -- The query (search entered in fzf) + list of results
    """
    encoding = encoding or sys.getdefaultencoding()
    iterator = iter(iterable)
    try:
        first = next(iterator)
    except StopIteration:
        return None, None  # early exit on empty iterable - fix later
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None
    )
    stdin = proc.stdin
    is_byte = isinstance(first, bytes)
    lf = b'\n' if is_byte else '\n'
    cr = b'\r' if is_byte else '\r'
    for line in chain([first], iterator):
        if isinstance(line, bytes) != is_byte:
            raise ValueError(
                'element values must be all byte strings or all '
                'unicode strings, not a mix of them: ' + repr(line)
            )
        if lf in line or cr in line:
            raise ValueError(
                r'element values must not contain CR({1!r})/'
                r'LF({2!r}): {0!r}'.format(line, cr, lf)
            )
        line_b = line if is_byte else line.encode(encoding)
        try:
            stdin.write(line_b + b'\n')
            stdin.flush()
        except IOError as e:
            if e.errno != errno.EPIPE and errno.EPIPE != 32:
                raise
            break
    if proc is None or proc.wait() not in [0, 1]:
        return None, None
    try:
        stdin.close()
    except IOError as e:
        if e.errno != errno.EPIPE and errno.EPIPE != 32:
            raise
    stdout = proc.stdout
    decode = (lambda b: b) if is_byte else (lambda t: t.decode(encoding))
    return [decode(l.strip(b'\r\n\0')) for l in iter(stdout.readline, b'')]
