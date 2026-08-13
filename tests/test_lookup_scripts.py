import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

_calendar_spec = importlib.util.spec_from_file_location(
    "tossinvest_calendar_script",
    ROOT / "scripts" / "calendar.py",
)
calendar = importlib.util.module_from_spec(_calendar_spec)
assert _calendar_spec.loader is not None
_calendar_spec.loader.exec_module(calendar)

import community_comments
import dashboard_ranking
import feed
import filings
import financials
import indices
import market_search
import news
import page_api_check
import pension_fund_trend
import quote
import screener_count
import sector
import stock_chart
import stock_page
import stock_summary
import theme
import trading_trend


class QuoteScriptTests(unittest.TestCase):
    def test_build_quote_path_uses_v3_quotes(self):
        self.assertEqual(
            quote.build_quote_path("005930", "krx", None, None),
            "/api/v3/stock-prices/A005930/quotes?investMode=krx",
        )

    def test_build_ticks_path_includes_count_and_view_type(self):
        self.assertEqual(
            quote.build_ticks_path("A005930", "krx", "krx", 5),
            "/api/v2/stock-prices/A005930/ticks?viewType=krx&count=5&investMode=krx",
        )

    def test_fetch_quote_rejects_excessive_tick_count_before_network(self):
        with self.assertRaisesRegex(ValueError, "ticks must be at most 100"):
            quote.fetch_quote(
                "A005930",
                invest_mode="krx",
                view_type=None,
                fallback_krx=None,
                tick_count=101,
            )


class StockChartScriptTests(unittest.TestCase):
    def test_build_chart_path_uses_c_chart_with_range_and_query(self):
        self.assertEqual(
            stock_chart.build_chart_path("005930", "kr-s", "day:1", 61, "all", "krx", True),
            "/api/v1/c-chart/kr-s/A005930/day:1?count=61&session=all&investMode=krx&useAdjustedRate=true",
        )

    def test_build_chart_path_allows_us_securities_type_with_observed_ranges(self):
        self.assertEqual(
            stock_chart.build_chart_path("US20100311002", "us-s", "day:1", 5, "all", "krx", True),
            "/api/v1/c-chart/us-s/US20100311002/day:1?count=5&session=all&investMode=krx&useAdjustedRate=true",
        )

    def test_build_chart_path_rejects_unverified_selectors(self):
        with self.assertRaisesRegex(ValueError, "securities_type must be one of"):
            stock_chart.build_chart_path("005930", "account", "day:1", 61, "all", "krx", True)
        with self.assertRaisesRegex(ValueError, "range_value must be one of"):
            stock_chart.build_chart_path("005930", "kr-s", "../day:1", 61, "all", "krx", True)

    def test_fetch_chart_rejects_non_positive_count_before_network(self):
        with self.assertRaisesRegex(ValueError, "count must be at least 1"):
            stock_chart.fetch_chart(
                "A005930",
                securities_type="kr-s",
                range_value="day:1",
                count=0,
                session="all",
                invest_mode="krx",
                use_adjusted_rate=True,
                from_datetime=None,
                currency=None,
                rsi_period=None,
                sma_periods=[],
                ema_periods=[],
                bollinger_period=None,
                bollinger_stddev=2.0,
                include_macd=False,
                macd_fast=12,
                macd_slow=26,
                macd_signal=9,
            )

    def test_calculate_rsi_returns_wilder_values_for_candles(self):
        candles = [{"close": close} for close in [44, 44.15, 43.9, 44.35, 44.7, 44.25]]
        enriched = stock_chart.add_rsi(candles, period=3)
        self.assertIsNone(enriched[0]["rsi3"])
        self.assertIsNone(enriched[2]["rsi3"])
        self.assertAlmostEqual(enriched[3]["rsi3"], 70.59, places=2)
        self.assertAlmostEqual(enriched[4]["rsi3"], 81.82, places=2)
        self.assertAlmostEqual(enriched[5]["rsi3"], 47.12, places=2)

    def test_add_sma_and_ema_use_close_prices(self):
        candles = [{"close": close} for close in [10, 11, 13, 12, 14]]
        with_sma = stock_chart.add_sma(candles, period=3)
        with_ema = stock_chart.add_ema(candles, period=3)
        self.assertEqual([row["sma3"] for row in with_sma], [None, None, 11.33, 12.0, 13.0])
        self.assertEqual([row["ema3"] for row in with_ema], [None, None, 11.33, 11.67, 12.83])

    def test_indicators_calculate_chronologically_and_keep_response_order(self):
        candles = [
            {"dt": "2026-01-03T00:00:00+09:00", "close": 13},
            {"dt": "2026-01-02T00:00:00+09:00", "close": 11},
            {"dt": "2026-01-01T00:00:00+09:00", "close": 10},
        ]
        enriched = stock_chart.add_sma(candles, period=2)
        self.assertEqual([row["dt"] for row in enriched], [row["dt"] for row in candles])
        self.assertEqual([row["sma2"] for row in enriched], [12.0, 10.5, None])

    def test_add_bollinger_bands_uses_sample_window(self):
        candles = [{"close": close} for close in [10, 11, 13, 12, 14]]
        enriched = stock_chart.add_bollinger_bands(candles, period=3, stddev=2.0)
        self.assertIsNone(enriched[1]["bb3Middle"])
        self.assertEqual(enriched[2]["bb3Middle"], 11.33)
        self.assertEqual(enriched[2]["bb3Upper"], 13.83)
        self.assertEqual(enriched[2]["bb3Lower"], 8.84)

    def test_add_macd_uses_configurable_ema_periods(self):
        candles = [{"close": close} for close in [10, 11, 13, 12, 14, 15, 14, 16]]
        enriched = stock_chart.add_macd(candles, fast_period=3, slow_period=5, signal_period=2)
        self.assertIsNone(enriched[3]["macd"])
        self.assertEqual(enriched[4]["macd"], 0.83)
        self.assertIsNone(enriched[4]["macdSignal"])
        self.assertEqual(enriched[5]["macdSignal"], 0.88)
        self.assertEqual(enriched[5]["macdHistogram"], 0.04)
        self.assertEqual(enriched[7]["macd"], 0.76)
        self.assertEqual(enriched[7]["macdSignal"], 0.74)
        self.assertEqual(enriched[7]["macdHistogram"], 0.02)


class FilingsScriptTests(unittest.TestCase):
    def test_build_filings_path_uses_company_code(self):
        self.assertEqual(
            filings.build_filings_path("A005930", 1, 3, None),
            "/api/v1/stock-detail/companies/005930/filings?number=1&size=3",
        )


class StockSummaryScriptTests(unittest.TestCase):
    def test_merge_summary_returns_selected_price_for_code(self):
        summary = stock_summary.merge_summary(
            "005930",
            info={"code": "A005930", "name": "삼성전자"},
            price_rows=[{"code": "A000660"}, {"code": "A005930", "close": 70000}],
            overview={"marketValueKrw": 100},
        )
        self.assertEqual(summary["code"], "A005930")
        self.assertEqual(summary["price"], {"code": "A005930", "close": 70000})
        self.assertEqual(summary["overview"], {"marketValueKrw": 100})


class ThemeScriptTests(unittest.TestCase):
    def test_build_theme_ranking_path_uses_tag(self):
        self.assertEqual(
            theme.build_theme_ranking_path("kr"),
            "/api/v1/rankings/contents/tics_margin_depth1/tags/kr",
        )

    def test_build_theme_news_path_includes_size(self):
        self.assertEqual(
            theme.build_theme_news_path("42", 3),
            "/api/v2/news/tics/42?size=3",
        )

    def test_build_theme_details_path_uses_tics_id(self):
        self.assertEqual(
            theme.build_theme_details_path("289"),
            "/api/v1/tics/289/details",
        )

    def test_build_theme_company_ranking_path_maps_marketcap(self):
        self.assertEqual(
            theme.build_theme_company_ranking_path("289", "marketcap"),
            "/api/v1/companies/tics/rankings?ticsId=289&ticsRanking=1",
        )

    def test_build_current_dashboard_theme_ranking_body(self):
        self.assertEqual(
            theme.build_dashboard_theme_ranking_body("us", "1d"),
            {"nation": "US", "duration": "1d"},
        )
        with self.assertRaisesRegex(ValueError, "duration must be one of: 1d"):
            theme.build_dashboard_theme_ranking_body("us", "20d")

    def test_build_sector_stock_and_etf_requests(self):
        self.assertEqual(
            theme.build_sector_stocks_path("925"),
            "/api/v2/dashboard/wts/overview/tics/925/stocks",
        )
        self.assertEqual(
            theme.build_sector_stocks_body("us", "volume", "asc", 2),
            {"nation": "US", "sortBy": "VOLUME", "sortOrder": "ASC", "page": 2},
        )
        self.assertEqual(
            theme.build_sector_etfs_path("925"),
            "/api/v2/dashboard/wts/overview/tics/925/etfs",
        )
        self.assertEqual(
            theme.build_sector_etfs_body("all", "expense-ratio", "desc", True, 1),
            {
                "nation": "ALL",
                "sortBy": "EXPENSE_RATIO",
                "sortOrder": "DESC",
                "includeLeverageInverse": True,
                "page": 1,
            },
        )


