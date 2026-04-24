import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import dashboard_ranking
import feed
import filings
import financials
import indices
import news
import quote
import screener_count
import stock_chart
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


class IndicesScriptTests(unittest.TestCase):
    def test_build_index_chart_path_keeps_step_and_encodes_query(self):
        self.assertEqual(
            indices.build_index_chart_path("KGG01P", "kr-s", "1d", "min:5", "krx"),
            "/api/v1/r-chart/kr-s/KGG01P/1d/min:5?session=main&investMode=krx&last=false",
        )

    def test_index_builders_reject_unverified_selectors(self):
        with self.assertRaisesRegex(ValueError, "securities_type must be one of"):
            indices.build_index_chart_path("KGG01P", "account", "1d", "min:5", "krx")
        with self.assertRaisesRegex(ValueError, "indicator_type must be one of"):
            indices.build_indicator_path("account", "kr")
        with self.assertRaisesRegex(ValueError, "net_range must be one of"):
            indices.build_net_buying_range_path("KGG01P", "account", "2026-04-20", 5)

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


class JsonOnlyScriptCliTests(unittest.TestCase):
    def test_json_only_scripts_accept_format_json_alias(self):
        script_names = [
            "dashboard_ranking.py",
            "feed.py",
            "financials.py",
            "indices.py",
            "quote.py",
            "screener_count.py",
            "stock_chart.py",
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

    def test_build_investor_rankings_path_includes_size(self):
        self.assertEqual(
            dashboard_ranking.build_investor_rankings_path(100),
            "/api/v1/dashboard/wts/overview/rankings/by-investors?size=100",
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


class FeedScriptTests(unittest.TestCase):
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


class NewsScriptTests(unittest.TestCase):
    def test_build_company_news_path_uses_company_code(self):
        self.assertEqual(
            news.build_company_news_path("A005930", 3),
            "/api/v2/news/companies/005930?size=3",
        )


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


if __name__ == "__main__":
    unittest.main()
