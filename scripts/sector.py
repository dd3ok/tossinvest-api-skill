#!/usr/bin/env python3
"""Fetch the current public TossInvest industry ranking and sector-page data."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from typing import Any

import tossinvest_api as api

RANKING_SORTS = {
    "fluctuation-rate": "FLUCTUATION_RATE",
    "trading-amount": "TRADING_AMOUNT",
}
STOCK_SORTS = {
    "market-cap": "MARKET_CAP",
    "trading-value": "TRADING_VALUE",
    "volume": "VOLUME",
    "analyst": "ANALYST",
}
ETF_SORTS = {
    "trading-value": "TRADING_VALUE",
    "expense-ratio": "EXPENSE_RATIO",
}
COMPARISON_INDICES = {
    "SPX.CBI",
    "COMP.NAI",
    "KGG01P",
    "QGG01P",
}
MARKET_NATIONS = {"kr", "us"}
FILTER_NATIONS = {"all", *MARKET_NATIONS}
DURATIONS = {"1d", "1w", "1m", "3m", "1y"}
SORT_ORDERS = {"asc", "desc"}
CATALOG_CHECKED_AT = "2026-09-07"
CLIENT_MAX_PAGE = 100
STOCK_PAGE_SIZE = 10
ETF_PAGE_SIZE = 10
NEWS_PAGE_SIZE = 5
_TICS_ID = re.compile(r"^\d{1,30}$")


def normalize_tics_id(tics_id: str) -> str:
    value = tics_id.strip()
    if not _TICS_ID.fullmatch(value):
        raise ValueError("tics-id must contain 1 to 30 digits")
    return value


def normalize_choice(name: str, value: str, allowed: set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {choices}")
    return normalized


def map_choice(name: str, value: str, mapping: dict[str, str]) -> str:
    normalized = normalize_choice(name, value, set(mapping))
    return mapping[normalized]


def build_observation_meta(source_page: str) -> dict[str, Any]:
    return {
        "catalogCheckedAt": CATALOG_CHECKED_AT,
        "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sourcePage": source_page,
        "transport": "rest_snapshot",
        "livePriceOverlay": "generic_stock_trade_ws_not_included",
    }


def build_sector_ranking_body(nation: str, duration: str, sort_by: str) -> dict[str, Any]:
    nation = normalize_choice("nation", nation, MARKET_NATIONS)
    duration = normalize_choice("duration", duration, DURATIONS)
    return {
        "nation": nation.upper(),
        "duration": duration,
        "sortBy": map_choice("ranking-sort", sort_by, RANKING_SORTS),
    }


def build_sector_overview_path(tics_id: str) -> str:
    return f"/api/v2/dashboard/wts/overview/tics/{normalize_tics_id(tics_id)}/overview"


def build_sector_simple_path(tics_id: str, nation: str, duration: str) -> str:
    nation = normalize_choice("nation", nation, MARKET_NATIONS)
    duration = normalize_choice("duration", duration, DURATIONS)
    return api.build_path(
        f"/api/v2/dashboard/wts/overview/tics/{normalize_tics_id(tics_id)}/simple",
        {"nation": nation.upper(), "duration": duration},
    )


def build_sector_comparison_path(tics_id: str, nation: str, indicator_code: str) -> str:
    nation = normalize_choice("nation", nation, MARKET_NATIONS)
    if indicator_code not in COMPARISON_INDICES:
        allowed = ", ".join(sorted(COMPARISON_INDICES))
        raise ValueError(f"indicator-code must be one of: {allowed}")
    return api.build_path(
        f"/api/v1/dashboard/wts/overview/tics/{normalize_tics_id(tics_id)}/comparison-chart",
        {
            "nation": nation.upper(),
            "securitiesType": "STOCK",
            "indicatorCode": indicator_code,
        },
    )


def build_sector_news_path(tics_id: str, page: int) -> str:
    page = api.require_int_range("news-page", page, minimum=1, maximum=CLIENT_MAX_PAGE)
    return api.build_path(
        f"/api/v2/dashboard/wts/overview/tics/{normalize_tics_id(tics_id)}/news",
        {"number": page},
    )


def build_sector_stocks_body(
    nation: str,
    sort_by: str,
    sort_order: str,
    page: int,
) -> dict[str, Any]:
    page = api.require_int_range("stock-page", page, minimum=1, maximum=CLIENT_MAX_PAGE)
    nation = normalize_choice("stock-nation", nation, FILTER_NATIONS)
    sort_order = normalize_choice("stock-order", sort_order, SORT_ORDERS)
    return {
        "nation": nation.upper(),
        "sortBy": map_choice("stock-sort", sort_by, STOCK_SORTS),
        "sortOrder": sort_order.upper(),
        "page": page,
    }


def build_sector_etfs_body(
    nation: str,
    sort_by: str,
    sort_order: str,
    include_leverage_inverse: bool,
    page: int,
) -> dict[str, Any]:
    page = api.require_int_range("etf-page", page, minimum=1, maximum=CLIENT_MAX_PAGE)
    nation = normalize_choice("etf-nation", nation, FILTER_NATIONS)
    sort_order = normalize_choice("etf-order", sort_order, SORT_ORDERS)
    return {
        "nation": nation.upper(),
        "sortBy": map_choice("etf-sort", sort_by, ETF_SORTS),
        "sortOrder": sort_order.upper(),
        "includeLeverageInverse": include_leverage_inverse,
        "page": page,
    }


def fetch_sector_ranking(nation: str, duration: str, sort_by: str) -> dict[str, Any]:
    body = build_sector_ranking_body(nation, duration, sort_by)
    return {
        "_meta": build_observation_meta("/?ranking-type=trending_category"),
        "request": {"ranking": body},
        "filters": body,
        "ranking": api.get_result(
            "/api/v2/dashboard/wts/overview/tics/ranking",
            method="POST",
            body=body,
        ),
    }


def fetch_sector_detail(
    *,
    tics_id: str,
    nation: str,
    duration: str,
    stock_nation: str,
    stock_sort: str,
    stock_order: str,
    stock_page: int,
    etf_nation: str,
    etf_sort: str,
    etf_order: str,
    etf_page: int,
    include_leverage_inverse: bool,
    news_page: int,
    include_comparison: bool,
    indicator_code: str,
) -> dict[str, Any]:
    normalized_id = normalize_tics_id(tics_id)
    nation = normalize_choice("nation", nation, MARKET_NATIONS)
    duration = normalize_choice("duration", duration, DURATIONS)
    overview_path = build_sector_overview_path(normalized_id)
    simple_path = build_sector_simple_path(normalized_id, nation, duration)
    news_path = build_sector_news_path(normalized_id, news_page)
    stock_body = build_sector_stocks_body(
        stock_nation,
        stock_sort,
        stock_order,
        stock_page,
    )
    etf_body = build_sector_etfs_body(
        etf_nation,
        etf_sort,
        etf_order,
        include_leverage_inverse,
        etf_page,
    )
    comparison_path = (
        build_sector_comparison_path(normalized_id, nation, indicator_code)
        if include_comparison
        else None
    )
    payload: dict[str, Any] = {
        "_meta": {
            **build_observation_meta(f"/sector/{normalized_id}?nation={nation.upper()}"),
            "pagination": {
                "stocks": {
                    "page": stock_page,
                    "pageSize": STOCK_PAGE_SIZE,
                    "base": 1,
                    "clientMaxPage": CLIENT_MAX_PAGE,
                },
                "etfs": {
                    "page": etf_page,
                    "pageSize": ETF_PAGE_SIZE,
                    "base": 1,
                    "clientMaxPage": CLIENT_MAX_PAGE,
                },
                "news": {
                    "page": news_page,
                    "pageSize": NEWS_PAGE_SIZE,
                    "base": 1,
                    "clientMaxPage": CLIENT_MAX_PAGE,
                },
            },
        },
        "request": {
            "simple": {"nation": nation.upper(), "duration": duration},
            "stocks": stock_body,
            "etfs": etf_body,
            "news": {"number": news_page},
            "comparison": (
                {
                    "nation": nation.upper(),
                    "securitiesType": "STOCK",
                    "indicatorCode": indicator_code,
                }
                if include_comparison
                else None
            ),
        },
        "ticsId": normalized_id,
        "nation": nation.upper(),
        "duration": duration,
        "overview": api.get_result(overview_path),
        "simple": api.get_result(simple_path),
        "stocks": api.get_result(
            f"/api/v2/dashboard/wts/overview/tics/{normalized_id}/stocks",
            method="POST",
            body=stock_body,
        ),
        "etfs": api.get_result(
            f"/api/v2/dashboard/wts/overview/tics/{normalized_id}/etfs",
            method="POST",
            body=etf_body,
        ),
        "news": api.get_result(news_path),
    }
    if comparison_path is not None:
        payload["comparisonChart"] = api.get_result(comparison_path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch current TossInvest industry ranking or sector-page data."
    )
    parser.add_argument(
        "--kind",
        choices=["ranking", "detail"],
        default="detail",
        help="Fetch the home industry ranking or a sector detail composite",
    )
    parser.add_argument("--tics-id", help="Numeric TICS id; required for --kind detail")
    parser.add_argument("--nation", choices=sorted(MARKET_NATIONS), default="kr")
    parser.add_argument("--duration", choices=sorted(DURATIONS), default="1d")
    parser.add_argument(
        "--ranking-sort",
        choices=sorted(RANKING_SORTS),
        default="fluctuation-rate",
    )
    parser.add_argument("--stock-nation", choices=sorted(FILTER_NATIONS))
    parser.add_argument(
        "--stock-sort",
        choices=sorted(STOCK_SORTS),
        default="market-cap",
    )
    parser.add_argument("--stock-order", choices=sorted(SORT_ORDERS), default="desc")
    parser.add_argument("--stock-page", type=int, default=1)
    parser.add_argument("--etf-nation", choices=sorted(FILTER_NATIONS), default="all")
    parser.add_argument(
        "--etf-sort",
        choices=sorted(ETF_SORTS),
        default="trading-value",
    )
    parser.add_argument("--etf-order", choices=sorted(SORT_ORDERS), default="desc")
    parser.add_argument("--etf-page", type=int, default=1)
    parser.add_argument(
        "--exclude-leverage-inverse",
        action="store_true",
        help="Set includeLeverageInverse=false for the related ETF request",
    )
    parser.add_argument("--news-page", type=int, default=1)
    parser.add_argument("--include-comparison", action="store_true")
    parser.add_argument(
        "--indicator-code",
        choices=sorted(COMPARISON_INDICES),
        help="Comparison index; defaults to KOSPI for KR and S&P 500 for US",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    if args.kind == "ranking":
        payload = fetch_sector_ranking(args.nation, args.duration, args.ranking_sort)
    else:
        if args.tics_id is None:
            parser.error("--tics-id is required for --kind detail")
        indicator_code = args.indicator_code or ("KGG01P" if args.nation == "kr" else "SPX.CBI")
        payload = fetch_sector_detail(
            tics_id=args.tics_id,
            nation=args.nation,
            duration=args.duration,
            stock_nation=args.stock_nation or args.nation,
            stock_sort=args.stock_sort,
            stock_order=args.stock_order,
            stock_page=args.stock_page,
            etf_nation=args.etf_nation,
            etf_sort=args.etf_sort,
            etf_order=args.etf_order,
            etf_page=args.etf_page,
            include_leverage_inverse=not args.exclude_leverage_inverse,
            news_page=args.news_page,
            include_comparison=args.include_comparison,
            indicator_code=indicator_code,
        )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