class SectorScriptTests(unittest.TestCase):
    def test_build_sector_ranking_body_maps_home_filters(self):
        self.assertEqual(
            sector.build_sector_ranking_body("us", "1m", "trading-amount"),
            {"nation": "US", "duration": "1m", "sortBy": "TRADING_AMOUNT"},
        )

    def test_build_sector_stocks_body_uses_one_based_page_and_sort(self):
        self.assertEqual(
            sector.build_sector_stocks_body("all", "trading-value", "asc", 2),
            {
                "nation": "ALL",
                "sortBy": "TRADING_VALUE",
                "sortOrder": "ASC",
                "page": 2,
            },
        )

    def test_build_sector_etfs_body_preserves_leverage_filter(self):
        self.assertEqual(
            sector.build_sector_etfs_body("us", "expense-ratio", "desc", False, 1),
            {
                "nation": "US",
                "sortBy": "EXPENSE_RATIO",
                "sortOrder": "DESC",
                "includeLeverageInverse": False,
                "page": 1,
            },
        )

    def test_build_sector_news_path_uses_number_query(self):
        self.assertEqual(
            sector.build_sector_news_path("79", 2),
            "/api/v2/dashboard/wts/overview/tics/79/news?number=2",
        )

    def test_build_sector_comparison_path_uses_public_index_allowlist(self):
        self.assertEqual(
            sector.build_sector_comparison_path("79", "us", "SPX.CBI"),
            "/api/v1/dashboard/wts/overview/tics/79/comparison-chart?"
            "nation=US&securitiesType=STOCK&indicatorCode=SPX.CBI",
        )
        with self.assertRaisesRegex(ValueError, "indicator-code must be one of"):
            sector.build_sector_comparison_path("79", "us", "DJI.DJI")

    def test_sector_builders_reject_invalid_id_and_page_before_network(self):
        with self.assertRaisesRegex(ValueError, "tics-id"):
            sector.build_sector_overview_path("../79")
        with self.assertRaisesRegex(ValueError, "stock-page must be at least 1"):
            sector.build_sector_stocks_body("kr", "market-cap", "desc", 0)

    def test_sector_builders_reject_unobserved_selectors_before_network(self):
        with self.assertRaisesRegex(ValueError, "nation must be one of"):
            sector.build_sector_ranking_body("account", "1m", "trading-amount")
        with self.assertRaisesRegex(ValueError, "duration must be one of"):
            sector.build_sector_simple_path("79", "kr", "all")
        with self.assertRaisesRegex(ValueError, "stock-sort must be one of"):
            sector.build_sector_stocks_body("kr", "price", "desc", 1)
        with self.assertRaisesRegex(ValueError, "etf-order must be one of"):
            sector.build_sector_etfs_body("all", "trading-value", "sideways", False, 1)

    @patch("sector.api.get_result", return_value={})
    def test_sector_detail_reports_request_and_snapshot_provenance(self, get_result):
        payload = sector.fetch_sector_detail(
            tics_id="79",
            nation="us",
            duration="1m",
            stock_nation="us",
            stock_sort="market-cap",
            stock_order="desc",
            stock_page=2,
            etf_nation="all",
            etf_sort="trading-value",
            etf_order="desc",
            etf_page=3,
            include_leverage_inverse=True,
            news_page=4,
            include_comparison=True,
            indicator_code="SPX.CBI",
        )
        self.assertEqual(get_result.call_count, 6)
        self.assertEqual(payload["_meta"]["catalogCheckedAt"], "2026-08-04")
        self.assertEqual(payload["_meta"]["transport"], "rest_snapshot")
        self.assertEqual(payload["_meta"]["pagination"]["stocks"]["pageSize"], 10)
        self.assertEqual(payload["_meta"]["pagination"]["news"]["pageSize"], 5)
        self.assertEqual(payload["_meta"]["pagination"]["etfs"]["clientMaxPage"], 100)
        self.assertEqual(payload["request"]["stocks"]["page"], 2)
        self.assertEqual(payload["request"]["comparison"]["indicatorCode"], "SPX.CBI")

    @patch("sector.api.get_result")
    def test_sector_detail_validates_all_inputs_before_network(self, get_result):
        common = {
            "tics_id": "79",
            "nation": "us",
            "duration": "1m",
            "stock_nation": "us",
            "stock_sort": "market-cap",
            "stock_order": "desc",
            "stock_page": 1,
            "etf_nation": "all",
            "etf_sort": "trading-value",
            "etf_order": "desc",
            "etf_page": 1,
            "include_leverage_inverse": True,
        }
        with self.assertRaisesRegex(ValueError, "news-page must be at least 1"):
            sector.fetch_sector_detail(
                **common,
                news_page=0,
                include_comparison=False,
                indicator_code="SPX.CBI",
            )
        with self.assertRaisesRegex(ValueError, "indicator-code must be one of"):
            sector.fetch_sector_detail(
                **common,
                news_page=1,
                include_comparison=True,
                indicator_code="DJI.DJI",
            )
        get_result.assert_not_called()


class PensionFundTrendScriptTests(unittest.TestCase):
    def test_year_windows_validate_dates_and_order(self):
        self.assertEqual(
            pension_fund_trend.year_windows("2025-12-31", "2026-01-02"),
            [("2025-12-31", "2025-12-31"), ("2026-01-01", "2026-01-02")],
        )
        with self.assertRaisesRegex(ValueError, "from must be a valid YYYY-MM-DD"):
            pension_fund_trend.year_windows("2026-02-30", "2026-03-01")
        with self.assertRaisesRegex(ValueError, "start date"):
            pension_fund_trend.year_windows("2026-03-02", "2026-03-01")

    def test_year_window_rejects_out_of_range_year(self):
        with self.assertRaisesRegex(ValueError, "year must be between"):
            pension_fund_trend.year_window(10000)

    @patch("pension_fund_trend.api.request_json")
    def test_fixed_trend_normalizes_code_and_builds_encoded_query(self, request_json):
        request_json.return_value = {"result": []}
        self.assertEqual(pension_fund_trend.fixed_trend("005930", "2026-01-01", "2026-01-02"), [])
        request_json.assert_called_once_with(
            "/api/v1/stock-infos/trade/trend/fixed-trading-trend?"
            "productCode=A005930&from=2026-01-01&to=2026-01-02"
        )

    @patch("pension_fund_trend.api.request_json")
    def test_fixed_trend_rejects_reversed_dates_before_network(self, request_json):
        with self.assertRaisesRegex(ValueError, "start date"):
            pension_fund_trend.fixed_trend("005930", "2026-01-02", "2026-01-01")
        request_json.assert_not_called()


