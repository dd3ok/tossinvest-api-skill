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


if __name__ == "__main__":
    unittest.main()
