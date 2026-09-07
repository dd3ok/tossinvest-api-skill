import io
import json
import subprocess
import sys
import unittest
import urllib.error
import urllib.response
from email.message import Message
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tossinvest_api as api


class TossInvestApiTests(unittest.TestCase):
    def test_urllib_first_import_with_script_calendar_shadow_does_not_cycle(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                "import urllib.request; import tossinvest_api; tossinvest_api.no_redirect_handler()",
            ],
            cwd=ROOT / "scripts",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_normalize_product_code_adds_prefix_for_kr_numeric_codes(self):
        self.assertEqual(api.normalize_product_code("005930"), "A005930")
        self.assertEqual(api.normalize_product_code("a005930"), "A005930")
        self.assertEqual(api.normalize_product_code("A005930"), "A005930")

    def test_to_company_code_strips_domestic_product_prefix_only(self):
        self.assertEqual(api.to_company_code("A005930"), "005930")
        self.assertEqual(api.to_company_code("005930"), "005930")
        self.assertEqual(api.to_company_code("AAPL"), "AAPL")

    def test_build_path_encodes_params_and_skips_none_values(self):
        path = api.build_path(
            "/api/v3/stock-prices/details",
            {"productCodes": "A005930,A000660", "meta": True, "empty": None},
        )
        self.assertEqual(
            path,
            "/api/v3/stock-prices/details?productCodes=A005930%2CA000660&meta=true",
        )

    def test_build_path_rejects_sensitive_query_keys(self):
        with self.assertRaisesRegex(RuntimeError, "sensitive key accountNo"):
            api.build_path("/api/v3/stock-prices/details", {"accountNo": "123"})
        with self.assertRaisesRegex(RuntimeError, "sensitive key authorization"):
            api.build_path("/api/v3/stock-prices/details", {"authorization": "Bearer token"})

    def test_request_target_rejects_blank_sensitive_query_keys(self):
        for path in [
            "/api/v3/stock-prices/details?accountNo=",
            "/api/v3/stock-prices/details?accountNo",
        ]:
            with self.subTest(path=path):
                with self.assertRaisesRegex(RuntimeError, "sensitive key accountNo"):
                    api.validate_request_target(api.BASE_URL, path)

    def test_result_or_raise_returns_result_key(self):
        self.assertEqual(api.result_or_raise({"result": {"ok": True}}), {"ok": True})

    def test_result_or_raise_rejects_unexpected_shape(self):
        with self.assertRaisesRegex(RuntimeError, "missing top-level result"):
            api.result_or_raise({"data": []})

    def test_find_by_code_uses_code_and_product_code(self):
        rows = [{"code": "A000660"}, {"productCode": "A005930", "close": 100}]
        self.assertEqual(api.find_by_code(rows, "005930"), {"productCode": "A005930", "close": 100})

    def test_render_csv_includes_keys_discovered_after_first_row(self):
        rows = [
            {"date": "2026-01-01", "close": 100},
            {"date": "2026-01-02", "volume": 2000, "close": 101},
        ]

        self.assertEqual(
            api.render_csv(rows),
            "date,close,volume\r\n2026-01-01,100,\r\n2026-01-02,101,2000\r\n",
        )

    def test_emit_output_escapes_only_characters_the_console_cannot_encode(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="cp949", write_through=True)
        with patch.object(api.sys, "stdout", stream):
            api.emit_output(api.render_json({"message": "한글 • 😀"}), None)
        rendered = buffer.getvalue().decode("cp949")
        stream.detach()

        self.assertEqual(json.loads(rendered), {"message": "한글 • 😀"})
        self.assertIn("\\u2022", rendered)
        self.assertIn("\\ud83d\\ude00", rendered)

    def test_request_json_rejects_account_or_order_paths_before_network(self):
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.request_json("/api/v1/accounts/balance")
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.request_json("/api/v3/trading/order/A005930/create")

    def test_request_json_rejects_encoded_account_or_order_paths_before_network(self):
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.validate_request_target(
                api.BASE_URL,
                "/api/v1/%61ccounts/balance",
            )
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.validate_request_target(
                api.BASE_URL,
                "/api/v1/stock-infos%2F..%2Ftrading%2Forder/A005930/create",
            )

    def test_request_json_rejects_unapproved_cert_paths_before_network(self):
        with self.assertRaisesRegex(RuntimeError, "not an approved cert-api endpoint"):
            api.request_json(
                "/api/v1/certificates/mutation",
                base_url="https://wts-cert-api.tossinvest.com",
            )

    def test_rate_limit_http_error_mentions_stop_and_reverify(self):
        exc = urllib.error.HTTPError(
            url="https://wts-info-api.tossinvest.com/api/v2/stock-infos/A005930",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=None,
        )

        message = api._http_error_message(exc, "GET", "/api/v2/stock-infos/A005930")
        exc.close()

        self.assertIn("HTTP 429", message)
        self.assertIn("stop", message)
        self.assertIn("rate limit", message)
        self.assertIn("reverify", message)

    def test_cert_allowlist_distinguishes_exact_paths_from_prefixes(self):
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v2/screener/screen",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v2/screener/screen/search/modal",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/screener/filters/base",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/screener/filters/range",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/dashboard/wts/overview/indicator/bond?market=kr",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/dashboard/wts/overview/indicator/index?market=kr",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/dashboard/wts/overview/indicator/commodity?market=kr",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v4/calendar/monthly/2026-05",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/calendar/ai-summary/key-events",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/nova-calendar/ai/summary/weekly",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v2/dashboard/wts/overview/calendar/economic-events",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v4/calendar/monthly/2026-06/index?countryType=us",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-06-01",
        )
        api.validate_request_target(
            api.CERT_BASE_URL,
            (
                "/api/v1/nova-calendar/ai/analysis/indicators"
                "?announceDateTime=2026-06-01T23%3A00%3A00&ricId=USPMI%3DECI"
            ),
        )

        with self.assertRaisesRegex(RuntimeError, "not an approved cert-api endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v2/screener/screen-extra",
            )
        with self.assertRaisesRegex(RuntimeError, "not an approved cert-api endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/dashboard/wts/overview/indicator-extra/bond",
            )
        with self.assertRaisesRegex(RuntimeError, "not an approved cert-api endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/dashboard/wts/overview/indicator/unverified",
            )
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/dashboard/wts/overview/indicator/bond/account",
            )
        with self.assertRaisesRegex(RuntimeError, "not an approved cert-api endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v4/calendar/monthly/2026-5",
            )
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v4/calendar/monthly/2026-05/account",
            )
        with self.assertRaisesRegex(RuntimeError, "not an approved cert-api endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/calendar/ai-summary/key-events-extra",
            )
        with self.assertRaisesRegex(RuntimeError, "query parameters"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v4/calendar/monthly/2026-05?stockCategory=WATCHLIST",
            )
        with self.assertRaisesRegex(RuntimeError, "query parameters"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/calendar/ai-summary/key-events?filter=HOLDING",
            )
        with self.assertRaisesRegex(RuntimeError, "countryType"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v4/calendar/monthly/2026-06/index?countryType=watchlist",
            )
        with self.assertRaisesRegex(RuntimeError, "announceDate"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-6-1",
            )
        with self.assertRaisesRegex(RuntimeError, "valid calendar date"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-02-31",
            )
        with self.assertRaisesRegex(RuntimeError, "duplicate query parameter announceDate"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                (
                    "/api/v1/calendar/economic-indicators/USPMI=ECI"
                    "?announceDate=2026-06-01&announceDate=2026-06-02"
                ),
            )
        with self.assertRaisesRegex(RuntimeError, "Blocked TossInvest endpoint"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/calendar/economic-indicators/../account?announceDate=2026-06-01",
            )
        with self.assertRaisesRegex(RuntimeError, "unexpected query"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-06-01&filter=HOLDING",
            )
        with self.assertRaisesRegex(RuntimeError, "announceDateTime"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                (
                    "/api/v1/nova-calendar/ai/analysis/indicators"
                    "?announceDateTime=2026-06-01&ricId=USPMI%3DECI"
                ),
            )
        with self.assertRaisesRegex(RuntimeError, "requires an empty JSON body"):
            api.request_json(
                "/api/v4/calendar/monthly/2026-05",
                method="POST",
                body={"stockCategory": "WATCHLIST"},
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "requires an empty JSON body"):
            api.request_json(
                "/api/v4/calendar/monthly/2026-05",
                method="POST",
                body=None,
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "must use POST"):
            api.request_json(
                "/api/v4/calendar/monthly/2026-05",
                method="GET",
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "must use GET"):
            api.request_json(
                "/api/v1/calendar/ai-summary/key-events",
                method="POST",
                body={},
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "do not accept request bodies"):
            api.request_json(
                "/api/v1/calendar/ai-summary/key-events",
                method="GET",
                body={},
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "must use POST"):
            api.request_json(
                "/api/v4/calendar/monthly/2026-06/index?countryType=us",
                method="GET",
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "must use GET"):
            api.request_json(
                "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-06-01",
                method="POST",
                body={},
                base_url=api.CERT_BASE_URL,
            )

    def test_cert_allowlist_allows_verified_public_social_and_status_reads(self):
        allowed_paths = [
            ("/api/v4/comments?subjectType=STOCK&subjectId=US20100311002&commentSortType=POPULAR"),
            (
                "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                "&commentSortType=RECENT&lastCommentId=287893608"
            ),
            ("/api/v4/comments?subjectType=LOUNGE&subjectId=LOUNGE_123&commentSortType=RECENT"),
            "/api/v2/comments/287893106/replies",
            "/api/v1/comments/287893106/replies",
            "/api/v1/comments/287893106/replies?lastReplyId=287893107",
            "/api/v4/feed/recommend/ranking-posts",
            "/api/v4/dashboard/wts/overview/indicator",
            "/api/v1/boards/STOCK/US20100311002/related",
            "/api/v1/community/board/US20100311002/recommend-profiles",
            "/api/v1/community/top-rankings/TOP_10_PROFIT_ROSS_AMOUNT",
            "/api/v1/stock-infos/US20100311002/red-flags",
            "/api/v3/trading/order/US20100311002/trading-status",
            "/api/v1/trading/analysis/productCode/US20100311002",
        ]
        for path in allowed_paths:
            with self.subTest(path=path):
                api.validate_request_target(api.CERT_BASE_URL, path)

    def test_cert_public_social_allowlist_rejects_unverified_writes_and_queries(self):
        rejected_paths = [
            ("/api/v4/comments?subjectType=ACCOUNT&subjectId=123&commentSortType=POPULAR"),
            (
                "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                "&commentSortType=FOLLOWING"
            ),
            ("/api/v4/comments?subjectType=STOCK&subjectId=LOUNGE_123&commentSortType=POPULAR"),
            ("/api/v4/comments?subjectType=LOUNGE&subjectId=US20100311002&commentSortType=POPULAR"),
            (
                "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                "&commentSortType=POPULAR&accountNo=123"
            ),
            "/api/v1/comments/287893106/reaction/LIKE",
            "/api/v1/comments/287893106/bookmark/true",
            "/api/v2/comments/report",
            "/api/v1/comments/287893106/replies?lastReplyId=not-a-number",
            "/api/v1/comments/287893106/replies?lastReplyId=%EF%BC%91%EF%BC%92%EF%BC%93",
            "/api/v1/comments/287893106/replies?lastReplyId=%D9%A1%D9%A2%D9%A3",
            "/api/v1/comments/287893106/replies?accountNo=123",
            "/api/v2/comments/upload/picture",
            "/api/v1/user-profiles/update",
            "/api/v3/trading/order/US20100311002/create",
        ]
        for path in rejected_paths:
            with self.subTest(path=path):
                with self.assertRaises(RuntimeError):
                    api.validate_request_target(api.CERT_BASE_URL, path)

    def test_cert_public_social_reads_must_use_get_without_body(self):
        with self.assertRaisesRegex(RuntimeError, "public cert read routes must use GET"):
            api.request_json(
                (
                    "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                    "&commentSortType=POPULAR"
                ),
                method="POST",
                body={},
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "public cert read routes do not accept"):
            api.request_json(
                "/api/v2/comments/287893106/replies",
                method="GET",
                body={},
                base_url=api.CERT_BASE_URL,
            )

    def test_public_cert_get_serialization_has_no_body_or_content_type(self):
        captured = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self, limit):
                return b'{"result":{"comments":[]}}'

        def fake_urlopen(request, timeout):
            captured.append(
                {
                    "data": request.data,
                    "headers": {key.lower(): value for key, value in request.header_items()},
                    "method": request.get_method(),
                    "timeout": timeout,
                    "url": request.full_url,
                }
            )
            return FakeResponse()

        with patch.object(api.urllib.request, "build_opener") as build_opener:
            build_opener.return_value.open.side_effect = fake_urlopen
            payload = api.request_json(
                (
                    "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                    "&commentSortType=POPULAR"
                ),
                method="GET",
                body=None,
                base_url=api.CERT_BASE_URL,
            )

        self.assertEqual(payload, {"result": {"comments": []}})
        self.assertEqual(captured[0]["method"], "GET")
        self.assertIsNone(captured[0]["data"])
        self.assertNotIn("content-type", captured[0]["headers"])
        self.assertEqual(
            captured[0]["url"],
            api.CERT_BASE_URL + "/api/v4/comments?subjectType=STOCK"
            "&subjectId=US20100311002&commentSortType=POPULAR",
        )

    def test_calendar_request_body_serialization_matches_observed_routes(self):
        captured = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self, limit):
                return b'{"result":{"ok":true}}'

        def fake_urlopen(request, timeout):
            captured.append(
                {
                    "data": request.data,
                    "headers": {key.lower(): value for key, value in request.header_items()},
                    "method": request.get_method(),
                    "timeout": timeout,
                    "url": request.full_url,
                }
            )
            return FakeResponse()

        with patch.object(api.urllib.request, "build_opener") as build_opener:
            build_opener.return_value.open.side_effect = fake_urlopen
            api.request_json(
                "/api/v4/calendar/monthly/2026-05",
                method="POST",
                body={},
                base_url=api.CERT_BASE_URL,
            )
            api.request_json(
                "/api/v1/calendar/ai-summary/key-events",
                method="GET",
                body=None,
                base_url=api.CERT_BASE_URL,
            )

        self.assertEqual(captured[0]["method"], "POST")
        self.assertEqual(captured[0]["data"], b"{}")
        self.assertEqual(captured[0]["headers"].get("content-type"), "application/json")
        self.assertEqual(captured[1]["method"], "GET")
        self.assertIsNone(captured[1]["data"])
        self.assertNotIn("content-type", captured[1]["headers"])

    def test_redirects_stop_before_any_followup_request_and_close_response(self):
        class UnreadableBody(io.BytesIO):
            def read(self, *args):
                raise AssertionError("Redirect bodies must not be read")

        locations = (
            api.BASE_URL + "/api/v2/stock-infos/A000660",
            api.BASE_URL + "/api/v1/login?token=synthetic-redirect-secret",
            "https://example.invalid/login?token=synthetic-redirect-secret",
            "http://wts-info-api.tossinvest.com/api/v2/stock-infos/A005930",
            "https://[synthetic-redirect-secret]/",
            "https://[::1",
            "",
            None,
        )
        for status in (301, 302, 303, 307, 308):
            for location in locations:
                with self.subTest(status=status, location=location):
                    requests = []
                    headers = Message()
                    if location is not None:
                        headers["Location"] = location
                    response = urllib.response.addinfourl(
                        UnreadableBody(b"synthetic-error-body-secret"),
                        headers,
                        api.BASE_URL + "/api/v2/stock-infos/A005930",
                        status,
                    )
                    response.msg = "synthetic-redirect-secret"

                    class FakeHTTPSHandler(urllib.request.HTTPSHandler):
                        def https_open(self, request):
                            requests.append(request.full_url)
                            return response

                    opener = urllib.request.build_opener(
                        api.no_redirect_handler(), FakeHTTPSHandler()
                    )
                    stderr = io.StringIO()
                    with (
                        patch.object(api.urllib.request, "build_opener", return_value=opener),
                        patch.dict(api.os.environ, {"TOSSINVEST_DEBUG": "1"}),
                        patch.object(api.sys, "stderr", stderr),
                    ):
                        result = api.run_cli(
                            lambda: api.request_json("/api/v2/stock-infos/A005930")
                        )
                    self.assertEqual(result, 1)
                    self.assertEqual(len(requests), 1)
                    self.assertTrue(response.closed)
                    self.assertIn(f"HTTP {status}", stderr.getvalue())
                    self.assertIn("redirect blocked", stderr.getvalue())
                    self.assertNotIn("synthetic-redirect-secret", stderr.getvalue())
                    self.assertNotIn("synthetic-error-body-secret", stderr.getvalue())

    def test_http_errors_do_not_read_or_emit_response_bodies_and_close_them(self):
        class UnreadableBody(io.BytesIO):
            def read(self, *args):
                raise AssertionError("HTTP error bodies must not be read")

        for status in (400, 403, 404, 429, 500):
            with self.subTest(status=status):
                body = UnreadableBody(b"synthetic-private-marker")
                error = urllib.error.HTTPError(
                    api.BASE_URL, status, "synthetic-private-message", {}, body
                )
                with patch.object(api.urllib.request, "build_opener") as opener:
                    opener.return_value.open.side_effect = error
                    with self.assertRaisesRegex(RuntimeError, f"HTTP {status}") as raised:
                        api.request_json("/api/v2/stock-infos/A005930")
                self.assertTrue(body.closed)
                self.assertNotIn("synthetic-private", str(raised.exception))
                if status in (403, 429):
                    self.assertIn("stop automated retries", str(raised.exception))

    def test_debug_http_errors_keep_tracebacks_without_raw_server_details(self):
        for status in (302, 400, 403, 429, 500):
            with self.subTest(status=status):
                body = io.BytesIO(b"synthetic-private-body")
                error = urllib.error.HTTPError(
                    api.BASE_URL + "?token=synthetic-private-url",
                    status,
                    "redirect to https://example.invalid/?token=synthetic-private-message",
                    {"Location": "https://example.invalid/?token=synthetic-private-header"},
                    body,
                )
                stderr = io.StringIO()
                with patch.object(api.urllib.request, "build_opener") as opener:
                    opener.return_value.open.side_effect = error
                    with patch.dict(api.os.environ, {"TOSSINVEST_DEBUG": "1"}):
                        with patch.object(api.sys, "stderr", stderr):
                            result = api.run_cli(
                                lambda: api.request_json("/api/v2/stock-infos/A005930")
                            )
                self.assertEqual(result, 1)
                self.assertTrue(body.closed)
                self.assertIn("Traceback", stderr.getvalue())
                self.assertIn(f"HTTP {status}", stderr.getvalue())
                self.assertIn("/api/v2/stock-infos/A005930", stderr.getvalue())
                self.assertNotIn("synthetic-private", stderr.getvalue())

    def test_json_read_is_bounded_and_closes_responses_at_size_boundary(self):
        class RecordingBody(io.BytesIO):
            def read(self, size=-1):
                self.read_size = size
                return super().read(size)

        valid_json = b'{"result":{}}'
        for extra, should_succeed in ((0, True), (1, False)):
            with self.subTest(extra=extra):
                response = RecordingBody(valid_json + b" " * extra)
                with patch.object(api, "MAX_RESPONSE_BYTES", len(valid_json)):
                    with patch.object(api.urllib.request, "build_opener") as opener:
                        opener.return_value.open.return_value = response
                        if should_succeed:
                            self.assertEqual(
                                api.request_json("/api/v2/stock-infos/A005930"), {"result": {}}
                            )
                        else:
                            with self.assertRaisesRegex(RuntimeError, "exceeded the local"):
                                api.request_json("/api/v2/stock-infos/A005930")
                self.assertEqual(response.read_size, len(valid_json) + 1)
                self.assertTrue(response.closed)

    def test_non_object_and_invalid_json_are_drift_errors(self):
        for raw in (b"null", b"[]", b"42", b'"result"', b"\xff", b"<html>login</html>"):
            with self.subTest(raw=raw):
                response = io.BytesIO(raw)
                with patch.object(api.urllib.request, "build_opener") as opener:
                    opener.return_value.open.return_value = response
                    with self.assertRaisesRegex(RuntimeError, "reverify the endpoint"):
                        api.request_json("/api/v2/stock-infos/A005930")
                self.assertTrue(response.closed)
        for payload in (None, [], "result"):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(RuntimeError, "top-level JSON must be an object"):
                    api.result_or_raise(payload)

    def test_non_origin_bases_cannot_change_the_validated_request_target(self):
        invalid_bases = (
            "http://wts-info-api.tossinvest.com",
            api.BASE_URL + "/api/v1/login?ignored=",
            api.BASE_URL + "?ignored=",
            api.BASE_URL + "#ignored",
            *(
                base + suffix
                for base in (api.BASE_URL, api.CERT_BASE_URL)
                for suffix in ("?", "#", "?#")
            ),
            "https://user:password@wts-info-api.tossinvest.com",
        )
        with patch.object(api.urllib.request, "build_opener") as opener:
            for base in invalid_bases:
                with self.subTest(base=base):
                    with self.assertRaisesRegex(RuntimeError, "HTTPS origin only"):
                        api.request_json("/api/v2/stock-infos/A005930", base_url=base)
            with self.assertRaisesRegex(RuntimeError, "fragment"):
                api.request_json("/api/v2/stock-infos/A005930#ignored")
        opener.assert_not_called()

    def test_request_json_rejects_sensitive_body_keys_before_network(self):
        with self.assertRaisesRegex(RuntimeError, "sensitive key accountNo"):
            api.request_json(
                "/api/v1/screener/screen/count",
                method="POST",
                body={"accountNo": "123", "filters": []},
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "sensitive key authorization"):
            api.request_json(
                "/api/v1/screener/screen/count",
                method="POST",
                body={"filters": [{"authorization": "Bearer token"}]},
                base_url=api.CERT_BASE_URL,
            )
        with self.assertRaisesRegex(RuntimeError, "sensitive key accountNo"):
            api.request_json(
                "/api/v1/screener/screen/count",
                method="POST",
                body=({"accountNo": "123"},),
                base_url=api.CERT_BASE_URL,
            )

    def test_screener_metadata_usage_requires_exact_public_post_shapes(self):
        api.validate_request_usage(
            api.CERT_BASE_URL,
            "/api/v1/screener/filters/base",
            "POST",
            {"filterId": "RSI_범위", "nation": "kr"},
        )
        api.validate_request_usage(
            api.CERT_BASE_URL,
            "/api/v1/screener/filters/range",
            "POST",
            {
                "filter": {
                    "id": "RSI_범위",
                    "conditions": [
                        {"id": "NUMBER_RANGE_DEFAULT", "type": "NUMBER_RANGE", "value": {}}
                    ],
                },
                "nation": "us",
            },
        )
        with self.assertRaisesRegex(RuntimeError, "must use POST"):
            api.validate_request_usage(
                api.CERT_BASE_URL,
                "/api/v1/screener/filters/base",
                "GET",
                None,
            )
        with self.assertRaisesRegex(RuntimeError, "requires filterId and nation"):
            api.validate_request_usage(
                api.CERT_BASE_URL,
                "/api/v1/screener/filters/base",
                "POST",
                {"filterId": "ACCOUNT FILTER", "nation": "kr"},
            )
        with self.assertRaisesRegex(RuntimeError, "do not accept query parameters"):
            api.validate_request_target(
                api.CERT_BASE_URL,
                "/api/v1/screener/filters/base?mode=all",
            )

    def test_require_int_range_rejects_non_positive_and_excessive_values(self):
        self.assertEqual(api.require_int_range("ticks", 5, minimum=1, maximum=100), 5)
        with self.assertRaisesRegex(ValueError, "ticks must be at least 1"):
            api.require_int_range("ticks", 0, minimum=1, maximum=100)
        with self.assertRaisesRegex(ValueError, "ticks must be at most 100"):
            api.require_int_range("ticks", 101, minimum=1, maximum=100)

    def test_run_cli_prints_short_error_without_traceback(self):
        script = ROOT / "scripts" / "stock_chart.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--count",
                "0",
                "--rsi-period",
                "0",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_run_cli_handles_missing_input_file_without_traceback(self):
        script = ROOT / "scripts" / "screener_count.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--filters-file",
                "/tmp/tossinvest-missing-filter-file.json",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
