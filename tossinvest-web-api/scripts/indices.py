#!/usr/bin/env python3
"""Fetch read-only TossInvest index, bond, commodity, and FX dashboard data."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api


CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"


def build_index_info_path(code: str) -> str:
    return f"/api/v2/index-infos/{code.strip().upper()}"


def build_index_price_path(code: str) -> str:
    return f"/api/v1/index-prices/{code.strip().upper()}"


def build_index_chart_path(
    code: str,
    securities_type: str,
    chart_range: str,
    step: str,
    invest_mode: str,
) -> str:
    return api.build_path(
        f"/api/v1/r-chart/{securities_type}/{code.strip().upper()}/{chart_range}/{step}",
        {"session": "main", "investMode": invest_mode, "last": False},
    )


def build_indicator_path(indicator_type: str, market: str | None) -> str:
    return api.build_path(
        f"/api/v1/dashboard/wts/overview/indicator/{indicator_type}",
        {"market": market},
    )


def fetch_index_payload(
    *,
    code: str,
    securities_type: str,
    chart_range: str,
    step: str,
    invest_mode: str,
    include_chart: bool,
    include_indicators: bool,
    indicator_type: str,
    market: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code.strip().upper(),
        "info": api.get_result(build_index_info_path(code)),
        "price": api.get_result(build_index_price_path(code)),
    }
    if include_chart:
        payload["chart"] = api.get_result(
            build_index_chart_path(code, securities_type, chart_range, step, invest_mode)
        )
    if include_indicators:
        payload["indicators"] = api.get_result(
            build_indicator_path(indicator_type, market),
            base_url=CERT_BASE_URL,
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest index details, price, optional chart, and indicator lists."
    )
    parser.add_argument("--code", default="KGG01P", help="TossInvest index code")
    parser.add_argument(
        "--securities-type",
        default="kr-s",
        help="Observed r-chart securitiesType, e.g. kr-s or us-s",
    )
    parser.add_argument("--range", dest="chart_range", default="1d")
    parser.add_argument("--step", default="min:5")
    parser.add_argument("--invest-mode", default="krx")
    parser.add_argument("--include-chart", action="store_true")
    parser.add_argument("--include-indicators", action="store_true")
    parser.add_argument("--indicator-type", default="index")
    parser.add_argument("--market", default="kr")
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_index_payload(
        code=args.code,
        securities_type=args.securities_type,
        chart_range=args.chart_range,
        step=args.step,
        invest_mode=args.invest_mode,
        include_chart=args.include_chart,
        include_indicators=args.include_indicators,
        indicator_type=args.indicator_type,
        market=args.market,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
