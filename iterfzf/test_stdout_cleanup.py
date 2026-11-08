import io
import unittest
from unittest.mock import Mock, patch

import iterfzf


class StdoutCleanupTest(unittest.TestCase):

    def process(self, output: bytes, exit_code: int = 0):
        proc = Mock()
        proc.stdin = io.BytesIO()
        proc.stdout = io.BytesIO(output)
        proc.wait.return_value = exit_code
        self.addCleanup(proc.stdin.close)
        self.addCleanup(proc.stdout.close)
        return proc

    def test_selected_output_is_closed(self):
        for byte in (False, True):
            for read0 in (False, True):
                for multi in (False, True):
                    for print_query in (False, True):
                        with self.subTest(
                            byte=byte,
                            read0=read0,
                            multi=multi,
                            print_query=print_query
                        ):
                            items = [b'alpha', b'beta'
                                     ] if byte else ['alpha', 'beta']
                            query = b'a' if byte else 'a'
                            separator = b'\0' if read0 else b'\n'
                            output = [b'alpha', b'beta']
                            if print_query:
                                output.insert(0, b'a')
                            proc = self.process(
                                separator.join(output) + separator
                            )
                            with patch('subprocess.Popen', return_value=proc):
                                actual = iterfzf.iterfzf(
                                    items,
                                    read0=read0,
                                    multi=multi,
                                    print_query=print_query
                                )
                            expected = items if multi else items[0]
                            if print_query:
                                expected = query, expected
                            self.assertEqual(actual, expected)
                            self.assertTrue(proc.stdin.closed)
                            self.assertTrue(proc.stdout.closed)

    def test_no_matches_closes_stdout(self):
        for read0 in (False, True):
            for multi in (False, True):
                for print_query in (False, True):
                    with self.subTest(
                        read0=read0, multi=multi, print_query=print_query
                    ):
                        output = (
                            b'absent\0' if read0 else b'absent\n'
                        ) if print_query else b''
                        proc = self.process(output, 1)
                        with patch('subprocess.Popen', return_value=proc):
                            actual = iterfzf.iterfzf(
                                ['alpha'],
                                read0=read0,
                                multi=multi,
                                print_query=print_query
                            )
                        expected = [] if multi else None
                        if print_query:
                            expected = 'absent', expected
                        self.assertEqual(actual, expected)
                        self.assertTrue(proc.stdout.closed)

    def test_error_exit_closes_stdout(self):
        for exit_code in (2, -1):
            for print_query in (False, True):
                with self.subTest(
                    exit_code=exit_code, print_query=print_query
                ):
                    proc = self.process(b'', exit_code)
                    with patch('subprocess.Popen', return_value=proc):
                        actual = iterfzf.iterfzf(
                            ['alpha'], print_query=print_query
                        )
                    self.assertEqual(
                        actual, (None, None) if print_query else None
                    )
                    self.assertTrue(proc.stdout.closed)

    def test_interrupt_exit_closes_stdout(self):
        proc = self.process(b'', iterfzf.INTERRUPT_EXIT_CODE)
        with patch('subprocess.Popen', return_value=proc):
            with self.assertRaises(KeyboardInterrupt):
                iterfzf.iterfzf(['alpha'])
        self.assertTrue(proc.stdout.closed)

    def test_decode_error_closes_stdout(self):
        for read0 in (False, True):
            with self.subTest(read0=read0):
                proc = self.process(b'\xff\0' if read0 else b'\xff\n')
                with patch('subprocess.Popen', return_value=proc):
                    with self.assertRaises(UnicodeDecodeError):
                        iterfzf.iterfzf(
                            ['alpha'], read0=read0, encoding='utf-8'
                        )
                self.assertTrue(proc.stdout.closed)

    def test_wait_error_closes_stdout(self):
        proc = self.process(b'')
        error = OSError('wait failed')
        proc.wait.side_effect = error
        with patch('subprocess.Popen', return_value=proc):
            with self.assertRaises(OSError) as raised:
                iterfzf.iterfzf(['alpha'])
        self.assertIs(raised.exception, error)
        self.assertTrue(proc.stdout.closed)

    def test_read_error_closes_stdout(self):

        class BrokenReader(io.BytesIO):

            def read(self, size: int = -1):
                raise OSError('read failed')

            def readline(self, size: int = -1):
                raise OSError('readline failed')

        for read0 in (False, True):
            with self.subTest(read0=read0):
                proc = self.process(b'')
                proc.stdout = BrokenReader()
                self.addCleanup(proc.stdout.close)
                with patch('subprocess.Popen', return_value=proc):
                    with self.assertRaises(OSError):
                        iterfzf.iterfzf(['alpha'], read0=read0)
                self.assertTrue(proc.stdout.closed)

    def test_close_error_preserves_active_exception(self):

        class BrokenCloser(io.BytesIO):

            def close(self):
                super().close()
                raise OSError('close failed')

        for error in (KeyboardInterrupt(), OSError('wait failed')):
            with self.subTest(error=type(error).__name__):
                proc = self.process(b'')
                proc.stdout = BrokenCloser()
                self.addCleanup(io.BytesIO.close, proc.stdout)
                proc.wait.side_effect = error
                with patch('subprocess.Popen', return_value=proc):
                    with self.assertRaises(type(error)) as raised:
                        iterfzf.iterfzf(['alpha'])
                self.assertIs(raised.exception, error)
                self.assertTrue(proc.stdout.closed)

    def test_close_error_is_reported_without_active_exception(self):

        class BrokenCloser(io.BytesIO):

            def close(self):
                super().close()
                raise OSError('close failed')

        proc = self.process(b'alpha\n')
        proc.stdout = BrokenCloser(b'alpha\n')
        self.addCleanup(io.BytesIO.close, proc.stdout)
        with patch('subprocess.Popen', return_value=proc):
            # A handled exception in the caller is not a pending exception
            # from iterfzf and must not hide its close failure.
            try:
                raise ValueError('already handled')
            except ValueError:
                with self.assertRaisesRegex(OSError, 'close failed'):
                    iterfzf.iterfzf(['alpha'])
        self.assertTrue(proc.stdout.closed)
