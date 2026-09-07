import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.response
from contextlib import redirect_stderr
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import websocket_prices as stream


class FakeTimeout(Exception):
    pass


class FakeSocket:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent = []
        self.closed = False
        self.timeout = None

    def settimeout(self, timeout):
        self.timeout = timeout

    def getstatus(self):
        return 101

    def send(self, message):
        self.sent.append(message)
        if message.startswith("DISCONNECT\n"):
            receipt = next(
                line.partition(":")[2]
                for line in message.splitlines()
                if line.startswith("receipt:")
            )
            self.messages.append(f"RECEIPT\nreceipt-id:{receipt}\n\n\x00")

    def recv(self):
        if self.messages:
            return self.messages.pop(0)
        raise FakeTimeout()

    def close(self):
        self.closed = True


class FakeWebSocketModule:
    WebSocketTimeoutException = FakeTimeout

    def __init__(self, socket):
        self.socket = socket
        self.options = None

    def create_connection(self, url, **options):
        self.options = {"url": url, **options}
        return self.socket


class WebSocketPriceTests(unittest.TestCase):
    def test_build_subscriptions_normalizes_deduplicates_and_keeps_index_case(self):
        subscriptions = stream.build_subscriptions(
            kr_stocks=["005930", "A005930"],
            us_stocks=["us20100311002"],
            kr_indices=["KGG01P", "QGG01P"],
            crypto=["vwap.krw-btc"],
        )

        self.assertEqual(
            [(item.kind, item.code) for item in subscriptions],
            [
                ("kr-stock", "A005930"),
                ("us-stock", "US20100311002"),
                ("kr-index", "KGG01P"),
                ("kr-index", "QGG01P"),
                ("crypto", "VWAP.KRW-BTC"),
            ],
        )

    def test_build_subscriptions_rejects_display_ticker_and_unbounded_fanout(self):
        with self.assertRaisesRegex(ValueError, "US stock product"):
            stream.build_subscriptions(us_stocks=["NVDA"])
        with self.assertRaisesRegex(ValueError, "at most 100"):
            stream.build_subscriptions(kr_stocks=[f"A{i:06d}" for i in range(101)])

    def test_build_subscriptions_uses_exact_public_us_index_allowlist(self):
        supported = ("COMP.NAI", "SPX.CBI", "RGI..VIX", "SOX.NAI")
        subscriptions = stream.build_subscriptions(us_indices=list(supported))

        self.assertEqual(
            [(item.kind, item.code, item.destination) for item in subscriptions],
            [("us-index", code, f"/topic/v1/us/stock/index/{code}") for code in supported],
        )

        for code in ("DJI.DJI", "RFU.NQc1", "RFU.GCv1", "UNKNOWN"):
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "login-gated"):
                stream.build_subscriptions(us_indices=[code])

    def test_build_subscriptions_uses_exact_public_crypto_allowlist(self):
        subscriptions = stream.build_subscriptions(
            crypto=["VWAP.KRW-BTC", "VWAP.KRW-ETH", "VWAP.KRW-XRP", "VWAP.KRW-SOL"]
        )

        self.assertEqual(
            [item.code for item in subscriptions],
            ["VWAP.KRW-BTC", "VWAP.KRW-ETH", "VWAP.KRW-XRP", "VWAP.KRW-SOL"],
        )
        with self.assertRaisesRegex(ValueError, "Unsupported crypto VWAP"):
            stream.build_subscriptions(crypto=["VWAP.KRW-FAKE"])

    def test_validate_subscriptions_rejects_injected_or_duplicate_destinations(self):
        injected = stream.Subscription("kr-stock", "A005930", "/topic/v1/kr/stock/bidoffer/A005930")
        with self.assertRaisesRegex(ValueError, "non-canonical"):
            stream.validate_subscriptions([injected])

        canonical = stream.build_subscriptions(kr_stocks=["A005930"])[0]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            stream.validate_subscriptions([canonical, canonical])

    def test_stomp_parser_handles_partial_and_multiple_frames(self):
        parser = stream.StompParser()
        self.assertEqual(parser.feed("CONNECTED\nversion:1.2\n\n"), [])

        frames = parser.feed(
            '\x00\nMESSAGE\ndestination:/topic/test\nsubscription:sub-0\n\n{"close":100}\x00'
        )

        self.assertEqual([frame.command for frame in frames], ["CONNECTED", "MESSAGE"])
        self.assertEqual(frames[1].headers["destination"], "/topic/test")
        self.assertEqual(json.loads(frames[1].body), {"close": 100})

    def test_stomp_parser_rejects_oversized_incomplete_frame_and_clears_buffer(self):
        parser = stream.StompParser()
        oversized = "x" * (stream.MAX_STOMP_FRAME_BYTES + 1)

        with self.assertRaisesRegex(RuntimeError, "exceeded"):
            parser.feed(oversized)

        self.assertEqual(parser._buffer, "")

    def test_stomp_parser_rejects_oversized_websocket_message(self):
        parser = stream.StompParser()
        oversized = "MESSAGE\n\n\x00" * (stream.MAX_STOMP_CHUNK_BYTES // len("MESSAGE\n\n\x00") + 1)

        with self.assertRaisesRegex(RuntimeError, "WebSocket message exceeded"):
            parser.feed(oversized)

        self.assertEqual(parser._buffer, "")

    def test_stomp_parser_allows_multiple_frames_with_safe_individual_sizes(self):
        parser = stream.StompParser()
        body = "x" * (stream.MAX_STOMP_FRAME_BYTES // 2)
        chunk = f"MESSAGE\n\n{body}\x00MESSAGE\n\n{body}\x00"

        self.assertEqual(len(parser.feed(chunk)), 2)

    def test_normalize_message_emits_only_allowlisted_scalar_fields(self):
        subscription = stream.Subscription("kr-stock", "A005930", "/topic/test")
        event = stream.normalize_message(
            subscription,
            {
                "code": "A005930",
                "close": 100,
                "session": "REGULAR",
                "authorization": "secret",
                "levels": [1, 2, 3],
            },
        )

        self.assertEqual(
            event,
            {
                "kind": "kr-stock",
                "destination": "/topic/test",
                "code": "A005930",
                "close": 100,
                "session": "REGULAR",
            },
        )

    def test_normalize_message_preserves_bounded_live_crypto_fields(self):
        subscription = stream.Subscription(
            "crypto", "VWAP.KRW-BTC", "/topic/v1/crypto/vwap/VWAP.KRW-BTC"
        )
        event = stream.normalize_message(
            subscription,
            {
                "code": "VWAP.KRW-BTC",
                "currency": "KRW",
                "changeType": "RISE",
                "base": 1,
                "close": 2,
                "cumulativeVolume": 3.0,
                "cumulativeAmount": 4.0,
                "dt": "synthetic",
                "unknownScalar": "drop",
                "unknownNested": {"drop": True},
            },
        )

        self.assertEqual(
            event,
            {
                "kind": "crypto",
                "destination": "/topic/v1/crypto/vwap/VWAP.KRW-BTC",
                "code": "VWAP.KRW-BTC",
                "currency": "KRW",
                "changeType": "RISE",
                "base": 1,
                "close": 2,
                "cumulativeVolume": 3.0,
                "cumulativeAmount": 4.0,
                "dt": "synthetic",
            },
        )

    def test_fetch_guest_key_returns_result_without_logging_or_persisting_it(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self, limit):
                self.limit = limit
                return b'{"result":"memory-only-key"}'

        response = Response()
        with patch("urllib.request.OpenerDirector.open", return_value=response):
            self.assertEqual(stream.fetch_guest_key(), "memory-only-key")
        self.assertEqual(response.limit, 4_097)

    def test_guest_bootstrap_rejects_redirects_without_following_or_leaking_reason(self):
        secret = "synthetic-guest-location-must-not-appear"
        for status in (301, 302, 303, 307, 308):
            for location in (f"https://other.example/{secret}", f"https://[{secret}]/"):
                with self.subTest(status=status, location=location):
                    headers = Message()
                    headers["Location"] = location
                    response = urllib.response.addinfourl(
                        io.BytesIO(b""),
                        headers,
                        stream.GUEST_KEY_URL,
                        status,
                    )
                    response.msg = secret
                    output = io.StringIO()
                    with (
                        patch(
                            "urllib.request.HTTPSHandler.https_open", return_value=response
                        ) as opened,
                        patch.dict(os.environ, {"TOSSINVEST_DEBUG": "1"}),
                        redirect_stderr(output),
                    ):
                        self.assertEqual(stream.api.run_cli(stream.fetch_guest_key), 1)
                    self.assertEqual(opened.call_count, 1)
                    self.assertTrue(response.closed)
                    self.assertIn(f"HTTP {status}", output.getvalue())
                    self.assertNotIn(secret, output.getvalue())

    def test_guest_bootstrap_enforces_limit_before_parsing_valid_json(self):
        payload = b'{"result":"memory-only-key"}'
        for length, accepted in ((4_096, True), (4_097, False)):
            with self.subTest(length=length):
                response = io.BytesIO(payload.ljust(length, b" "))
                with patch("urllib.request.OpenerDirector.open", return_value=response):
                    if accepted:
                        self.assertEqual(stream.fetch_guest_key(), "memory-only-key")
                    else:
                        with self.assertRaisesRegex(RuntimeError, "exceeded 4096 bytes"):
                            stream.fetch_guest_key()
                self.assertTrue(response.closed)

    def test_guest_bootstrap_closes_http_errors_and_suppresses_transport_causes(self):
        secret = "synthetic-transport-reason-must-not-appear"
        body = io.BytesIO(secret.encode())
        errors = [
            urllib.error.HTTPError(stream.GUEST_KEY_URL, 403, secret, {}, body),
            urllib.error.URLError(secret),
            TimeoutError(secret),
        ]
        for error in errors:
            with self.subTest(error_type=type(error).__name__):
                output = io.StringIO()
                with (
                    patch("urllib.request.OpenerDirector.open", side_effect=error),
                    patch.dict(os.environ, {"TOSSINVEST_DEBUG": "1"}),
                    redirect_stderr(output),
                ):
                    self.assertEqual(stream.api.run_cli(stream.fetch_guest_key), 1)
                self.assertNotIn(secret, output.getvalue())
                self.assertIn("guest bootstrap", output.getvalue())
        self.assertTrue(body.closed)

    def test_guest_bootstrap_rejects_invalid_payload_without_echoing_it(self):
        secret = "synthetic-invalid-guest-response"
        for payload in (secret.encode(), secret.encode() + b"\xff", b'{"result":null}'):
            with self.subTest(payload_type=payload[-1:]):
                output = io.StringIO()
                with (
                    patch("urllib.request.OpenerDirector.open", return_value=io.BytesIO(payload)),
                    patch.dict(os.environ, {"TOSSINVEST_DEBUG": "1"}),
                    redirect_stderr(output),
                ):
                    self.assertEqual(stream.api.run_cli(stream.fetch_guest_key), 1)
                self.assertNotIn(secret, output.getvalue())
                self.assertIn("Unexpected TossInvest guest bootstrap response", output.getvalue())

    def test_websocket_rejects_non_upgrade_before_sending_guest_connect(self):
        socket = FakeSocket([])
        module = FakeWebSocketModule(socket)
        with patch.object(socket, "getstatus", return_value=302):
            with self.assertRaisesRegex(RuntimeError, "WebSocket connection failed"):
                stream.stream_prices(
                    stream.build_subscriptions(kr_stocks=["A005930"]),
                    duration=1,
                    max_events=1,
                    emit=lambda event: None,
                    guest_key_fetcher=lambda: "synthetic-guest-key",
                    websocket_module=module,
                )
        self.assertEqual(module.options["redirect_limit"], 0)
        self.assertEqual(socket.sent, [])
        self.assertTrue(socket.closed)

    def test_websocket_handshake_failures_hide_guest_values_in_debug_tracebacks(self):
        secret = "synthetic-handshake-secret-must-not-appear"
        for failure in ("create_connection", "send", "recv"):
            with self.subTest(failure=failure):
                socket = FakeSocket([])
                module = FakeWebSocketModule(socket)
                target = module if failure == "create_connection" else socket
                output = io.StringIO()
                with (
                    patch.object(target, failure, side_effect=RuntimeError(secret)),
                    patch.dict(os.environ, {"TOSSINVEST_DEBUG": "1"}),
                    redirect_stderr(output),
                ):
                    result = stream.api.run_cli(
                        lambda: stream.stream_prices(
                            stream.build_subscriptions(kr_stocks=["A005930"]),
                            duration=1,
                            max_events=1,
                            emit=lambda event: None,
                            guest_key_fetcher=lambda: secret,
                            websocket_module=module,
                        )
                    )
                self.assertEqual(result, 1)
                self.assertNotIn(secret, output.getvalue())
                self.assertIn("connection failed", output.getvalue())
                if failure != "create_connection":
                    self.assertTrue(socket.closed)

    def test_pinned_websocket_client_redirect_is_rejected_without_second_connection(self):
        try:
            import websocket
            import websocket._core as core
        except ModuleNotFoundError:
            self.skipTest("optional websocket-client is not installed")
        if websocket.__version__ != "1.9.0":
            self.skipTest("test requires the pinned websocket-client 1.9.0")
        transport = Mock()
        response = SimpleNamespace(
            status=302, headers={"location": "wss://other.example/ws"}, subprotocol=None
        )
        with (
            patch.object(
                core, "connect", return_value=(transport, ("host", 443, "/ws", True))
            ) as opened,
            patch.object(core, "handshake", return_value=response),
            patch.object(core.WebSocket, "send") as send,
            patch.object(core.WebSocket, "close") as close,
        ):
            with self.assertRaisesRegex(RuntimeError, "WebSocket connection failed"):
                stream.stream_prices(
                    stream.build_subscriptions(kr_stocks=["A005930"]),
                    duration=1,
                    max_events=1,
                    emit=lambda event: None,
                    guest_key_fetcher=lambda: "synthetic-guest-key",
                    websocket_module=websocket,
                )
        self.assertEqual(opened.call_count, 1)
        self.assertEqual(opened.call_args.args[0], stream.SOCKET_URL)
        send.assert_not_called()
        close.assert_called_once()

    def test_stream_prices_connects_subscribes_normalizes_and_closes(self):
        destination = "/topic/v1/kr/stock/trade/A005930"
        socket = FakeSocket(
            [
                "CONNECTED\nversion:1.2\n\n\x00",
                "MESSAGE\n"
                "subscription:sub-0\nmessage-id:m-1\n\n"
                '{"code":"A005930","close":100,"authorization":"hidden"}\x00',
            ]
        )
        module = FakeWebSocketModule(socket)
        events = []

        count = stream.stream_prices(
            [stream.Subscription("kr-stock", "A005930", destination)],
            duration=5,
            max_events=1,
            emit=events.append,
            guest_key_fetcher=lambda: "memory-only-key",
            websocket_module=module,
        )

        self.assertEqual(count, 1)
        self.assertEqual(events[0]["close"], 100)
        self.assertNotIn("authorization", events[0])
        self.assertEqual(
            module.options,
            {
                "url": stream.SOCKET_URL,
                "subprotocols": [stream.SUBPROTOCOL],
                "origin": stream.PUBLIC_ORIGIN,
                "timeout": stream.CONNECT_TIMEOUT_SECONDS,
                "redirect_limit": 0,
            },
        )
        connect_frame = next(message for message in socket.sent if message.startswith("CONNECT\n"))
        self.assertEqual(connect_frame.count(f"\nhost:{stream.SOCKET_HOST}\n"), 1)
        subscribe_frame = next(
            message for message in socket.sent if message.startswith("SUBSCRIBE\n")
        )
        self.assertIn("\nid:sub-0\n", subscribe_frame)
        self.assertIn(f"\ndestination:{destination}\n", subscribe_frame)
        self.assertNotIn("\nack:", subscribe_frame)
        self.assertTrue(any(message.startswith("UNSUBSCRIBE\n") for message in socket.sent))
        self.assertTrue(
            any(
                message.startswith("DISCONNECT\n") and "\nreceipt:" in message
                for message in socket.sent
            )
        )
        self.assertTrue(socket.closed)

    def test_subscriptions_are_sent_in_twenty_item_batches(self):
        subscriptions = stream.build_subscriptions(kr_stocks=[f"A{i:06d}" for i in range(45)])
        socket = FakeSocket([])
        subscription_ids = {
            item.destination: f"sub-{index}" for index, item in enumerate(subscriptions)
        }
        subscribed_ids = []

        with patch("websocket_prices.time.sleep") as sleep:
            stream._send_subscriptions(socket, subscriptions, subscription_ids, subscribed_ids)

        self.assertEqual(len(subscribed_ids), 45)
        self.assertEqual(sum(message.startswith("SUBSCRIBE\n") for message in socket.sent), 45)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_called_with(stream.SUBSCRIPTION_BATCH_INTERVAL_SECONDS)

    def test_single_instance_lock_rejects_a_second_client_and_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "client.lock"
            with stream.SingleInstanceLock(lock_path):
                with self.assertRaisesRegex(RuntimeError, "already running"):
                    with stream.SingleInstanceLock(lock_path):
                        pass
            with stream.SingleInstanceLock(lock_path):
                pass

    def test_jsonl_emitter_is_compact_and_batches_flushes(self):
        class RecordingOutput(io.StringIO):
            def __init__(self):
                super().__init__()
                self.flush_count = 0

            def flush(self):
                self.flush_count += 1
                super().flush()

        output = RecordingOutput()
        emitter = stream.JsonlEmitter(output)
        emitter({"code": "A005930", "close": 100})
        self.assertEqual(output.getvalue(), '{"code":"A005930","close":100}\n')
        self.assertEqual(output.flush_count, 1)

        for index in range(stream.OUTPUT_FLUSH_EVENTS):
            emitter({"code": f"A{index:06d}"})
        self.assertEqual(output.flush_count, 2)

    def test_websocket_dependency_is_exactly_pinned_and_hashed(self):
        requirements = (ROOT / "requirements-websocket.txt").read_text(encoding="utf-8")
        self.assertIn("--only-binary=:all:", requirements)
        self.assertIn("--require-hashes", requirements)
        self.assertIn("websocket-client==1.9.0", requirements)
        self.assertIn("sha256:", requirements)

    def test_missing_dependency_routes_to_project_local_install_docs(self):
        real_import = stream.importlib.import_module

        def import_without_websocket(name):
            if name == "websocket":
                raise ModuleNotFoundError(name)
            return real_import(name)

        with patch(
            "websocket_prices.importlib.import_module", side_effect=import_without_websocket
        ):
            with self.assertRaisesRegex(RuntimeError, r"project-local `\.venv`"):
                stream._load_websocket_module()


if __name__ == "__main__":
    unittest.main()
