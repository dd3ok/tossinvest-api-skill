import subprocess
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tossinvest_api as api


class TossInvestApiTests(unittest.TestCase):
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
            "/api/v4/feed/recommend/ranking-posts",
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

            def read(self):
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

        with patch.object(api.urllib.request, "urlopen", fake_urlopen):
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
        self.assertIn("wts-cert-api.tossinvest.com/api/v4/comments", captured[0]["url"])

    def test_calendar_request_body_serialization_matches_observed_routes(self):
        captured = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
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

        with patch.object(api.urllib.request, "urlopen", fake_urlopen):
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
