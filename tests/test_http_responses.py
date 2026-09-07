import http.client
import io
import os
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tossinvest_api as api
import websocket_prices as stream


class HttpResponseTests(unittest.TestCase):
    BODY = b'{"result":"synthetic-private-marker"}'

    def fetch(self, source, headers, wire_body):
        wire = io.BytesIO(b"HTTP/1.1 200 OK\r\n" + headers + b"\r\n" + wire_body)

        class MemorySocket:
            def makefile(self, *args, **kwargs):
                return wire

        response = http.client.HTTPResponse(MemorySocket())
        response.begin()
        opener = Mock()
        opener.open.return_value = response
        try:
            with patch.object(api.urllib.request, "build_opener", return_value=opener):
                if source == "guest":
                    return stream.fetch_guest_key()
                return api.request_json("/api/v2/stock-infos/A005930")["result"]
        finally:
            self.assertTrue(wire.closed)
            opener.open.assert_called_once()

    def test_complete_http_responses_preserve_payload(self):
        chunk = f"{len(self.BODY):x}\r\n".encode() + self.BODY + b"\r\n0\r\n\r\n"
        cases = (
            (f"Content-Length: {len(self.BODY)}\r\n".encode(), self.BODY),
            (b"", self.BODY),
            (b"Transfer-Encoding: chunked\r\n", chunk),
            (b"Transfer-Encoding: chunked\r\nContent-Length: 999\r\n", chunk),
        )
        for source in ("rest", "guest"):
            for headers, body in cases:
                with self.subTest(source=source, headers=headers):
                    self.assertEqual(self.fetch(source, headers, body), "synthetic-private-marker")

    def test_truncated_http_responses_fail_without_leaking_body(self):
        cases = (
            (f"Content-Length: {len(self.BODY) + 10}\r\n".encode(), self.BODY),
            (
                b"Transfer-Encoding: chunked\r\n",
                f"{len(self.BODY):x}\r\n".encode() + self.BODY + b"\r\n",
            ),
            (
                b"Transfer-Encoding: chunked\r\n",
                f"{len(self.BODY) + 10:x}\r\n".encode() + self.BODY,
            ),
        )
        for source in ("rest", "guest"):
            for headers, body in cases:
                with self.subTest(source=source, headers=headers, body_length=len(body)):
                    stderr = io.StringIO()

                    def main():
                        self.fetch(source, headers, body)
                        return 0

                    with patch.dict(os.environ, {"TOSSINVEST_DEBUG": "1"}):
                        with redirect_stderr(stderr):
                            status = api.run_cli(main)
                    self.assertEqual(status, 1)
                    self.assertIn("RuntimeError", stderr.getvalue())
                    self.assertNotIn("synthetic-private-marker", stderr.getvalue())
                    self.assertNotIn("IncompleteRead", stderr.getvalue())

    def test_response_size_limits_still_apply(self):
        for source in ("rest", "guest"):
            module = api if source == "rest" else stream
            constant = "MAX_RESPONSE_BYTES" if source == "rest" else "MAX_GUEST_RESPONSE_BYTES"
            for extra in (0, 1):
                body = self.BODY + b" " * (64 + extra - len(self.BODY))
                for headers in (b"", f"Content-Length: {len(body)}\r\n".encode()):
                    with self.subTest(source=source, extra=extra, headers=headers):
                        with patch.object(module, constant, 64):
                            if extra:
                                with self.assertRaisesRegex(RuntimeError, "exceeded"):
                                    self.fetch(source, headers, body)
                            else:
                                self.assertEqual(
                                    self.fetch(source, headers, body), "synthetic-private-marker"
                                )
