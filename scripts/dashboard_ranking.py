#!/usr/bin/env python3
"""Fetch read-only TossInvest dashboard ranking widgets."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"
LIVE_CHART_IDS = {
    "biggest_total_amount",
    "biggest_total_volume",
    "biggest_market_amount",
    "biggest_market_volume",
    "heavy_soar",
    "heavy_descent",
    "realtime_stock",
}
MARKETS = {"all", "kr", "us"}
DURATIONS = {"1d", "5d", "20d", "60d", "120d", "240d", "realtime"}
HIDE_INVESTMENT_RISK_FILTERS = (
    "KRX_MANAGEMENT_STOCK",
    "MARKET_CAP_GREATER_THAN_50M",
    "STOCKS_PRICE_GREATER_THAN_ONE_DOLLAR",
)
RANKING_FILTER_IDS = set(HIDE_INVESTMENT_RISK_FILTERS)


def normalize_ranking_filters(
    filters: list[str] | None,
    hide_investment_risk: bool = False,
) -> list[str]:
    normalized: list[str] = []
    for filter_id in filters or []:
        candidate = filter_id.strip().upper()
        if candidate not in RANKING_FILTER_IDS:
            expected = ", ".join(sorted(RANKING_FILTER_IDS))
            raise ValueError(f"filter must be one of: {expected}")
        if candidate not in normalized:
            normalized.append(candidate)
    if hide_investment_risk:
        for filter_id in HIDE_INVESTMENT_RISK_FILTERS:
            if filter_id not in normalized:
                normalized.append(filter_id)
    return normalized


def build_overview_ranking_body(
    ranking_id: str,
    tag: str,
    duration: str,
    filters: list[str] | None,
    hide_investment_risk: bool = False,
) -> dict[str, Any]:
    ranking_id = _require_choice("ranking_id", ranking_id, LIVE_CHART_IDS)
    tag = _require_choice("tag", tag, MARKETS)
    duration = _require_choice("duration", duration, DURATIONS)
    return {
        "id": ranking_id,
        "tag": tag,
        "duration": duration,
        "filters": normalize_ranking_filters(filters, hide_investment_risk),
    }


def build_live_chart_body(
    live_chart: str,
    market: str,
    duration: str,
    filters: list[str] | None,
    hide_investment_risk: bool = False,
) -> dict[str, Any]:
    return build_overview_ranking_body(
        live_chart,
        market,
        duration,
        filters,
        hide_investment_risk,
    )


def _require_choice(name: str, value: str, choices: set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in choices:
        expected = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {expected}")
    return normalized


def build_investor_rankings_path(size: int) -> str:
    return api.build_path(
        "/api/v1/dashboard/wts/overview/rankings/by-investors",
        {"size": size},
    )


def build_overview_signals_path(product_codes: list[str]) -> str:
    if not product_codes:
        raise ValueError("signal codes must contain at least one code")
    normalized_codes = ",".join(api.normalize_product_code(code) for code in product_codes)
    return api.build_path(
        "/api/v1/dashboard/wts/overview/signals",
        {"codes": normalized_codes},
    )


def fetch_overview_ranking(
    ranking_id: str,
    tag: str,
    duration: str,
    filters: list[str] | None,
    hide_investment_risk: bool = False,
) -> dict[str, Any]:
    body = build_overview_ranking_body(
        ranking_id,
        tag,
        duration,
        filters,
        hide_investment_risk,
    )
    return {
        "kind": "overview",
        "body": body,
        "result": api.get_result(
            "/api/v2/dashboard/wts/overview/ranking",
            method="POST",
            body=body,
            base_url=CERT_BASE_URL,
        ),
    }


def fetch_live_chart(
    live_chart: str,
    market: str,
    duration: str,
    filters: list[str] | None,
    hide_investment_risk: bool = False,
) -> dict[str, Any]:
    body = build_live_chart_body(
        live_chart,
        market,
        duration,
        filters,
        hide_investment_risk,
    )
    return {
        "kind": "live-chart",
        "body": body,
        "result": api.get_result(
            "/api/v2/dashboard/wts/overview/ranking",
            method="POST",
            body=body,
            base_url=CERT_BASE_URL,
        ),
    }


def fetch_investor_rankings(size: int, side: str) -> dict[str, Any]:
    size = api.require_int_range("investor-size", size, minimum=1, maximum=100)
    side = _require_choice("side", side, {"buy", "sell"})
    result = api.get_result(
        build_investor_rankings_path(size),
        base_url=CERT_BASE_URL,
    )
    return {
        "kind": "investors",
        "side": side,
        "result": result,
        "selectedRankings": select_investor_rankings(result, side),
    }


def select_investor_rankings(result: Any, side: str) -> dict[str, Any]:
    side = _require_choice("side", side, {"buy", "sell"})
    if not isinstance(result, dict) or not isinstance(result.get("rankings"), dict):
        raise RuntimeError("Unexpected TossInvest response: investor rankings are missing")
    stock_key = "buyStocks" if side == "buy" else "sellStocks"
    selected: dict[str, Any] = {}
    for investor_type, ranking in result["rankings"].items():
        if not isinstance(ranking, dict) or not isinstance(ranking.get(stock_key), list):
            continue
        selected[investor_type] = {
            "basedAt": ranking.get("basedAt"),
            "type": ranking.get("type"),
            "stocks": ranking[stock_key],
        }
    return selected


def fetch_overview_signals(product_codes: list[str]) -> dict[str, Any]:
    return {
        "kind": "signals",
        "codes": [api.normalize_product_code(code) for code in product_codes],
        "result": api.get_result(build_overview_signals_path(product_codes)),
    }


def fetch_overview_indicator() -> dict[str, Any]:
    return {
        "kind": "indicator",
        "result": api.get_result(
            "/api/v4/dashboard/wts/overview/indicator",
            base_url=CERT_BASE_URL,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest overview, live-chart, investor rankings, or stock signals."
    )
    parser.add_argument(
        "--kind",
        choices=["indicator", "overview", "live-chart", "investors", "signals"],
        default="overview",
    )
    parser.add_argument(
        "--ranking-id", default="biggest_market_amount", choices=sorted(LIVE_CHART_IDS)
    )
    parser.add_argument(
        "--live-chart",
        choices=sorted(LIVE_CHART_IDS),
        help="Home live-chart id, e.g. biggest_total_amount or heavy_soar",
    )
    parser.add_argument(
        "--market",
        choices=sorted(MARKETS),
        help="Home live-chart market parameter; alias for --tag",
    )
    parser.add_argument("--tag", default="all", choices=sorted(MARKETS))
    parser.add_argument("--duration", default="realtime", choices=sorted(DURATIONS))
    parser.add_argument(
        "--filter",
        dest="filters",
        action="append",
        choices=sorted(RANKING_FILTER_IDS),
        help="Observed home ranking filter id; repeat to combine filters",
    )
    parser.add_argument(
        "--hide-investment-risk",
        action="store_true",
        help="Mirror the home '투자위험 주식 숨기기' composite filter",
    )
    parser.add_argument("--investor-size", type=int, default=100)
    parser.add_argument("--side", choices=["buy", "sell"], default="buy")
    parser.add_argument(
        "--signal-code",
        action="append",
        help="Product code for --kind signals; can be repeated",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    if args.kind == "indicator":
        payload = fetch_overview_indicator()
    elif args.kind == "investors":
        payload = fetch_investor_rankings(args.investor_size, args.side)
    elif args.kind == "signals":
        if not args.signal_code:
            raise ValueError("--kind signals requires at least one --signal-code")
        payload = fetch_overview_signals(args.signal_code)
    elif args.kind == "live-chart":
        payload = fetch_live_chart(
            args.live_chart or args.ranking_id,
            args.market or args.tag,
            args.duration,
            args.filters,
            args.hide_investment_risk,
        )
    else:
        payload = fetch_overview_ranking(
            args.ranking_id,
            args.tag,
            args.duration,
            args.filters,
            args.hide_investment_risk,
        )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