class IndicesScriptTests(unittest.TestCase):
    def test_build_index_chart_path_keeps_step_and_encodes_query(self):
        self.assertEqual(
            indices.build_index_chart_path("KGG01P", "kr-s", "1d", "min:5", "krx"),
            "/api/v1/r-chart/kr-s/KGG01P/1d/min:5?session=main&investMode=krx&last=false",
        )

    def test_build_index_daily_quotes_path_supports_cursor_paging(self):
        self.assertEqual(
            indices.build_index_daily_quotes_path(
                "KGG01P",
                "auto",
                20,
                "2026-07-13T00:00:00+09:00",
            ),
            (
                "/api/v1/c-chart/kr-s/KGG01P/day:1?count=20"
                "&from=2026-07-13T00%3A00%3A00%2B09%3A00&useAdjustedRate=true"
            ),
        )

    def test_build_index_daily_quotes_path_requires_timezone_cursor(self):
        with self.assertRaisesRegex(ValueError, "must include a timezone"):
            indices.build_index_daily_quotes_path("KGG01P", "kr-s", 20, "2026-07-13T00:00:00")

    def test_index_builders_reject_unverified_selectors(self):
        with self.assertRaisesRegex(ValueError, "securities_type must be one of"):
            indices.build_index_chart_path("KGG01P", "account", "1d", "min:5", "krx")
        with self.assertRaisesRegex(ValueError, "indicator_type must be one of"):
            indices.build_indicator_path("account", "kr")
        with self.assertRaisesRegex(ValueError, "net_range must be one of"):
            indices.build_net_buying_range_path("KGG01P", "account", "2026-04-20", 5)
        with self.assertRaisesRegex(ValueError, "net_range must be one of"):
            indices.build_net_buying_range_path("KGG01P", "quarter", "2026-04-20", 5)

    def test_cli_rejects_invalid_net_buying_range_before_network(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "indices.py"),
                "--include-net-buying",
                "--net-buying-range",
                "quarter",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)
        self.assertIn("quarter", result.stderr)

    def test_build_index_info_path_uses_index_code(self):
        self.assertEqual(indices.build_index_info_path("KGG01P"), "/api/v2/index-infos/KGG01P")

    def test_build_index_paths_preserve_case_sensitive_indicator_codes(self):
        self.assertEqual(
            indices.build_index_info_path("RFU.GCv1"),
            "/api/v2/index-infos/RFU.GCv1",
        )
        self.assertEqual(
            indices.build_index_price_path("RFU.GCv1"),
            "/api/v1/index-prices/RFU.GCv1",
        )

    def test_infer_index_securities_type_for_dotted_indicator_codes(self):
        self.assertEqual(indices.infer_securities_type("RFU.GCv1", "auto"), "us-s")
        self.assertEqual(indices.infer_securities_type("ROB.US10YT-RR", "auto"), "us-s")
        self.assertEqual(indices.infer_securities_type("KR1BENCH0010", "auto"), "kr-s")
        with self.assertRaisesRegex(ValueError, "securities_type must be one of"):
            indices.infer_securities_type("RFU.GCv1", "commodity")

    def test_build_index_chart_path_infers_dotted_indicator_securities_type(self):
        self.assertEqual(
            indices.build_index_chart_path("RFU.GCv1", "auto", "1d", "min:5", "krx"),
            "/api/v1/r-chart/us-s/RFU.GCv1/1d/min:5?session=main&investMode=krx&last=false",
        )

    def test_resolve_chart_window_applies_presets_and_overrides(self):
        self.assertEqual(indices.resolve_chart_window("intraday", None, None), ("1d", "min:5"))
        self.assertEqual(indices.resolve_chart_window("quarter", None, None), ("3m", "day:1"))
        self.assertEqual(indices.resolve_chart_window("daily", None, "week:1"), ("1y", "week:1"))

    def test_build_indicator_widget_paths(self):
        self.assertEqual(
            indices.build_mini_chart_path(),
            "/api/v3/dashboard/wts/overview/indicator/mini-chart",
        )
        self.assertEqual(
            indices.build_related_etfs_path("RFU.GCv1"),
            "/api/v3/dashboard/wts/overview/indicator/RFU.GCv1/related-etfs",
        )

    def test_build_index_net_buying_paths(self):
        self.assertEqual(
            indices.build_net_buying_range_path("KGG01P", "week", "2026-04-20", 5),
            "/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=week&from=2026-04-20&count=5",
        )
        self.assertEqual(
            indices.build_net_buying_range_path("KGG01P", "month", "2026-06-08", 5),
            "/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=month&from=2026-06-08&count=5",
        )
        self.assertEqual(
            indices.build_net_buying_range_path("KGG01P", "year", "2026-06-08", 5),
            "/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=year&from=2026-06-08&count=5",
        )
        self.assertEqual(
            indices.build_net_buying_daily_path("KGG01P", "2026-04-20", 35),
            "/api/v1/stock-infos/index/net-buying/daily?code=KGG01P&count=35&from=2026-04-20",
        )

    def test_build_exchange_rates_path_uses_dashboard_widget(self):
        self.assertEqual(
            indices.build_exchange_rates_path(),
            "/api/v1/dashboard/wts/overview/exchange-rates",
        )

    def test_build_fx_chart_path_uses_exchange_rate_route(self):
        self.assertEqual(
            indices.build_fx_chart_path("1d", "min:5", "usd"),
            "/api/v1/r-chart/fx/EXCHANGE_RATE/1d/min:5?last=false&useAdjustedRate=true&currency=USD",
        )

    def test_infer_securities_type_uses_crypto_for_vwap_codes(self):
        self.assertEqual(indices.infer_securities_type("VWAP.KRW-BTC", "auto"), "crypto")

    def test_build_crypto_index_chart_path_uses_crypto_route(self):
        self.assertEqual(
            indices.build_index_chart_path("VWAP.KRW-BTC", "auto", "1d", "min:5", "krx"),
            "/api/v1/r-chart/crypto/VWAP.KRW-BTC/1d/min:5?session=main&investMode=krx&last=false",
        )

    def test_build_crypto_prices_path_uses_product_codes_query(self):
        self.assertEqual(
            indices.build_crypto_prices_path(["VWAP.KRW-BTC"]),
            "/api/v1/crypto-prices?productCodes=VWAP.KRW-BTC",
        )

    def test_build_product_exchange_rate_path_uses_currency_pair(self):
        self.assertEqual(
            indices.build_product_exchange_rate_path("usd", "krw"),
            "/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW",
        )

    def test_fetch_index_payload_wires_optional_crypto_and_exchange_rate_widgets(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            return {"path": path}

        original_get_result = indices.api.get_result
        try:
            indices.api.get_result = fake_get_result
            payload = indices.fetch_index_payload(
                code="VWAP.KRW-BTC",
                securities_type="auto",
                chart_preset="intraday",
                chart_range=None,
                step=None,
                invest_mode="krx",
                include_chart=False,
                include_fx_chart=False,
                include_indicators=False,
                include_exchange_rates=False,
                include_crypto_prices=True,
                include_product_exchange_rate=True,
                include_mini_chart=False,
                include_related_etfs=False,
                include_net_buying=False,
                fx_chart_range="1d",
                fx_step="min:5",
                fx_currency="USD",
                exchange_buy_currency="usd",
                exchange_sell_currency="krw",
                indicator_type="index",
                market="kr",
                net_buying_from="2026-05-29",
                net_buying_range="week",
                net_buying_count=5,
            )
        finally:
            indices.api.get_result = original_get_result

        self.assertIn("cryptoPrices", payload)
        self.assertIn("productExchangeRate", payload)
        self.assertIn(
            ("/api/v1/crypto-prices?productCodes=VWAP.KRW-BTC", {}),
            calls,
        )
        self.assertIn(
            ("/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW", {}),
            calls,
        )


class CalendarScriptTests(unittest.TestCase):
    def test_build_calendar_paths_use_current_public_routes(self):
        self.assertEqual(
            calendar.build_monthly_path("2026-05"),
            "/api/v4/calendar/monthly/2026-05",
        )
        self.assertEqual(
            calendar.build_key_events_path(),
            "/api/v1/calendar/ai-summary/key-events",
        )
        self.assertEqual(
            calendar.build_weekly_summary_path(),
            "/api/v1/nova-calendar/ai/summary/weekly",
        )
        self.assertEqual(
            calendar.build_overview_economic_events_path(),
            "/api/v2/dashboard/wts/overview/calendar/economic-events",
        )
        self.assertEqual(
            calendar.build_index_monthly_path("2026-06", "us"),
            "/api/v4/calendar/monthly/2026-06/index?countryType=us",
        )
        self.assertEqual(
            calendar.build_economic_indicator_path("USPMI=ECI", "2026-06-01"),
            "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-06-01",
        )
        self.assertEqual(
            calendar.build_economic_indicator_analysis_path(
                "2026-06-01T23:00:00",
                "USPMI=ECI",
            ),
            (
                "/api/v1/nova-calendar/ai/analysis/indicators"
                "?announceDateTime=2026-06-01T23%3A00%3A00&ricId=USPMI%3DECI"
            ),
        )

    def test_build_monthly_path_rejects_invalid_months(self):
        for value in ["2026-00", "2026-13", "202605", "../2026-05"]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "year-month must be YYYY-MM"):
                    calendar.build_monthly_path(value)

    def test_calendar_detail_builders_reject_unverified_values(self):
        with self.assertRaisesRegex(ValueError, "date must be YYYY-MM-DD"):
            calendar.build_economic_indicator_path("USPMI=ECI", "2026-6-1")
        with self.assertRaisesRegex(ValueError, "date must be a valid calendar date"):
            calendar.build_economic_indicator_path("USPMI=ECI", "2026-02-31")
        with self.assertRaisesRegex(ValueError, "announcement datetime"):
            calendar.build_economic_indicator_analysis_path("2026-06-01 23:00:00", "USPMI=ECI")
        with self.assertRaisesRegex(ValueError, "ric must"):
            calendar.build_economic_indicator_path("../account", "2026-06-01")
        with self.assertRaisesRegex(ValueError, "index-country must be one of"):
            calendar.build_index_monthly_path("2026-06", "all")

    def test_filter_monthly_events_maps_category_and_country_tabs(self):
        events = [
            {
                "id": {"group": "ECONOMIC"},
                "date": "2026-05-01",
                "view": {"economicIndicatorValue": {"countryType": "us"}},
            },
            {
                "id": {"group": "ECONOMIC"},
                "date": "2026-05-02",
                "view": {"economicIndicatorValue": {"countryType": "kr"}},
            },
            {
                "id": {"group": "KRX_EARNINGS_ANNOUNCEMENT"},
                "date": "2026-05-03",
                "stockEarnings": {"countryType": "kr"},
            },
            {
                "id": {"group": "USD_EARNINGS_ANNOUNCEMENT"},
                "date": "2026-05-04",
                "stockEarnings": {"countryType": "us"},
            },
            {
                "id": {"group": "HOLIDAY", "uniqueName": "20260505_CHILDREN_HOLIDAY_KR"},
                "date": "2026-05-05",
            },
            {
                "id": {"group": "COMPANY_EVENT"},
                "date": "2026-05-06",
                "excludeFromAll": True,
            },
        ]

        self.assertEqual(
            [event["date"] for event in calendar.filter_monthly_events(events, "economic", "us")],
            ["2026-05-01"],
        )
        self.assertEqual(
            [event["date"] for event in calendar.filter_monthly_events(events, "earnings", "kr")],
            ["2026-05-03"],
        )
        self.assertEqual(
            [event["date"] for event in calendar.filter_monthly_events(events, "all", "kr")],
            ["2026-05-02", "2026-05-03", "2026-05-05"],
        )

    def test_filter_monthly_events_rejects_non_dictionary_events(self):
        with self.assertRaisesRegex(RuntimeError, "monthly calendar event is not a dictionary"):
            calendar.filter_monthly_events([{"date": "2026-05-01"}, "bad-event"], "all", "all")

    def test_fetch_monthly_payload_applies_kind_aliases_before_network_result(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            return {
                "events": [
                    {
                        "id": {"group": "USD_EARNINGS_ANNOUNCEMENT"},
                        "date": "2026-05-04",
                        "stockEarnings": {"countryType": "us"},
                    },
                    {
                        "id": {"group": "KRX_EARNINGS_ANNOUNCEMENT"},
                        "date": "2026-05-03",
                        "stockEarnings": {"countryType": "kr"},
                    },
                ]
            }

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            payload = calendar.fetch_calendar("2026-05", "overseas", "all", "all")
        finally:
            calendar.api.get_result = original_get_result

        self.assertEqual(payload["kind"], "overseas")
        self.assertEqual(payload["category"], "all")
        self.assertEqual(payload["country"], "us")
        self.assertEqual([event["date"] for event in payload["events"]], ["2026-05-04"])
        self.assertEqual(
            calls,
            [
                (
                    "/api/v4/calendar/monthly/2026-05",
                    {"method": "POST", "body": {}, "base_url": calendar.CERT_BASE_URL},
                )
            ],
        )

    def test_fetch_monthly_payload_rejects_non_dictionary_result(self):
        def fake_get_result(path, **kwargs):
            return None

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(
                RuntimeError, "monthly calendar result is not a dictionary"
            ):
                calendar.fetch_calendar("2026-05", "monthly", "all", "all")
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_monthly_payload_rejects_missing_events(self):
        def fake_get_result(path, **kwargs):
            return {}

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(RuntimeError, "monthly calendar events is not a list"):
                calendar.fetch_calendar("2026-05", "monthly", "all", "all")
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_index_monthly_payload_uses_index_calendar_route(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            return {"events": [{"id": {"group": "ECONOMIC"}, "date": "2026-06-01"}]}

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            payload = calendar.fetch_calendar(
                "2026-06",
                "index-events",
                "all",
                "all",
                index_country="us",
            )
        finally:
            calendar.api.get_result = original_get_result

        self.assertEqual(payload["kind"], "index-events")
        self.assertEqual(payload["indexCountry"], "us")
        self.assertEqual(payload["totalEvents"], 1)
        self.assertEqual(
            calls,
            [
                (
                    "/api/v4/calendar/monthly/2026-06/index?countryType=us",
                    {"method": "POST", "body": {}, "base_url": calendar.CERT_BASE_URL},
                )
            ],
        )

    def test_fetch_index_monthly_payload_rejects_missing_events(self):
        def fake_get_result(path, **kwargs):
            return {}

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(RuntimeError, "index calendar events is not a list"):
                calendar.fetch_calendar(
                    "2026-06",
                    "index-events",
                    "all",
                    "all",
                    index_country="us",
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_economic_detail_can_include_ai_analysis(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            if path.startswith("/api/v1/calendar/economic-indicators/"):
                return {
                    "announcementDate": "2026-06-01",
                    "announcementTime": "23:00:00",
                    "indicatorDetail": {"ric": "USPMI=ECI"},
                }
            return {"title": "AI analysis", "contents": "public summary"}

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            payload = calendar.fetch_calendar(
                "2026-06",
                "economic-detail",
                "all",
                "all",
                ric="USPMI=ECI",
                announcement_date="2026-06-01",
                include_analysis=True,
            )
        finally:
            calendar.api.get_result = original_get_result

        self.assertEqual(payload["kind"], "economic-detail")
        self.assertEqual(payload["ric"], "USPMI=ECI")
        self.assertIn("analysis", payload)
        self.assertEqual(
            calls,
            [
                (
                    "/api/v1/calendar/economic-indicators/USPMI=ECI?announceDate=2026-06-01",
                    {"base_url": calendar.CERT_BASE_URL},
                ),
                (
                    (
                        "/api/v1/nova-calendar/ai/analysis/indicators"
                        "?announceDateTime=2026-06-01T23%3A00%3A00&ricId=USPMI%3DECI"
                    ),
                    {"base_url": calendar.CERT_BASE_URL},
                ),
            ],
        )

    def test_fetch_economic_detail_rejects_non_dictionary_result(self):
        def fake_get_result(path, **kwargs):
            return None

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(
                RuntimeError, "economic indicator result is not a dictionary"
            ):
                calendar.fetch_calendar(
                    "2026-06",
                    "economic-detail",
                    "all",
                    "all",
                    ric="USPMI=ECI",
                    announcement_date="2026-06-01",
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_economic_detail_analysis_requires_announcement_fields(self):
        def fake_get_result(path, **kwargs):
            return {
                "announcementDate": "2026-06-01",
                "indicatorDetail": {"ric": "USPMI=ECI"},
            }

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(
                RuntimeError, "economic indicator announcement date/time is missing"
            ):
                calendar.fetch_calendar(
                    "2026-06",
                    "economic-detail",
                    "all",
                    "all",
                    ric="USPMI=ECI",
                    announcement_date="2026-06-01",
                    include_analysis=True,
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_economic_detail_analysis_requires_detail_ric(self):
        def fake_get_result(path, **kwargs):
            return {
                "announcementDate": "2026-06-01",
                "announcementTime": "23:00:00",
                "indicatorDetail": {},
            }

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(RuntimeError, "economic indicator ric is missing"):
                calendar.fetch_calendar(
                    "2026-06",
                    "economic-detail",
                    "all",
                    "all",
                    ric="USPMI=ECI",
                    announcement_date="2026-06-01",
                    include_analysis=True,
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_economic_detail_analysis_rejects_malformed_response_datetime(self):
        def fake_get_result(path, **kwargs):
            return {
                "announcementDate": "2026-02-31",
                "announcementTime": "23:00:00",
                "indicatorDetail": {"ric": "USPMI=ECI"},
            }

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(RuntimeError, "malformed announcement datetime or RIC"):
                calendar.fetch_calendar(
                    "2026-06",
                    "economic-detail",
                    "all",
                    "all",
                    ric="USPMI=ECI",
                    announcement_date="2026-06-01",
                    include_analysis=True,
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_economic_detail_analysis_rejects_malformed_response_ric(self):
        def fake_get_result(path, **kwargs):
            return {
                "announcementDate": "2026-06-01",
                "announcementTime": "23:00:00",
                "indicatorDetail": {"ric": "../account"},
            }

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(RuntimeError, "malformed announcement datetime or RIC"):
                calendar.fetch_calendar(
                    "2026-06",
                    "economic-detail",
                    "all",
                    "all",
                    ric="USPMI=ECI",
                    announcement_date="2026-06-01",
                    include_analysis=True,
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_fetch_economic_detail_rejects_non_dictionary_analysis(self):
        def fake_get_result(path, **kwargs):
            if path.startswith("/api/v1/calendar/economic-indicators/"):
                return {
                    "announcementDate": "2026-06-01",
                    "announcementTime": "23:00:00",
                    "indicatorDetail": {"ric": "USPMI=ECI"},
                }
            return None

        original_get_result = calendar.api.get_result
        try:
            calendar.api.get_result = fake_get_result
            with self.assertRaisesRegex(
                RuntimeError, "economic indicator analysis is not a dictionary"
            ):
                calendar.fetch_calendar(
                    "2026-06",
                    "economic-detail",
                    "all",
                    "all",
                    ric="USPMI=ECI",
                    announcement_date="2026-06-01",
                    include_analysis=True,
                )
        finally:
            calendar.api.get_result = original_get_result

    def test_apply_event_window_limits_and_summarizes_output(self):
        events = [{"date": f"2026-05-{day:02d}"} for day in range(1, 6)]
        payload = {
            "kind": "monthly",
            "yearMonth": "2026-05",
            "category": "all",
            "country": "all",
            "totalEvents": 10,
            "events": events,
        }

        windowed = calendar.apply_event_window(payload, limit=2, offset=1, summary_only=False)

        self.assertEqual(windowed["filteredEvents"], 5)
        self.assertEqual(windowed["offset"], 1)
        self.assertEqual(windowed["limit"], 2)
        self.assertEqual(
            [event["date"] for event in windowed["events"]], ["2026-05-02", "2026-05-03"]
        )

        summary = calendar.apply_event_window(payload, limit=None, offset=0, summary_only=True)
        self.assertEqual(summary["filteredEvents"], 5)
        self.assertNotIn("events", summary)

        empty_window = calendar.apply_event_window(payload, limit=2, offset=99, summary_only=False)
        self.assertEqual(empty_window["filteredEvents"], 5)
        self.assertEqual(empty_window["events"], [])

        summary_payload = {"kind": "key-events", "eventsCount": 3}
        self.assertEqual(
            calendar.apply_event_window(
                summary_payload,
                limit=1,
                offset=1,
                summary_only=True,
            ),
            summary_payload,
        )

    def test_apply_event_window_rejects_invalid_bounds(self):
        payload = {"events": []}
        with self.assertRaisesRegex(ValueError, "limit must be at least 1"):
            calendar.apply_event_window(payload, limit=0, offset=0, summary_only=False)
        with self.assertRaisesRegex(ValueError, "limit must be at most 10000"):
            calendar.apply_event_window(payload, limit=10_001, offset=0, summary_only=False)
        with self.assertRaisesRegex(ValueError, "offset must be at least 0"):
            calendar.apply_event_window(payload, limit=None, offset=-1, summary_only=False)
        with self.assertRaisesRegex(ValueError, "offset must be at most 10000"):
            calendar.apply_event_window(payload, limit=None, offset=10_001, summary_only=False)

    def test_fetch_calendar_rejects_unverified_selectors(self):
        with self.assertRaisesRegex(ValueError, "kind must be one of"):
            calendar.fetch_calendar("2026-05", "account", "all", "all")
        with self.assertRaisesRegex(ValueError, "category must be one of"):
            calendar.fetch_calendar("2026-05", "monthly", "account", "all")
        with self.assertRaisesRegex(ValueError, "country must be one of"):
            calendar.fetch_calendar("2026-05", "monthly", "all", "account")


class JsonOnlyScriptCliTests(unittest.TestCase):
    def test_json_only_scripts_accept_format_json_alias(self):
        script_names = [
            "calendar.py",
            "community_comments.py",
            "dashboard_ranking.py",
            "feed.py",
            "financials.py",
            "indices.py",
            "market_search.py",
            "page_api_check.py",
            "quote.py",
            "screener_count.py",
            "stock_chart.py",
            "stock_page.py",
            "stock_summary.py",
            "theme.py",
            "trading_trend.py",
        ]
        for script_name in script_names:
            with self.subTest(script=script_name):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / script_name), "--help"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("--format {json}", result.stdout)


class DashboardRankingScriptTests(unittest.TestCase):
    def test_build_overview_ranking_body_defaults_filters(self):
        self.assertEqual(
            dashboard_ranking.build_overview_ranking_body(
                "biggest_market_amount", "all", "realtime", None
            ),
            {
                "id": "biggest_market_amount",
                "tag": "all",
                "duration": "realtime",
                "filters": [],
            },
        )

    def test_build_overview_ranking_body_rejects_unverified_selectors(self):
        with self.assertRaisesRegex(ValueError, "ranking_id must be one of"):
            dashboard_ranking.build_overview_ranking_body("account", "all", "realtime", None)
        with self.assertRaisesRegex(ValueError, "tag must be one of"):
            dashboard_ranking.build_overview_ranking_body(
                "biggest_market_amount", "account", "realtime", None
            )
        with self.assertRaisesRegex(ValueError, "duration must be one of"):
            dashboard_ranking.build_overview_ranking_body(
                "biggest_market_amount", "all", "30d", None
            )
        with self.assertRaisesRegex(ValueError, "filter must be one of"):
            dashboard_ranking.build_overview_ranking_body(
                "biggest_market_amount", "all", "realtime", ["ACCOUNT_DERIVED_FILTER"]
            )

    def test_build_overview_ranking_body_hides_observed_investment_risk_stocks(self):
        body = dashboard_ranking.build_overview_ranking_body(
            "biggest_total_amount",
            "us",
            "realtime",
            None,
            hide_investment_risk=True,
        )
        self.assertEqual(
            body["filters"],
            [
                "KRX_MANAGEMENT_STOCK",
                "MARKET_CAP_GREATER_THAN_50M",
                "STOCKS_PRICE_GREATER_THAN_ONE_DOLLAR",
            ],
        )

    def test_normalize_ranking_filters_normalizes_and_deduplicates(self):
        self.assertEqual(
            dashboard_ranking.normalize_ranking_filters(
                ["market_cap_greater_than_50m", "MARKET_CAP_GREATER_THAN_50M"]
            ),
            ["MARKET_CAP_GREATER_THAN_50M"],
        )

    def test_build_investor_rankings_path_includes_size(self):
        self.assertEqual(
            dashboard_ranking.build_investor_rankings_path(100),
            "/api/v1/dashboard/wts/overview/rankings/by-investors?size=100",
        )

    def test_select_investor_rankings_applies_buy_or_sell_side(self):
        result = {
            "rankings": {
                "foreigner": {
                    "basedAt": "2026-08-13",
                    "type": "FOREIGNER",
                    "buyStocks": [{"code": "A005930"}],
                    "sellStocks": [{"code": "A000660"}],
                }
            }
        }

        self.assertEqual(
            dashboard_ranking.select_investor_rankings(result, "buy")["foreigner"]["stocks"],
            [{"code": "A005930"}],
        )
        self.assertEqual(
            dashboard_ranking.select_investor_rankings(result, "sell")["foreigner"]["stocks"],
            [{"code": "A000660"}],
        )

    def test_build_live_chart_body_matches_home_url_params(self):
        self.assertEqual(
            dashboard_ranking.build_live_chart_body("biggest_total_amount", "KR", "realtime", None),
            {
                "id": "biggest_total_amount",
                "tag": "kr",
                "duration": "realtime",
                "filters": [],
            },
        )

    def test_build_live_chart_body_accepts_all_visible_periods(self):
        for duration in ["1d", "5d", "20d", "60d", "120d", "240d", "realtime"]:
            with self.subTest(duration=duration):
                body = dashboard_ranking.build_live_chart_body(
                    "biggest_market_amount", "US", duration, None
                )
                self.assertEqual(body["duration"], duration)

    def test_build_overview_signals_path_joins_product_codes(self):
        self.assertEqual(
            dashboard_ranking.build_overview_signals_path(["005930", "A000660"]),
            "/api/v1/dashboard/wts/overview/signals?codes=A005930%2CA000660",
        )

    def test_fetch_current_overview_indicator_uses_public_get_route(self):
        with patch.object(
            dashboard_ranking.api,
            "get_result",
            return_value={"leftSection": [], "rightSection": []},
        ) as get_result:
            payload = dashboard_ranking.fetch_overview_indicator()

        self.assertEqual(payload["kind"], "indicator")
        get_result.assert_called_once_with(
            "/api/v4/dashboard/wts/overview/indicator",
            base_url=dashboard_ranking.CERT_BASE_URL,
        )

    def test_help_mentions_signals_mode(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "dashboard_ranking.py"), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("signals", result.stdout)
        self.assertIn("indicator", result.stdout)
        self.assertIn("--signal-code", result.stdout)
        self.assertIn("--hide-investment-risk", result.stdout)
        self.assertIn("MARKET_CAP_GREATER_THAN_50M", result.stdout)


class FeedScriptTests(unittest.TestCase):
    def test_build_recommended_alias_uses_current_public_cert_route(self):
        self.assertEqual(
            feed.build_feed_path("recommended", None),
            "/api/v4/feed/recommend/ranking-posts",
        )

    def test_build_feed_path_for_recommended_ranking(self):
        self.assertEqual(
            feed.build_feed_path("recommended-ranking", None),
            "/api/v4/feed/recommend/ranking-posts",
        )

    def test_build_news_body_requires_index_code_for_index_news(self):
        self.assertEqual(
            feed.build_news_body("INDEX", "KGG01P"),
            {"type": "INDEX", "indexCode": "KGG01P"},
        )

    def test_recommended_ranking_uses_observed_cert_host(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            return {"feeds": [], "key": None}

        with patch.object(feed.api, "get_result", fake_get_result):
            payload = feed.fetch_feed("recommended-ranking", None)

        self.assertEqual(payload["kind"], "recommended-ranking")
        self.assertEqual(payload["feeds"], [])
        self.assertNotIn("result", payload)
        self.assertEqual(calls[0][0], "/api/v4/feed/recommend/ranking-posts")
        self.assertEqual(calls[0][1]["base_url"], feed.CERT_BASE_URL)

    def test_recommended_feed_sanitizes_profile_and_social_metadata(self):
        result = {
            "feeds": [
                {
                    "type": "COMMENT",
                    "comment": {
                        "commentId": 10,
                        "authorUserProfileId": "private-profile",
                        "author": {
                            "nickname": "public name",
                            "userProfileId": "private-profile",
                            "profilePictureUrl": "https://example.com/private.png",
                        },
                        "message": {"message": "mail me@example.com"},
                        "statistic": {"likeCount": 1, "isFollowing": True},
                    },
                    "recommendationAttribution": {"accountId": "private-account"},
                }
            ],
            "key": {"lastRecommendId": "next:10"},
        }

        sanitized = feed.sanitize_recommended_feed_result(result)

        self.assertEqual(sanitized["feedCount"], 1)
        self.assertTrue(sanitized["hasNext"])
        self.assertEqual(sanitized["nextLastRecommendId"], "next:10")
        self.assertEqual(
            sanitized["feeds"][0]["comment"]["message"]["message"],
            "mail [redacted-email]",
        )
        dumped = repr(sanitized)
        self.assertNotIn("private-profile", dumped)
        self.assertNotIn("private-account", dumped)
        self.assertNotIn("profilePictureUrl", dumped)
        self.assertNotIn("isFollowing", dumped)

    def test_sanitize_community_ranking_strips_profile_identifiers(self):
        item = {
            "type": "USER_PROFILE",
            "target": {
                "nickname": "public name",
                "profilePictureUrl": "https://example.com/profile.png",
                "userProfileId": "private-profile-id",
            },
            "profitLossAmountKrw": 1000,
            "profitLossRateKrw": 0.1,
            "isFollowing": True,
            "isMyProfile": False,
        }
        sanitized = feed.sanitize_community_ranking_item(item, 1)
        self.assertEqual(
            sanitized,
            {
                "rank": 1,
                "nickname": "public name",
                "type": "USER_PROFILE",
                "profitLossAmountKrw": 1000,
                "profitLossRateKrw": 0.1,
            },
        )
        self.assertNotIn("private-profile-id", repr(sanitized))

        nested = feed.sanitize_community_ranking_item(
            {
                "type": {"profileUrl": "https://example.com/private"},
                "target": {"nickname": {"userProfileId": "private-profile-id"}},
                "profitLossAmountKrw": {"accountId": "private-account"},
            },
            2,
        )
        self.assertEqual(nested, {"rank": 2})


class CommunityCommentsScriptTests(unittest.TestCase):
    def test_build_stock_comments_path_uses_public_stock_query(self):
        self.assertEqual(
            community_comments.build_stock_comments_path("US20100311002", "popular", None),
            ("/api/v4/comments?subjectType=STOCK&subjectId=US20100311002&commentSortType=POPULAR"),
        )
        self.assertEqual(
            community_comments.build_stock_comments_path("US20100311002", "recent", 287893608),
            (
                "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                "&commentSortType=RECENT&lastCommentId=287893608"
            ),
        )

    def test_build_stock_comments_path_rejects_unverified_inputs(self):
        with self.assertRaisesRegex(ValueError, "sort must be one of"):
            community_comments.build_stock_comments_path("US20100311002", "following", None)
        with self.assertRaisesRegex(ValueError, "last_comment_id must contain digits"):
            community_comments.build_stock_comments_path("US20100311002", "popular", "abc")

    def test_build_lounge_comments_path_uses_bounded_public_query(self):
        self.assertEqual(
            community_comments.build_lounge_comments_path("lounge_193394", "recent", None),
            ("/api/v4/comments?subjectType=LOUNGE&subjectId=LOUNGE_193394&commentSortType=RECENT"),
        )
        with self.assertRaisesRegex(ValueError, "LOUNGE_<digits>"):
            community_comments.build_lounge_comments_path("LOUNGE_account", "recent", None)

    def test_build_community_post_path_uses_reply_cursor(self):
        self.assertEqual(
            community_comments.build_community_post_path(309855290, None),
            "/api/v1/comments/309855290/replies",
        )
        self.assertEqual(
            community_comments.build_community_post_path(309855290, 309855291),
            "/api/v1/comments/309855290/replies?lastReplyId=309855291",
        )
        with self.assertRaisesRegex(ValueError, "last_reply_id must contain digits"):
            community_comments.build_community_post_path(309855290, "bad")
        for unicode_cursor in ["１２３", "١٢٣"]:
            with self.subTest(cursor=unicode_cursor):
                with self.assertRaisesRegex(ValueError, "last_reply_id must contain digits"):
                    community_comments.build_community_post_path(309855290, unicode_cursor)

    def test_sanitize_comment_removes_profile_and_personal_flags(self):
        raw = {
            "commentId": 287893106,
            "type": "USER_COMMENT",
            "authorUserProfileId": "profile-123",
            "author": {
                "userProfileId": "profile-123",
                "nickname": "public nickname",
                "profilePictureUrl": "https://example.com/avatar.png",
                "shortDescription": "profile text",
            },
            "message": {"title": "title", "message": "call me 010-1234-5678"},
            "board": {"subjectType": "STOCK", "subjectId": "US20100311002", "topic": "SOXL"},
            "statistic": {
                "likeCount": 3,
                "replyCount": 1,
                "readCount": 10,
                "followerCount": 99,
                "isFollowing": True,
                "isBookmarked": True,
                "isMyProfile": False,
            },
            "holding": {"shareHoldingStatus": "HOLDING"},
            "createdAt": "2026-07-08T12:00:00+09:00",
        }

        sanitized = community_comments.sanitize_comment(raw)
        dumped = repr(sanitized)

        self.assertEqual(sanitized["commentId"], 287893106)
        self.assertEqual(sanitized["authorNickname"], "public nickname")
        self.assertEqual(sanitized["message"]["message"], "call me [redacted-phone]")
        self.assertNotIn("profile-123", dumped)
        self.assertNotIn("profilePictureUrl", dumped)
        self.assertNotIn("followerCount", dumped)
        self.assertNotIn("isFollowing", dumped)
        self.assertNotIn("isBookmarked", dumped)
        self.assertNotIn("isMyProfile", dumped)

    def test_sanitize_comment_redacts_common_phone_formats(self):
        for raw_phone in [
            "010 1234 5678",
            "010.1234.5678",
            "+82-10-1234-5678",
            "+82 10 1234 5678",
        ]:
            with self.subTest(raw_phone=raw_phone):
                sanitized = community_comments.sanitize_comment(
                    {"message": {"message": f"call {raw_phone}"}}
                )
                self.assertEqual(sanitized["message"]["message"], "call [redacted-phone]")

    def test_sanitize_comment_removes_profile_id_from_public_mention_markup(self):
        sanitized = community_comments.sanitize_post_comment(
            {
                "id": 1,
                "message": "#[써니님v](2782547) 의견에 동의해요",
                "author": {"nickname": "public"},
            }
        )

        self.assertEqual(sanitized["message"]["message"], "#[써니님v] 의견에 동의해요")
        self.assertNotIn("2782547", repr(sanitized))

    def test_sanitize_post_comment_drops_unexpected_structured_scalar_fields(self):
        sanitized = community_comments.sanitize_post_comment(
            {
                "id": {"accountId": "private-comment-id"},
                "type": {"accountId": "private-type"},
                "author": {
                    "nickname": {"userProfileId": "private-author-profile"},
                },
                "title": {"accountId": "private-title"},
                "message": {"accountId": "private-message"},
                "subjectType": {"accountId": "private-subject-type"},
                "subjectId": {"accountId": "private-subject-id"},
                "stockCode": {"accountId": "private-stock-code"},
                "topic": {"accountId": "private-topic"},
                "likeCount": {"accountId": "private-like-count"},
                "replyCount": {"accountId": "private-reply-count"},
                "readCount": {"accountId": "private-read-count"},
                "instrumentHoldingStatus": {"accountId": "private-holding"},
                "createdAt": {"accountId": "private-created-at"},
                "updatedAt": {"accountId": "private-updated-at"},
                "edited": {"accountId": "private-edited"},
                "media": [{"type": {"accountId": "private-media-type"}}],
            }
        )

        self.assertNotIn("private-", repr(sanitized))
        self.assertNotIn("commentId", sanitized)
        self.assertEqual(sanitized["media"], {"count": 1, "types": []})

    def test_fetch_stock_comments_uses_key_pagination_and_sanitizes_rows(self):
        responses = [
            {
                "results": [
                    {
                        "commentId": 1,
                        "author": {"nickname": "n1", "userProfileId": "u1"},
                        "message": {"message": "first"},
                    }
                ],
                "hasNext": True,
                "key": 1,
            },
            {
                "results": [
                    {
                        "commentId": 2,
                        "author": {"nickname": "n2", "userProfileId": "u2"},
                        "message": {"message": "second"},
                    }
                ],
                "hasNext": False,
                "key": None,
            },
        ]
        paths = []

        def fake_get_result(path, **kwargs):
            paths.append((path, kwargs))
            return responses.pop(0)

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_stock_comments(
                "US20100311002",
                sort="popular",
                pages=2,
                limit=10,
                include_replies=False,
            )

        self.assertEqual(payload["pagesFetched"], 2)
        self.assertEqual([row["commentId"] for row in payload["comments"]], [1, 2])
        self.assertIn("lastCommentId=1", paths[1][0])
        self.assertEqual(paths[0][1]["base_url"], community_comments.CERT_BASE_URL)

    def test_fetch_stock_comments_accepts_explicit_start_cursor(self):
        def fake_get_result(path, **kwargs):
            self.assertIn("lastCommentId=77", path)
            return {"results": [], "hasNext": False, "key": None}

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_stock_comments(
                "A005930",
                sort="popular",
                pages=1,
                limit=5,
                include_replies=False,
                last_comment_id="77",
            )

        self.assertEqual(payload["lastCommentId"], "77")

    def test_fetch_stock_comments_resolves_display_symbol_before_comment_lookup(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            if path == "/api/v2/stock-infos/code-or-symbol/NVDA":
                return {"code": "US19990122001", "symbol": "NVDA"}
            if path == (
                "/api/v4/comments?subjectType=STOCK&subjectId=US19990122001&commentSortType=POPULAR"
            ):
                return {
                    "results": [{"commentId": 1, "author": {"nickname": "nvidia holder"}}],
                    "hasNext": False,
                    "key": None,
                }
            raise AssertionError(path)

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_stock_comments(
                "NVDA",
                sort="popular",
                pages=1,
                limit=5,
                include_replies=False,
            )

        self.assertEqual(payload["subjectId"], "US19990122001")
        self.assertEqual(payload["comments"][0]["authorNickname"], "nvidia holder")
        self.assertEqual(calls[1][1]["base_url"], community_comments.CERT_BASE_URL)

    def test_fetch_stock_comments_uses_last_emitted_id_when_limit_truncates_page(self):
        def fake_get_result(path, **kwargs):
            self.assertEqual(
                path,
                (
                    "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002"
                    "&commentSortType=POPULAR"
                ),
            )
            self.assertEqual(kwargs["base_url"], community_comments.CERT_BASE_URL)
            return {
                "results": [
                    {"commentId": 1, "author": {"nickname": "first"}},
                    {"commentId": 2, "author": {"nickname": "second"}},
                ],
                "hasNext": True,
                "key": 2,
            }

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_stock_comments(
                "US20100311002",
                sort="popular",
                pages=1,
                limit=1,
                include_replies=False,
            )

        self.assertEqual([row["commentId"] for row in payload["comments"]], [1])
        self.assertEqual(payload["nextLastCommentId"], "1")

    def test_comment_limit_exposes_continuation_even_on_server_last_page(self):
        with patch.object(
            community_comments.api,
            "get_result",
            return_value={
                "results": [
                    {"commentId": 1, "author": {"nickname": "first"}},
                    {"commentId": 2, "author": {"nickname": "second"}},
                ],
                "hasNext": False,
                "key": None,
            },
        ):
            payload = community_comments.fetch_stock_comments(
                "US20100311002",
                sort="popular",
                pages=1,
                limit=1,
                include_replies=False,
            )

        self.assertTrue(payload["hasNext"])
        self.assertEqual(payload["nextLastCommentId"], "1")

    def test_fetch_community_post_pages_and_sanitizes_permalink_payload(self):
        responses = [
            {
                "topic": "삼성전자",
                "comment": {
                    "id": 100,
                    "type": "COMMENT",
                    "message": "parent",
                    "topic": {"accountId": "private-nested-topic"},
                    "createdAt": "2026-08-13T09:00:00+09:00",
                    "author": {
                        "nickname": "parent author",
                        "id": "private-parent",
                        "profilePictureUrl": "https://example.com/parent.png",
                    },
                    "replyCount": 2,
                },
                "replies": {
                    "body": [
                        {
                            "id": 101,
                            "message": "first 010-1234-5678",
                            "author": {"nickname": "first", "id": "private-first"},
                        }
                    ],
                    "hasNext": True,
                },
            },
            {
                "topic": "삼성전자",
                "comment": {"id": 100, "message": "parent", "author": {}},
                "replies": {
                    "body": [
                        {
                            "id": 102,
                            "message": "second@example.com",
                            "author": {"nickname": "second", "id": "private-second"},
                        }
                    ],
                    "hasNext": False,
                },
            },
        ]
        paths = []

        def fake_get_result(path, **kwargs):
            paths.append((path, kwargs))
            return responses.pop(0)

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_community_post(100, pages=2, limit=10)

        self.assertEqual(payload["postId"], "100")
        self.assertEqual(payload["pagesFetched"], 2)
        self.assertFalse(payload["hasNext"])
        self.assertEqual(payload["comment"]["createdAt"], "2026-08-13T09:00:00+09:00")
        self.assertEqual([row["commentId"] for row in payload["replies"]], [101, 102])
        self.assertEqual(
            payload["replies"][0]["message"]["message"],
            "first [redacted-phone]",
        )
        self.assertEqual(
            payload["replies"][1]["message"]["message"],
            "[redacted-email]",
        )
        self.assertIn("lastReplyId=101", paths[1][0])
        self.assertNotIn("private-", repr(payload))

    def test_fetch_community_post_does_not_emit_structured_topic_metadata(self):
        with patch.object(
            community_comments.api,
            "get_result",
            return_value={
                "topic": {"profileId": "private", "title": "topic"},
                "comment": {"id": 100, "message": "parent", "author": {}},
                "replies": {"body": [], "hasNext": False},
            },
        ):
            payload = community_comments.fetch_community_post(100, pages=1, limit=5)

        self.assertIsNone(payload["topic"])
        self.assertNotIn("private", repr(payload))

    def test_fetch_community_post_accepts_explicit_start_cursor(self):
        def fake_get_result(path, **kwargs):
            self.assertEqual(path, "/api/v1/comments/100/replies?lastReplyId=99")
            return {
                "topic": "topic",
                "comment": {"id": 100, "message": "parent", "author": {}},
                "replies": {"body": [], "hasNext": False},
            }

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_community_post(
                100,
                pages=1,
                limit=5,
                last_reply_id="99",
            )

        self.assertEqual(payload["lastReplyId"], "99")

    def test_fetch_comment_replies_sanitizes_reply_rows(self):
        def fake_get_result(path, **kwargs):
            self.assertEqual(path, "/api/v2/comments/287893106/replies")
            self.assertEqual(kwargs["base_url"], community_comments.CERT_BASE_URL)
            return {
                "results": [
                    {
                        "commentId": 287893107,
                        "author": {
                            "nickname": "reply author",
                            "userProfileId": "reply-profile",
                            "profilePictureUrl": "https://example.com/reply.png",
                        },
                        "message": {"message": "reply 01012345678"},
                        "statistic": {"likeCount": 1, "isFollowing": True},
                    }
                ]
            }

        with patch.object(community_comments.api, "get_result", fake_get_result):
            replies = community_comments.fetch_comment_replies(287893106)

        dumped = repr(replies)
        self.assertEqual(replies[0]["commentId"], 287893107)
        self.assertEqual(replies[0]["authorNickname"], "reply author")
        self.assertEqual(replies[0]["message"]["message"], "reply [redacted-phone]")
        self.assertNotIn("reply-profile", dumped)
        self.assertNotIn("profilePictureUrl", dumped)
        self.assertNotIn("isFollowing", dumped)

    def test_fetch_stock_comments_can_attach_sanitized_replies(self):
        responses = {
            "/api/v4/comments?subjectType=STOCK&subjectId=US20100311002&commentSortType=POPULAR": {
                "results": [{"commentId": 1, "author": {"nickname": "parent"}}],
                "hasNext": False,
                "key": None,
            },
            "/api/v2/comments/1/replies": {
                "results": [
                    {
                        "commentId": 2,
                        "author": {"nickname": "child", "userProfileId": "child-profile"},
                        "message": {"message": "child@example.com"},
                    }
                ]
            },
        }

        def fake_get_result(path, **kwargs):
            self.assertEqual(kwargs["base_url"], community_comments.CERT_BASE_URL)
            return responses[path]

        with patch.object(community_comments.api, "get_result", fake_get_result):
            payload = community_comments.fetch_stock_comments(
                "US20100311002",
                sort="popular",
                pages=1,
                limit=10,
                include_replies=True,
            )

        self.assertEqual(payload["comments"][0]["replies"][0]["commentId"], 2)
        self.assertEqual(
            payload["comments"][0]["replies"][0]["message"]["message"],
            "[redacted-email]",
        )
        self.assertNotIn("child-profile", repr(payload))


class StockPageScriptTests(unittest.TestCase):
    def test_build_ai_signal_detail_path_for_stock(self):
        self.assertEqual(
            stock_page.build_ai_signal_detail_path("US20100311002", "stocks"),
            (
                "/api/v1/dashboard/wts/overview/ai-signals/detail"
                "?productCode=US20100311002&productType=STOCKS"
            ),
        )

    def test_build_public_stock_status_helper_paths(self):
        self.assertEqual(
            stock_page.build_red_flags_path("005930"),
            "/api/v1/stock-infos/A005930/red-flags",
        )
        self.assertEqual(
            stock_page.build_trading_status_path("005930"),
            "/api/v3/trading/order/A005930/trading-status",
        )
        self.assertEqual(
            stock_page.build_trading_analysis_path("005930"),
            "/api/v1/trading/analysis/productCode/A005930",
        )

    def test_fetch_stock_page_composes_public_main_card_data(self):
        calls = []

        def fake_get_result(path, **kwargs):
            calls.append((path, kwargs))
            if path == "/api/v2/stock-infos/code-or-symbol/SOXL":
                return {"code": "US20100311002", "name": "SOXL", "logoImageUrl": "logo.png"}
            if path == "/api/v3/stock-prices/details?productCodes=US20100311002":
                return [{"code": "US20100311002", "close": 240515}]
            if path.startswith("/api/v1/dashboard/wts/overview/ai-signals/detail"):
                return {"reasoning": {"description": "AI reason"}, "terms": {}}
            raise AssertionError(path)

        with (
            patch.object(stock_page.api, "get_result", fake_get_result),
            patch.object(
                stock_page.community_comments,
                "fetch_stock_comments",
                return_value={"comments": [{"commentId": 1}]},
            ) as fetch_comments,
        ):
            payload = stock_page.fetch_stock_page(
                "SOXL",
                include_ai_detail=True,
                include_comments=True,
                comment_sort="popular",
                comment_limit=5,
                comment_pages=1,
                include_replies=False,
            )

        self.assertEqual(payload["productCode"], "US20100311002")
        self.assertEqual(payload["info"]["logoImageUrl"], "logo.png")
        self.assertEqual(payload["price"], {"code": "US20100311002", "close": 240515})
        self.assertEqual(payload["aiSignalDetail"]["reasoning"]["description"], "AI reason")
        self.assertEqual(payload["community"]["comments"], [{"commentId": 1}])
        fetch_comments.assert_called_once_with(
            "US20100311002",
            sort="popular",
            pages=1,
            limit=5,
            include_replies=False,
        )


class ScreenerCountScriptTests(unittest.TestCase):
    def test_build_screener_common_presets_path(self):
        self.assertEqual(
            screener_count.build_common_presets_path(True),
            "/api/v2/screener/presets/common?useCustom=true",
        )

    def test_build_screener_search_modal_path(self):
        self.assertEqual(
            screener_count.build_search_modal_path(),
            "/api/v2/screener/screen/search/modal",
        )

    def test_build_screener_filter_metadata_bodies(self):
        filter_body = screener_count.build_rsi_filter("oversold")
        self.assertEqual(
            screener_count.build_filter_base_body("KR", filter_body["id"]),
            {"filterId": filter_body["id"], "nation": "kr"},
        )
        self.assertEqual(
            screener_count.build_filter_range_body("US", filter_body),
            {"filter": filter_body, "nation": "us"},
        )

    def test_filter_metadata_rejects_unselected_or_undocumented_filter(self):
        with self.assertRaisesRegex(ValueError, "filter metadata count"):
            screener_count.validate_filter_metadata_selection([])
        with self.assertRaisesRegex(ValueError, "undocumented screener filter id"):
            screener_count.build_filter_base_body("kr", "ACCOUNT_FILTER")
        with self.assertRaisesRegex(ValueError, "undocumented screener filter id"):
            screener_count.build_filter_range_body("kr", {"id": "ACCOUNT_FILTER", "conditions": []})

    def test_filter_metadata_selection_is_bounded_and_unique(self):
        selected = [screener_count.build_rsi_filter("oversold")]
        self.assertEqual(
            screener_count.validate_filter_metadata_selection(selected),
            selected,
        )
        with self.assertRaisesRegex(ValueError, "unique filter ids"):
            screener_count.validate_filter_metadata_selection(selected * 2)
        with self.assertRaisesRegex(ValueError, "at most 10"):
            screener_count.validate_filter_metadata_selection(
                [
                    {"id": filter_id, "conditions": []}
                    for filter_id in sorted(screener_count.ALLOWED_FILTER_IDS)[:11]
                ]
            )

    def test_build_screener_count_body_normalizes_nation(self):
        self.assertEqual(
            screener_count.build_count_body("KR"),
            {"filters": [], "nation": "kr"},
        )

    def test_build_rsi_filter_for_oversold_screen(self):
        self.assertEqual(
            screener_count.build_rsi_filter("oversold"),
            {
                "id": "RSI_범위",
                "conditions": [
                    {
                        "id": "NUMBER_RANGE_DEFAULT",
                        "type": "NUMBER_RANGE",
                        "value": {
                            "from": None,
                            "to": 30,
                            "includeFrom": None,
                            "includeTo": True,
                        },
                    }
                ],
            },
        )

    def test_build_rsi_filter_for_overbought_screen(self):
        self.assertEqual(
            screener_count.build_rsi_filter("overbought")["conditions"][0]["value"],
            {"from": 70, "to": None, "includeFrom": True, "includeTo": None},
        )

    def test_build_screener_results_body_includes_paging_param(self):
        filters = [screener_count.build_rsi_filter("oversold")]
        self.assertEqual(
            screener_count.build_screen_body("US", filters, 5),
            {"filters": filters, "nation": "us", "pagingParam": {"number": 1, "size": 5}},
        )

    def test_build_screener_sort_uses_observed_column_shape(self):
        self.assertEqual(
            screener_count.build_sort("market-cap", "desc"),
            {"column": "C_시가총액", "label": "시가총액", "order": "DESC"},
        )

    def test_build_screener_sort_supports_current_price_change_column(self):
        self.assertEqual(
            screener_count.build_sort("price-change-1w", "desc"),
            {"column": "C_주가등락률_1W", "label": "주가등락률", "order": "DESC"},
        )

    def test_build_screener_results_body_includes_sort_when_requested(self):
        self.assertEqual(
            screener_count.build_screen_body(
                "kr",
                [],
                size=10,
                page=2,
                sort=screener_count.build_sort("volume", "asc"),
            ),
            {
                "filters": [],
                "nation": "kr",
                "pagingParam": {"number": 2, "size": 10},
                "sort": {"column": "C_거래량", "label": "거래량", "order": "ASC"},
            },
        )

    def test_build_price_moving_average_cross_filter(self):
        self.assertEqual(
            screener_count.build_technical_filter("price-ma-cross-up"),
            {
                "id": "CUSTOM_주가_이동평균선_돌파",
                "conditions": [
                    {
                        "id": "주가_이동평균선_돌파",
                        "type": "PRICE_MOVING_AVERAGE_CROSS_ARRAY",
                        "value": [{"period": 20, "within": 5, "crossDirection": "upward"}],
                    }
                ],
            },
        )

    def test_build_volume_moving_average_cross_filter(self):
        self.assertEqual(
            screener_count.build_technical_filter("volume-ma-cross-down")["conditions"][0],
            {
                "id": "이동평균선_돌파",
                "type": "MOVING_AVERAGE_CROSS_ARRAY",
                "value": [
                    {
                        "shortPeriod": 5,
                        "longPeriod": 20,
                        "within": 5,
                        "crossDirection": "downward",
                    }
                ],
            },
        )

    def test_build_bollinger_cross_filter(self):
        self.assertEqual(
            screener_count.build_technical_filter("bollinger-lower-down")["conditions"][0]["value"],
            [{"within": 5, "crossBand": "lower", "crossDirection": "downward"}],
        )

    def test_build_price_change_filter(self):
        self.assertEqual(
            screener_count.build_price_filter("price-change-5d-up-5"),
            {
                "id": "주가등락률",
                "conditions": [
                    {"id": "기간_선택_DAY_TO_MONTH", "type": "PERIOD", "value": "DAY_5"},
                    {
                        "id": "NUMBER_RANGE_DEFAULT",
                        "type": "NUMBER_RANGE",
                        "value": {
                            "from": 0.05,
                            "to": None,
                            "includeFrom": True,
                            "includeTo": None,
                        },
                    },
                ],
            },
        )

    def test_build_consecutive_fall_filter(self):
        self.assertEqual(
            screener_count.build_price_filter("consecutive-fall-5")["conditions"][0],
            {
                "id": "NUMBER_RANGE_DEFAULT",
                "type": "NUMBER_RANGE",
                "value": {"from": 5, "to": None, "includeFrom": True, "includeTo": None},
            },
        )

    def test_build_new_high_filter(self):
        self.assertEqual(
            screener_count.build_price_filter("new-high-52w-within-20d")["conditions"][0],
            {
                "id": "WEEK_NEW_PRICE_HIT",
                "type": "WEEK_NEW_PRICE_HIT_WITHIN",
                "value": {"numberOfWeeks": 52, "within": 20},
            },
        )

    def test_validate_filters_rejects_undocumented_filter_id(self):
        with self.assertRaisesRegex(ValueError, "undocumented screener filter id"):
            screener_count.validate_filters([{"id": "ACCOUNT_DERIVED_FILTER", "conditions": []}])

    def test_validate_filters_accepts_example_filter_shapes(self):
        filters = [
            screener_count.build_rsi_filter("oversold"),
            screener_count.build_price_filter("new-high-52w-within-20d"),
            screener_count.build_technical_filter("price-ma-cross-up"),
        ]
        self.assertEqual(screener_count.validate_filters(filters), filters)


class MarketSearchScriptTests(unittest.TestCase):
    def test_build_search_body_uses_visible_home_sections(self):
        self.assertEqual(
            market_search.build_search_body(" Samsung ", ["product", "news"]),
            {
                "query": "Samsung",
                "sections": [
                    {"type": "PRODUCT", "option": {"addIntegratedSearchResult": True}},
                    {"type": "NEWS"},
                ],
            },
        )

    def test_build_search_body_rejects_blank_and_unknown_sections(self):
        with self.assertRaisesRegex(ValueError, "must not be blank"):
            market_search.build_search_body(" ", None)
        with self.assertRaisesRegex(ValueError, "section must be one of"):
            market_search.build_search_body("Samsung", ["account"])

    def test_sanitize_search_results_keeps_public_market_fields_only(self):
        result = [
            {
                "type": "PRODUCT",
                "data": {
                    "type": "PRODUCT",
                    "items": [
                        {
                            "productCode": "A005930",
                            "productName": "Samsung Electronics",
                            "symbol": "005930",
                            "market": "KOSPI",
                            "stockStatus": {"accountOnly": True},
                        }
                    ],
                },
            }
        ]
        self.assertEqual(
            market_search.sanitize_search_results(result, 10),
            [
                {
                    "type": "PRODUCT",
                    "items": [
                        {
                            "productCode": "A005930",
                            "productName": "Samsung Electronics",
                            "symbol": "005930",
                            "market": "KOSPI",
                        }
                    ],
                }
            ],
        )


class NewsScriptTests(unittest.TestCase):
    def test_build_company_news_path_uses_company_code(self):
        self.assertEqual(
            news.build_company_news_path("A005930", 3, 2, "latest"),
            "/api/v2/news/companies/005930?size=3&number=2&orderBy=latest",
        )
        self.assertEqual(
            news.build_company_news_path("A005930", 20, 1, "relevant"),
            "/api/v2/news/companies/005930?size=20&orderBy=relevant",
        )

    def test_build_company_news_path_rejects_invalid_paging_and_order(self):
        with self.assertRaisesRegex(ValueError, "page must be at least 1"):
            news.build_company_news_path("A005930", 3, 0, "latest")
        with self.assertRaisesRegex(ValueError, "order-by must be one of"):
            news.build_company_news_path("A005930", 3, 1, "account")


class FinancialsScriptTests(unittest.TestCase):
    def test_build_financial_path_selects_company_endpoint(self):
        self.assertEqual(
            financials.build_financial_path("005930", "comprehensive"),
            "/api/v2/companies/A005930/financial-statements/comprehensive",
        )

    def test_build_financial_path_selects_stock_info_endpoint(self):
        self.assertEqual(
            financials.build_financial_path("A005930", "valuation"),
            "/api/v2/stock-infos/evaluation/A005930",
        )

    def test_validate_body_rejects_custom_body_without_explicit_opt_in(self):
        with self.assertRaisesRegex(ValueError, "custom financial POST bodies require"):
            financials.validate_body({"period": "quarterly"}, allow_custom=False)

    def test_validate_body_accepts_empty_default_body(self):
        self.assertEqual(financials.validate_body({}, allow_custom=False), {})


class TradingTrendScriptTests(unittest.TestCase):
    def test_normalize_investor_rows_maps_live_domestic_investor_taxonomy(self):
        rows = [
            {
                "baseDate": "2026-04-24",
                "netIndividualsBuyVolume": 6603714,
                "netForeignerBuyVolume": -5636939,
                "netInstitutionBuyVolume": -979657,
                "netFinancialInvestmentBuyVolume": -131380,
                "netInsuranceBuyVolume": -33737,
                "netOtherFinancialInstitutionsBuyVolume": -9516,
                "netTrustBuyVolume": -17438,
                "netPrivateEquityFundBuyVolume": -757178,
                "netPensionFundBuyVolume": -3787,
                "netBankBuyVolume": -26621,
                "netOtherCorporationBuyVolume": -23714,
            }
        ]

        normalized = trading_trend.normalize_investor_rows(rows)

        self.assertEqual(
            [(item["investorType"], item["labelKo"], item["netBuyVolume"]) for item in normalized],
            [
                ("individual", "개인", 6603714),
                ("foreigner", "외국인", -5636939),
                ("institution_total", "기관계", -979657),
                ("financial_investment", "금융투자", -131380),
                ("insurance", "보험", -33737),
                ("other_financial", "기타금융", -9516),
                ("trust", "투신", -17438),
                ("private_equity_fund", "사모펀드", -757178),
                ("pension_fund", "연기금등", -3787),
                ("bank", "은행", -26621),
                ("other_corporation", "기타법인", -23714),
            ],
        )
        self.assertEqual({item["date"] for item in normalized}, {"2026-04-24"})

    def test_normalize_investor_result_accepts_explicit_empty_primary_lists(self):
        self.assertEqual(
            trading_trend.normalize_investor_result(
                {
                    "body": [],
                    "tradingTrends": [{"baseDate": "2026-04-24", "netForeignerBuyVolume": 1}],
                }
            ),
            [],
        )
        self.assertEqual(
            trading_trend.normalize_investor_result(
                {
                    "data": {
                        "content": [],
                        "items": [{"baseDate": "2026-04-24", "netForeignerBuyVolume": 1}],
                    }
                }
            ),
            [],
        )

    def test_build_trend_path_for_recent_investor_trend(self):
        self.assertEqual(
            trading_trend.build_trend_path("005930", "investor", 20, None, None),
            "/api/v1/stock-infos/trade/trend/trading-trend?productCode=A005930&size=20",
        )

    def test_build_trend_path_for_fixed_window(self):
        self.assertEqual(
            trading_trend.build_trend_path("A005930", "fixed", None, "2026-01-01", "2026-01-31"),
            "/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A005930&from=2026-01-01&to=2026-01-31",
        )

    def test_build_trend_path_for_lending_trading(self):
        self.assertEqual(
            trading_trend.build_trend_path("005930", "lending-trading", 3, None, None),
            "/api/v1/mds/info/lending-trading?stockCode=A005930&number=1&size=3",
        )

    def test_build_trend_path_for_short_selling_trend(self):
        self.assertEqual(
            trading_trend.build_trend_path("A005930", "short-selling-trend", 3, None, None),
            "/api/v1/mds/info/short-selling-trend?stockCode=A005930&number=1&size=3",
        )

    def test_build_trend_path_for_cfd(self):
        self.assertEqual(
            trading_trend.build_trend_path("A005930", "cfd", 3, None, None),
            "/api/v1/mds/info/cfd?stockCode=A005930&number=1&size=3",
        )

    def test_build_mds_path_accepts_previous_response_page_and_key(self):
        self.assertEqual(
            trading_trend.build_mds_info_path(
                "A005930",
                "credit",
                5,
                page=2,
                key="2026-08-06",
            ),
            ("/api/v1/mds/info/credit?stockCode=A005930&number=2&size=5&key=2026-08-06"),
        )
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            trading_trend.build_mds_info_path(
                "A005930",
                "credit",
                5,
                page=2,
                key="not-a-date",
            )
        for non_canonical_key in ["20260813", "2026-W33-4"]:
            with self.subTest(key=non_canonical_key):
                with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
                    trading_trend.build_mds_info_path(
                        "A005930",
                        "credit",
                        5,
                        page=2,
                        key=non_canonical_key,
                    )


class PageApiCheckScriptTests(unittest.TestCase):
    def test_build_check_plan_maps_stock_pages_to_read_only_endpoints(self):
        plan = page_api_check.build_check_plan(
            "A005930",
            ["order", "analytics", "news", "transaction-status"],
            start="2026-04-01",
            end="2026-04-24",
            news_size=5,
            filing_size=5,
            tick_count=5,
            candle_count=5,
        )

        self.assertEqual(plan[0].page, "order")
        self.assertEqual(plan[0].path, "/api/v1/stock-detail/ui/A005930/common")
        self.assertIn(
            "/api/v2/news/companies/005930?size=5",
            [item.path for item in plan],
        )
        self.assertIn(
            "/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A005930&from=2026-04-01&to=2026-04-24",
            [item.path for item in plan],
        )
        self.assertIn(
            "/api/v1/mds/info/lending-trading?stockCode=A005930&number=1&size=5",
            [item.path for item in plan],
        )
        self.assertIn(
            "/api/v1/mds/info/short-selling-trend?stockCode=A005930&number=1&size=5",
            [item.path for item in plan],
        )
        self.assertIn(
            "/api/v1/mds/info/cfd?stockCode=A005930&number=1&size=5",
            [item.path for item in plan],
        )

    def test_transaction_status_plan_uses_shared_mds_info_types(self):
        plan = page_api_check.build_check_plan(
            "A005930",
            ["transaction-status"],
            start="2026-04-01",
            end="2026-04-24",
            news_size=5,
            filing_size=5,
            tick_count=5,
            candle_count=5,
        )
        mds_paths = {item.path for item in plan if item.path.startswith("/api/v1/mds/info/")}
        self.assertEqual(
            mds_paths,
            {
                trading_trend.build_mds_info_path("A005930", mds_type, 5)
                for mds_type in trading_trend.MDS_INFO_TYPES
            },
        )

    def test_build_check_plan_excludes_order_account_and_mutation_paths(self):
        plan = page_api_check.build_check_plan(
            "A005930",
            ["order"],
            start="2026-04-01",
            end="2026-04-24",
            news_size=5,
            filing_size=5,
            tick_count=5,
            candle_count=5,
        )

        forbidden_fragments = ["/trading/order", "/orderable", "/account", "/balance"]
        for item in plan:
            with self.subTest(path=item.path):
                self.assertFalse(any(fragment in item.path for fragment in forbidden_fragments))

    def test_build_check_plan_rejects_non_kr_product_codes(self):
        for invalid_code in ["US20100311002", "ASECRET", "A１２３４５６"]:
            with self.subTest(code=invalid_code):
                with self.assertRaisesRegex(ValueError, "require a KR product code"):
                    page_api_check.build_check_plan(
                        invalid_code,
                        ["order"],
                        start="2026-04-01",
                        end="2026-04-24",
                        news_size=5,
                        filing_size=5,
                        tick_count=5,
                        candle_count=5,
                    )

    def test_summarize_result_reports_shapes_without_storing_full_payload(self):
        summary = page_api_check.summarize_result(
            {
                "pagingParam": {"number": 1},
                "body": [
                    {
                        "id": "news1",
                        "title": "sample",
                        "summary": "long content should not be copied",
                    }
                ],
                "lastPage": False,
            }
        )

        self.assertEqual(
            summary,
            {
                "type": "object",
                "keys": ["pagingParam", "body", "lastPage"],
                "rowKeys": {"body": ["id", "title", "summary"]},
            },
        )

    def test_run_checks_rejects_missing_result_and_stops(self):
        plan = [
            page_api_check.EndpointCheck("order", "first", "GET", "/api/v1/first"),
            page_api_check.EndpointCheck("order", "second", "GET", "/api/v1/second"),
        ]
        with patch.object(
            page_api_check.api,
            "request_json",
            side_effect=[{"data": []}, {"result": {"ok": True}}],
        ) as request_json:
            with self.assertRaisesRegex(RuntimeError, "missing top-level result"):
                page_api_check.run_checks(plan)

        self.assertEqual(request_json.call_count, 1)

    def test_run_checks_fails_fast_on_transport_or_access_error(self):
        plan = [
            page_api_check.EndpointCheck("order", "first", "GET", "/api/v1/first"),
            page_api_check.EndpointCheck("order", "second", "GET", "/api/v1/second"),
        ]
        with patch.object(
            page_api_check.api,
            "request_json",
            side_effect=RuntimeError("HTTP 429; stop automated retries"),
        ) as request_json:
            with self.assertRaisesRegex(RuntimeError, "HTTP 429"):
                page_api_check.run_checks(plan)

        self.assertEqual(request_json.call_count, 1)

    def test_build_check_plan_rejects_unknown_pages(self):
        with self.assertRaisesRegex(ValueError, "unknown page"):
            page_api_check.build_check_plan(
                "A005930",
                ["account"],
                start="2026-04-01",
                end="2026-04-24",
                news_size=5,
                filing_size=5,
                tick_count=5,
                candle_count=5,
            )


if __name__ == "__main__":
    unittest.main()
