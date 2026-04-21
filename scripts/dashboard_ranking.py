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


def build_overview_ranking_body(
    ranking_id: str,
    tag: str,
    duration: str,
    filters: list[str] | None,
) -> dict[str, Any]:
    return {
        "id": ranking_id,
        "tag": tag,
        "duration": duration,
        "filters": filters or [],
    }


def build_live_chart_body(
    live_chart: str,
    market: str,
    duration: str,
    filters: list[str] | None,
) -> dict[str, Any]:
    normalized_chart = live_chart.strip()
    normalized_market = market.strip().lower()
    if normalized_chart not in LIVE_CHART_IDS:
        raise ValueError(f"unknown live-chart id: {live_chart}")
    if normalized_market not in MARKETS:
        raise ValueError(f"unknown market: {market}")
    return build_overview_ranking_body(
        normalized_chart,
        normalized_market,
        duration,
        filters,
    )


def build_investor_rankings_path(size: int) -> str:
    return api.build_path(
        "/api/v1/dashboard/wts/overview/rankings/by-investors",
        {"size": size},
    )


def fetch_overview_ranking(
    ranking_id: str,
    tag: str,
    duration: str,
    filters: list[str] | None,
) -> dict[str, Any]:
    body = build_overview_ranking_body(ranking_id, tag, duration, filters)
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
) -> dict[str, Any]:
    body = build_live_chart_body(live_chart, market, duration, filters)
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
    return {
        "kind": "investors",
        "side": side,
        "result": api.get_result(
            build_investor_rankings_path(size),
            base_url=CERT_BASE_URL,
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest overview, live-chart, or investor rankings."
    )
    parser.add_argument(
        "--kind",
        choices=["overview", "live-chart", "investors"],
        default="overview",
    )
    parser.add_argument("--ranking-id", default="biggest_market_amount")
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
    parser.add_argument("--tag", default="all")
    parser.add_argument("--duration", default="realtime")
    parser.add_argument("--filter", dest="filters", action="append")
    parser.add_argument("--investor-size", type=int, default=100)
    parser.add_argument("--side", choices=["buy", "sell"], default="buy")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    if args.kind == "investors":
        payload = fetch_investor_rankings(args.investor_size, args.side)
    elif args.kind == "live-chart":
        payload = fetch_live_chart(
            args.live_chart or args.ranking_id,
            args.market or args.tag,
            args.duration,
            args.filters,
        )
    else:
        payload = fetch_overview_ranking(
            args.ranking_id,
            args.tag,
            args.duration,
            args.filters,
        )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
