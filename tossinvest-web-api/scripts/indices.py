#!/usr/bin/env python3
"""Fetch read-only TossInvest index and market-indicator dashboard data."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api


CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"


def normalize_index_code(code: str) -> str:
    value = code.strip()
    if "." in value:
        return value
    return value.upper()


def build_index_info_path(code: str) -> str:
    return f"/api/v2/index-infos/{normalize_index_code(code)}"


def build_index_price_path(code: str) -> str:
    return f"/api/v1/index-prices/{normalize_index_code(code)}"


def build_index_chart_path(
    code: str,
    securities_type: str,
    chart_range: str,
    step: str,
    invest_mode: str,
) -> str:
    return api.build_path(
        f"/api/v1/r-chart/{securities_type}/{normalize_index_code(code)}/{chart_range}/{step}",
        {"session": "main", "investMode": invest_mode, "last": False},
    )


def build_fx_chart_path(chart_range: str, step: str, currency: str) -> str:
    return api.build_path(
        f"/api/v1/r-chart/fx/EXCHANGE_RATE/{chart_range}/{step}",
        {
            "last": False,
            "useAdjustedRate": True,
            "currency": currency.strip().upper(),
        },
    )


def build_indicator_path(indicator_type: str, market: str | None) -> str:
    return api.build_path(
        f"/api/v1/dashboard/wts/overview/indicator/{indicator_type}",
        {"market": market},
    )


def build_exchange_rates_path() -> str:
    return "/api/v1/dashboard/wts/overview/exchange-rates"


def fetch_index_payload(
    *,
    code: str,
    securities_type: str,
    chart_range: str,
    step: str,
    invest_mode: str,
    include_chart: bool,
    include_fx_chart: bool,
    include_indicators: bool,
    include_exchange_rates: bool,
    fx_chart_range: str,
    fx_step: str,
    fx_currency: str,
    indicator_type: str,
    market: str | None,
) -> dict[str, Any]:
    normalized_code = normalize_index_code(code)
    payload: dict[str, Any] = {
        "code": normalized_code,
        "info": api.get_result(build_index_info_path(code)),
        "price": api.get_result(build_index_price_path(code)),
    }
    if include_chart:
        payload["chart"] = api.get_result(
            build_index_chart_path(code, securities_type, chart_range, step, invest_mode)
        )
    if include_fx_chart:
        payload["fxChart"] = api.get_result(
            build_fx_chart_path(fx_chart_range, fx_step, fx_currency)
        )
    if include_indicators:
        payload["indicators"] = api.get_result(
            build_indicator_path(indicator_type, market),
            base_url=CERT_BASE_URL,
        )
    if include_exchange_rates:
        payload["exchangeRates"] = api.get_result(build_exchange_rates_path())
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch TossInvest index details, price, optional index/FX charts, "
            "exchange-rate widgets, and indicator lists."
        )
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
    parser.add_argument(
        "--include-fx-chart",
        action="store_true",
        help="Also fetch the FX exchange-rate r-chart",
    )
    parser.add_argument("--fx-range", default="1d", help="FX r-chart range")
    parser.add_argument("--fx-step", default="min:5", help="FX r-chart step")
    parser.add_argument("--fx-currency", default="USD", help="FX r-chart currency")
    parser.add_argument("--include-indicators", action="store_true")
    parser.add_argument(
        "--include-exchange-rates",
        action="store_true",
        help="Also fetch the public-looking dashboard exchange-rates widget",
    )
    parser.add_argument(
        "--indicator-type",
        default="index",
        help="Observed dashboard indicator type, e.g. index, bond, or commodity",
    )
    parser.add_argument("--market", default="kr", help="Indicator market query value")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_index_payload(
        code=args.code,
        securities_type=args.securities_type,
        chart_range=args.chart_range,
        step=args.step,
        invest_mode=args.invest_mode,
        include_chart=args.include_chart,
        include_fx_chart=args.include_fx_chart,
        include_indicators=args.include_indicators,
        include_exchange_rates=args.include_exchange_rates,
        fx_chart_range=args.fx_range,
        fx_step=args.fx_step,
        fx_currency=args.fx_currency,
        indicator_type=args.indicator_type,
        market=args.market,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
