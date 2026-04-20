import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import filings
import dashboard_ranking
import feed
import financials
import indices
import news
import quote
import screener_count
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

    def test_build_index_info_path_uses_index_code(self):
        self.assertEqual(indices.build_index_info_path("KGG01P"), "/api/v2/index-infos/KGG01P")


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

    def test_build_investor_rankings_path_includes_size(self):
        self.assertEqual(
            dashboard_ranking.build_investor_rankings_path(100),
            "/api/v1/dashboard/wts/overview/rankings/by-investors?size=100",
        )


class FeedScriptTests(unittest.TestCase):
    def test_build_feed_path_for_recommended_ranking(self):
        self.assertEqual(
            feed.build_feed_path("recommended-ranking", None),
            "/api/v4/feed/recommend/ranking-posts",
        )

    def test_build_feed_path_for_subscription_posts(self):
        self.assertEqual(
            feed.build_feed_path("subscription", None),
            "/api/v3/feed/subscription/posts?filterType=COMMENT",
        )

    def test_build_news_body_requires_index_code_for_index_news(self):
        self.assertEqual(
            feed.build_news_body("INDEX", "KGG01P"),
            {"type": "INDEX", "indexCode": "KGG01P"},
        )


class ScreenerCountScriptTests(unittest.TestCase):
    def test_build_screener_count_body_normalizes_nation(self):
        self.assertEqual(
            screener_count.build_count_body("KR"),
            {"filters": [], "nation": "kr"},
        )


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


class TradingTrendScriptTests(unittest.TestCase):
    def test_build_trend_path_for_recent_investor_trend(self):
        self.assertEqual(
            trading_trend.build_trend_path("005930", "investor", 20, None, None),
            "/api/v1/stock-infos/trade/trend/trading-trend?productCode=A005930&size=20",
        )

    def test_build_trend_path_for_fixed_window(self):
        self.assertEqual(
            trading_trend.build_trend_path(
                "A005930", "fixed", None, "2026-01-01", "2026-01-31"
            ),
            "/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A005930&from=2026-01-01&to=2026-01-31",
        )


if __name__ == "__main__":
    unittest.main()
