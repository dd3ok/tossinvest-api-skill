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
DURATIONS = {"1d", "realtime"}


def build_overview_ranking_body(
    ranking_id: str,
    tag: str,
    duration: str,
    filters: list[str] | None,
) -> dict[str, Any]:
    ranking_id = _require_choice("ranking_id", ranking_id, LIVE_CHART_IDS)
    tag = _require_choice("tag", tag, MARKETS)
    duration = _require_choice("duration", duration, DURATIONS)
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
    return build_overview_ranking_body(
        live_chart,
        market,
        duration,
        filters,
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
    size = api.require_int_range("investor-size", size, minimum=1, maximum=100)
    return {
        "kind": "investors",
        "side": side,
        "result": api.get_result(
            build_investor_rankings_path(size),
            base_url=CERT_BASE_URL,
        ),
    }


def fetch_overview_signals(product_codes: list[str]) -> dict[str, Any]:
    return {
        "kind": "signals",
        "codes": [api.normalize_product_code(code) for code in product_codes],
        "result": api.get_result(build_overview_signals_path(product_codes)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest overview, live-chart, investor rankings, or stock signals."
    )
    parser.add_argument(
        "--kind",
        choices=["overview", "live-chart", "investors", "signals"],
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
    parser.add_argument("--filter", dest="filters", action="append")
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

    if args.kind == "investors":
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
    raise SystemExit(api.run_cli(main))
