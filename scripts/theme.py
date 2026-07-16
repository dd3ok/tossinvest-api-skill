#!/usr/bin/env python3
"""Fetch read-only TossInvest theme/TICS discovery data."""

from __future__ import annotations

import argparse
import re
from typing import Any

import tossinvest_api as api

COMPANY_RANKINGS = {
    "marketcap": 1,
    "revenue": 3,
    "operating-margin": 4,
}
# The current public TICS-ranking endpoint rejects the longer home-ranking
# durations. Keep this narrower than dashboard_ranking.py's product durations.
DASHBOARD_DURATIONS = {"1d"}
DASHBOARD_NATIONS = {"kr": "KR", "us": "US"}
SECTOR_NATIONS = {"all": "ALL", "kr": "KR", "us": "US"}
SECTOR_STOCK_SORTS = {
    "analyst": "ANALYST",
    "market-cap": "MARKET_CAP",
    "trading-value": "TRADING_VALUE",
    "volume": "VOLUME",
}
SECTOR_ETF_SORTS = {
    "expense-ratio": "EXPENSE_RATIO",
    "trading-value": "TRADING_VALUE",
}
SORT_ORDERS = {"asc": "ASC", "desc": "DESC"}
_TICS_ID_RE = re.compile(r"^\d{1,12}$")


def build_theme_ranking_path(tag: str) -> str:
    return f"/api/v1/rankings/contents/tics_margin_depth1/tags/{tag.strip().lower()}"


def build_theme_details_path(tics_id: str) -> str:
    return f"/api/v1/tics/{validate_tics_id(tics_id)}/details"


def build_theme_news_path(tics_id: str, size: int) -> str:
    return api.build_path(f"/api/v2/news/tics/{validate_tics_id(tics_id)}", {"size": size})


def build_theme_company_ranking_path(tics_id: str, ranking: str) -> str:
    if ranking not in COMPANY_RANKINGS:
        raise ValueError(f"unknown company ranking: {ranking}")
    return api.build_path(
        "/api/v1/companies/tics/rankings",
        {"ticsId": validate_tics_id(tics_id), "ticsRanking": COMPANY_RANKINGS[ranking]},
    )


def build_related_path(tics_id: str) -> str:
    return f"/api/v1/tics/{validate_tics_id(tics_id)}/related"


def build_fluctuations_path(tics_id: str) -> str:
    return f"/api/v2/tics/{validate_tics_id(tics_id)}/fluctuations"


def build_dashboard_theme_ranking_body(nation: str, duration: str) -> dict[str, Any]:
    return {
        "nation": _require_choice("nation", nation, DASHBOARD_NATIONS),
        "duration": _require_choice("duration", duration, DASHBOARD_DURATIONS),
    }


def build_sector_stocks_path(tics_id: str) -> str:
    return f"/api/v2/dashboard/wts/overview/tics/{validate_tics_id(tics_id)}/stocks"


def build_sector_etfs_path(tics_id: str) -> str:
    return f"/api/v2/dashboard/wts/overview/tics/{validate_tics_id(tics_id)}/etfs"


def validate_tics_id(tics_id: str) -> str:
    value = str(tics_id).strip()
    if not _TICS_ID_RE.fullmatch(value):
        raise ValueError("tics id must contain 1-12 digits")
    return value


def build_sector_stocks_body(
    nation: str,
    sort_by: str,
    sort_order: str,
    page: int,
) -> dict[str, Any]:
    return {
        "nation": _require_choice("nation", nation, SECTOR_NATIONS),
        "sortBy": _require_choice("stock sort", sort_by, SECTOR_STOCK_SORTS),
        "sortOrder": _require_choice("sort order", sort_order, SORT_ORDERS),
        "page": api.require_int_range("sector-page", page, minimum=1, maximum=1000),
    }


def build_sector_etfs_body(
    nation: str,
    sort_by: str,
    sort_order: str,
    include_leverage_inverse: bool,
    page: int,
) -> dict[str, Any]:
    return {
        "nation": _require_choice("nation", nation, SECTOR_NATIONS),
        "sortBy": _require_choice("ETF sort", sort_by, SECTOR_ETF_SORTS),
        "sortOrder": _require_choice("sort order", sort_order, SORT_ORDERS),
        "includeLeverageInverse": bool(include_leverage_inverse),
        "page": api.require_int_range("sector-page", page, minimum=1, maximum=1000),
    }


