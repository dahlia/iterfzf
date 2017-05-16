from __future__ import print_function

import errno
import subprocess
import sys

__all__ = 'iterfzf',


def iterfzf(
    iterable,
    # Search mode:
    extended=True, exact=False, case_sensitive=None,
    # Interface:
    multi=False, mouse=True,
    # Layout:
    prompt='> ',
    # Misc:
    query='', encoding=None, executable='fzf'
):
    cmd = [executable, '--no-sort', '--prompt=' + prompt]
    if not extended:
        cmd.append('--no-extended')
    if case_sensitive is not None:
        cmd.append('+i' if case_sensitive else '-i')
    if exact:
        cmd.append('--exact')
    if multi:
        cmd.append('--multi')
    if not mouse:
        cmd.append('--no-mouse')
    if query:
        cmd.append('--query=' + query)
    encoding = encoding or sys.getdefaultencoding()
    proc = None
    stdin = None
    byte = None
    lf = u'\n'
    cr = u'\r'
    for line in iterable:
        if byte is None:
            byte = isinstance(line, bytes)
            if byte:
                lf = b'\n'
                cr = b'\r'
        elif isinstance(line, bytes) is not byte:
            raise ValueError(
                'element values must be all byte strings or all '
                'unicode strings, not mixed of them: ' + repr(line)
            )
        if lf in line or cr in line:
            raise ValueError(r"element values must not contain CR({1!r})/"
                             r"LF({2!r}): {0!r}".format(line, cr, lf))
        if proc is None:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=None
            )
            stdin = proc.stdin
        if not byte:
            line = line.encode(encoding)
        try:
            stdin.write(line + b'\n')
            stdin.flush()
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise
            break
    try:
        stdin.close()
    except IOError as e:
        if e.errno != errno.EPIPE:
            raise
    stdout = proc.stdout
    decode = (lambda b: b) if byte else (lambda t: t.decode(encoding))
    if multi:
        return [decode(l.strip(b'\r\n')) for l in iter(stdout.readline, b'')]
    return decode(stdout.read().strip(b'\r\n'))
