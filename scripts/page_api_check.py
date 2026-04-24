#!/usr/bin/env python3
"""Smoke-check read-only TossInvest APIs used by selected stock pages."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import tossinvest_api as api

DEFAULT_PAGES = ("order", "analytics", "news", "transaction-status")
MAX_SUMMARY_KEYS = 24
MAX_SUMMARY_ROW_KEYS = 18
ROW_KEYS = (
    "body",
    "candles",
    "compositions",
    "majorList",
    "minorList",
    "items",
    "graph",
    "table",
    "tables",
    "graphs",
    "top5ActivityList",
    "indicatorSections",
    "analystReportGroups",
)


@dataclass(frozen=True)
class EndpointCheck:
    page: str
    purpose: str
    method: str
    path: str
    body: dict[str, Any] | None = None


@dataclass(frozen=True)
class CheckContext:
    product_code: str
    company_code: str
    start: str
    end: str
    news_size: int
    filing_size: int
    tick_count: int
    candle_count: int


def build_check_plan(
    code: str,
    pages: list[str],
    *,
    start: str,
    end: str,
    news_size: int,
    filing_size: int,
    tick_count: int,
    candle_count: int,
) -> list[EndpointCheck]:
    product_code = api.normalize_product_code(code)
    context = CheckContext(
        product_code=product_code,
        company_code=api.to_company_code(product_code),
        start=start,
        end=end,
        news_size=news_size,
        filing_size=filing_size,
        tick_count=tick_count,
        candle_count=candle_count,
    )
    page_builders = {
        "order": _order_checks,
        "analytics": _analytics_checks,
        "news": _news_checks,
        "transaction-status": _transaction_status_checks,
    }
    plan: list[EndpointCheck] = []
    for page in pages:
        if page not in page_builders:
            raise ValueError(f"unknown page: {page}")
        plan.extend(page_builders[page](context))
    return plan


def _order_checks(context: CheckContext) -> list[EndpointCheck]:
    return [
        EndpointCheck(
            "order",
            "common stock detail UI",
            "GET",
            f"/api/v1/stock-detail/ui/{context.product_code}/common",
        ),
        EndpointCheck(
            "order",
            "stock header info",
            "GET",
            f"/api/v1/stock-infos/header/{context.product_code}",
        ),
        EndpointCheck(
            "order",
            "WTS badges",
            "GET",
            f"/api/v1/stock-infos/{context.product_code}/wts-badges",
        ),
        EndpointCheck(
            "order", "stock metadata", "GET", f"/api/v2/stock-infos/{context.product_code}"
        ),
        EndpointCheck(
            "order",
            "price details",
            "GET",
            api.build_path("/api/v3/stock-prices/details", {"productCodes": context.product_code}),
        ),
        EndpointCheck(
            "order",
            "quote book",
            "GET",
            api.build_path(
                f"/api/v3/stock-prices/{context.product_code}/quotes", {"investMode": "krx"}
            ),
        ),
        EndpointCheck(
            "order",
            "intraday ticks",
            "GET",
            api.build_path(
                f"/api/v2/stock-prices/{context.product_code}/ticks",
                {"viewType": "krx", "count": context.tick_count, "investMode": "krx"},
            ),
        ),
        EndpointCheck(
            "order",
            "upper/lower bounds",
            "GET",
            f"/api/v2/stock-prices/{context.product_code}/upper-lower",
        ),
        EndpointCheck(
            "order",
            "daily c-chart candles",
            "GET",
            api.build_path(
                f"/api/v1/c-chart/kr-s/{context.product_code}/day:1",
                {
                    "count": context.candle_count,
                    "session": "all",
                    "investMode": "krx",
                    "useAdjustedRate": True,
                },
            ),
        ),
    ]


def _analytics_checks(context: CheckContext) -> list[EndpointCheck]:
    post_paths = [
        (
            "comprehensive financial statements",
            f"/api/v2/companies/{context.product_code}/financial-statements/comprehensive",
        ),
        (
            "financial statement records",
            f"/api/v2/companies/{context.product_code}/financial-statement-records",
        ),
        (
            "revenue estimate",
            f"/api/v2/companies/{context.product_code}/financial/estimate/revenue",
        ),
        ("EPS estimate", f"/api/v2/companies/{context.product_code}/financial/estimate/eps"),
        (
            "operating income estimate",
            f"/api/v2/companies/{context.product_code}/financial/estimate/operating-income",
        ),
        ("valuation", f"/api/v2/stock-infos/evaluation/{context.product_code}"),
        (
            "valuation comparison",
            f"/api/v2/stock-infos/evaluation-comparison/{context.product_code}",
        ),
        ("stability", f"/api/v2/stock-infos/stability/{context.product_code}"),
        (
            "revenue and net profit",
            f"/api/v2/stock-infos/revenue-and-net-profit/{context.product_code}",
        ),
        ("operating income", f"/api/v2/stock-infos/operating-income/{context.product_code}"),
    ]
    checks = [
        EndpointCheck(
            "analytics",
            "sales composition",
            "GET",
            f"/api/v1/companies/{context.company_code}/sales-compositions",
        ),
        EndpointCheck(
            "analytics", "related themes", "GET", f"/api/v2/companies/{context.company_code}/tics"
        ),
        EndpointCheck(
            "analytics",
            "stock overview",
            "GET",
            f"/api/v2/stock-infos/{context.product_code}/overview",
        ),
        EndpointCheck(
            "analytics",
            "business/holding composition",
            "GET",
            f"/api/v2/stock-infos/{context.product_code}/compositions",
        ),
        EndpointCheck(
            "analytics",
            "consensus",
            "GET",
            f"/api/v2/stock-infos/consensus/{context.product_code}",
        ),
        EndpointCheck(
            "analytics",
            "analyst opinion",
            "GET",
            f"/api/v1/stock-detail/ui/wts/{context.product_code}/analyst-opinion",
        ),
        EndpointCheck(
            "analytics",
            "analyst reports",
            "GET",
            f"/api/v1/stock-detail/ui/wts/{context.product_code}/analyst-reports",
        ),
        EndpointCheck(
            "analytics",
            "investment indicators",
            "GET",
            f"/api/v1/stock-detail/ui/wts/{context.product_code}/investment-indicators",
        ),
        EndpointCheck(
            "analytics",
            "analytics section order",
            "GET",
            f"/api/v1/stock-detail/ui/wts/{context.product_code}/section-orders",
        ),
        EndpointCheck(
            "analytics",
            "dividend summary",
            "GET",
            f"/api/v1/stock-infos/dividend/{context.product_code}/summary",
        ),
        EndpointCheck(
            "analytics",
            "dividend years",
            "GET",
            f"/api/v1/stock-infos/dividend/{context.product_code}/years",
        ),
        EndpointCheck(
            "analytics",
            "dividend yield histories",
            "GET",
            f"/api/v1/stock-infos/{context.product_code}/dividends/yield-ratio/histories",
        ),
        EndpointCheck(
            "analytics",
            "financial estimate date",
            "GET",
            f"/api/v2/companies/{context.product_code}/financial/estimate/date",
        ),
    ]
    checks.extend(
        EndpointCheck("analytics", purpose, "POST", path, {}) for purpose, path in post_paths
    )
    return checks


def _news_checks(context: CheckContext) -> list[EndpointCheck]:
    return [
        EndpointCheck(
            "news",
            "company news",
            "GET",
            api.build_path(
                f"/api/v2/news/companies/{context.company_code}", {"size": context.news_size}
            ),
        ),
        EndpointCheck(
            "news",
            "company filings",
            "GET",
            api.build_path(
                f"/api/v1/stock-detail/companies/{context.company_code}/filings",
                {"number": 1, "size": context.filing_size},
            ),
        ),
    ]


def _transaction_status_checks(context: CheckContext) -> list[EndpointCheck]:
    return [
        EndpointCheck(
            "transaction-status",
            "broker trading ranking",
            "GET",
            api.build_path("/api/v1/mds/broker/trading-ranking", {"code": context.product_code}),
        ),
        EndpointCheck(
            "transaction-status",
            "investor trading trend",
            "GET",
            api.build_path(
                "/api/v1/stock-infos/trade/trend/trading-trend",
                {"productCode": context.product_code, "size": 5},
            ),
        ),
        EndpointCheck(
            "transaction-status",
            "program trading",
            "GET",
            api.build_path(
                "/api/v1/stock-infos/trade/trend/program-trading",
                {"productCode": context.product_code, "size": 5},
            ),
        ),
        EndpointCheck(
            "transaction-status",
            "fixed-date trading trend",
            "GET",
            api.build_path(
                "/api/v1/stock-infos/trade/trend/fixed-trading-trend",
                {"productCode": context.product_code, "from": context.start, "to": context.end},
            ),
        ),
        EndpointCheck(
            "transaction-status",
            "accumulated fixed trading trend",
            "GET",
            api.build_path(
                "/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend",
                {"productCode": context.product_code, "from": context.start, "to": context.end},
            ),
        ),
        EndpointCheck(
            "transaction-status",
            "accumulated fixed trend detail",
            "GET",
            api.build_path(
                "/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail",
                {"productCode": context.product_code, "from": context.start, "to": context.end},
            ),
        ),
        EndpointCheck(
            "transaction-status",
            "credit info",
            "GET",
            api.build_path(
                "/api/v1/mds/info/credit",
                {"stockCode": context.product_code, "number": 1, "size": 5},
            ),
        ),
    ]


def summarize_result(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        summary: dict[str, Any] = {
            "type": "object",
            "keys": list(result.keys())[:MAX_SUMMARY_KEYS],
        }
        for key in ROW_KEYS:
            rows = result.get(key)
            if isinstance(rows, list) and rows and isinstance(rows[0], dict):
                summary["rowKeys"] = {key: list(rows[0].keys())[:MAX_SUMMARY_ROW_KEYS]}
                break
        return summary
    if isinstance(result, list):
        summary = {"type": "list", "len": len(result)}
        if result and isinstance(result[0], dict):
            summary["itemKeys"] = list(result[0].keys())[:MAX_SUMMARY_KEYS]
        return summary
    return {"type": type(result).__name__}


def run_checks(plan: list[EndpointCheck]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in plan:
        try:
            payload = api.request_json(item.path, method=item.method, body=item.body)
            rows.append(
                {
                    "page": item.page,
                    "purpose": item.purpose,
                    "method": item.method,
                    "path": item.path,
                    "ok": True,
                    "resultShape": summarize_result(payload.get("result")),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "page": item.page,
                    "purpose": item.purpose,
                    "method": item.method,
                    "path": item.path,
                    "ok": False,
                    "error": str(exc),
                }
            )
    return rows


def _parse_pages(value: str) -> list[str]:
    if value.strip().lower() == "all":
        return list(DEFAULT_PAGES)
    return [page.strip() for page in value.split(",") if page.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke-check read-only TossInvest stock page API endpoint groups."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--pages",
        default="all",
        help="Comma-separated pages: order,analytics,news,transaction-status; or all",
    )
    parser.add_argument("--from", dest="start", default="2026-04-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="end", default="2026-04-24", help="End date YYYY-MM-DD")
    parser.add_argument("--news-size", type=int, default=5)
    parser.add_argument("--filing-size", type=int, default=5)
    parser.add_argument("--ticks", type=int, default=5)
    parser.add_argument("--candles", type=int, default=5)
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    pages = _parse_pages(args.pages)
    plan = build_check_plan(
        args.code,
        pages,
        start=args.start,
        end=args.end,
        news_size=api.require_int_range("news-size", args.news_size, minimum=1, maximum=50),
        filing_size=api.require_int_range("filing-size", args.filing_size, minimum=1, maximum=50),
        tick_count=api.require_int_range("ticks", args.ticks, minimum=1, maximum=100),
        candle_count=api.require_int_range("candles", args.candles, minimum=1, maximum=200),
    )
    payload = {
        "code": api.normalize_product_code(args.code),
        "pages": pages,
        "checks": run_checks(plan),
    }
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