def _require_choice(name: str, value: str, choices: dict[str, str] | set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in choices:
        raise ValueError(f"{name} must be one of: {', '.join(sorted(choices))}")
    if isinstance(choices, dict):
        return choices[normalized]
    return normalized


def fetch_theme_payload(
    *,
    tag: str,
    tics_id: str | None,
    news_size: int,
    include_all: bool,
    include_details: bool,
    company_rankings: list[str],
    include_dashboard_ranking: bool = False,
    dashboard_duration: str = "1d",
    include_sector_stocks: bool = False,
    include_sector_etfs: bool = False,
    sector_nation: str = "all",
    sector_stock_sort: str = "market-cap",
    sector_etf_sort: str = "trading-value",
    sector_sort_order: str = "desc",
    sector_page: int = 1,
    include_leverage_inverse: bool = False,
) -> dict[str, Any]:
    news_size = api.require_int_range("news-size", news_size, minimum=1, maximum=50)
    if tics_id is None and (include_sector_stocks or include_sector_etfs):
        raise ValueError("sector stock/ETF requests require --tics-id")
    payload: dict[str, Any] = {
        "tag": tag.strip().lower(),
        "ranking": api.get_result(build_theme_ranking_path(tag)),
    }
    if include_dashboard_ranking:
        dashboard_body = build_dashboard_theme_ranking_body(tag, dashboard_duration)
        payload["dashboardRanking"] = api.get_result(
            "/api/v2/dashboard/wts/overview/tics/ranking",
            method="POST",
            body=dashboard_body,
        )
    if include_all:
        payload["allThemes"] = api.get_result("/api/v1/tics/all")
    if tics_id is not None:
        payload["ticsId"] = validate_tics_id(tics_id)
        if include_details:
            payload["details"] = api.get_result(build_theme_details_path(tics_id))
        payload["related"] = api.get_result(build_related_path(tics_id))
        payload["news"] = api.get_result(build_theme_news_path(tics_id, news_size))
        payload["fluctuations"] = api.get_result(build_fluctuations_path(tics_id))
        if company_rankings:
            payload["companyRankings"] = {
                ranking: api.get_result(build_theme_company_ranking_path(tics_id, ranking))
                for ranking in company_rankings
            }
        if include_sector_stocks:
            stock_body = build_sector_stocks_body(
                sector_nation,
                sector_stock_sort,
                sector_sort_order,
                sector_page,
            )
            payload["sectorStocks"] = api.get_result(
                build_sector_stocks_path(tics_id),
                method="POST",
                body=stock_body,
            )
        if include_sector_etfs:
            etf_body = build_sector_etfs_body(
                sector_nation,
                sector_etf_sort,
                sector_sort_order,
                include_leverage_inverse,
                sector_page,
            )
            payload["sectorEtfs"] = api.get_result(
                build_sector_etfs_path(tics_id),
                method="POST",
                body=etf_body,
            )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest theme/TICS rankings and optional theme details."
    )
    parser.add_argument(
        "--tag",
        default="kr",
        help="Theme ranking tag observed in TossInvest, commonly kr or us",
    )
    parser.add_argument("--tics-id", help="Also fetch details for this TICS id")
    parser.add_argument(
        "--news-size",
        type=int,
        default=5,
        help="Number of theme news items to request when --tics-id is set",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Also fetch /api/v1/tics/all",
    )
    parser.add_argument(
        "--include-details",
        action="store_true",
        help="Also fetch /api/v1/tics/{id}/details when --tics-id is set",
    )
    parser.add_argument(
        "--company-ranking",
        action="append",
        choices=sorted(COMPANY_RANKINGS),
        default=[],
        help="Also fetch a TICS company ranking; repeat for multiple rankings",
    )
    parser.add_argument(
        "--include-dashboard-ranking",
        action="store_true",
        help="Also fetch the current home trending-industry ranking",
    )
    parser.add_argument(
        "--dashboard-duration",
        choices=sorted(DASHBOARD_DURATIONS),
        default="1d",
    )
    parser.add_argument("--include-sector-stocks", action="store_true")
    parser.add_argument("--include-sector-etfs", action="store_true")
    parser.add_argument("--sector-nation", choices=sorted(SECTOR_NATIONS), default="all")
    parser.add_argument(
        "--sector-stock-sort", choices=sorted(SECTOR_STOCK_SORTS), default="market-cap"
    )
    parser.add_argument(
        "--sector-etf-sort", choices=sorted(SECTOR_ETF_SORTS), default="trading-value"
    )
    parser.add_argument("--sector-sort-order", choices=sorted(SORT_ORDERS), default="desc")
    parser.add_argument("--sector-page", type=int, default=1)
    parser.add_argument(
        "--include-leverage-inverse",
        action="store_true",
        help="Include leveraged and inverse ETFs in the sector ETF table",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_theme_payload(
        tag=args.tag,
        tics_id=args.tics_id,
        news_size=args.news_size,
        include_all=args.include_all,
        include_details=args.include_details,
        company_rankings=args.company_ranking,
        include_dashboard_ranking=args.include_dashboard_ranking,
        dashboard_duration=args.dashboard_duration,
        include_sector_stocks=args.include_sector_stocks,
        include_sector_etfs=args.include_sector_etfs,
        sector_nation=args.sector_nation,
        sector_stock_sort=args.sector_stock_sort,
        sector_etf_sort=args.sector_etf_sort,
        sector_sort_order=args.sector_sort_order,
        sector_page=args.sector_page,
        include_leverage_inverse=args.include_leverage_inverse,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
