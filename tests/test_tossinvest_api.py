import subprocess
import sys
import unittest
from pathlib import Path

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

    def test_request_json_rejects_unapproved_cert_paths_before_network(self):
        with self.assertRaisesRegex(RuntimeError, "not in the approved"):
            api.request_json(
                "/api/v1/certificates/mutation",
                base_url="https://wts-cert-api.tossinvest.com",
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
