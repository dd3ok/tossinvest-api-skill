#!/usr/bin/env python3
"""Fetch read-only TossInvest index and market-indicator dashboard data."""

from __future__ import annotations

import argparse
from datetime import date
from typing import Any

import tossinvest_api as api


CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"
CHART_PRESETS = {
    "intraday": ("1d", "min:5"),
    "quarter": ("3m", "day:1"),
    "daily": ("1y", "day:1"),
}


def normalize_index_code(code: str) -> str:
    value = code.strip()
    if "." in value:
        return value
    return value.upper()


def infer_securities_type(code: str, securities_type: str) -> str:
    normalized = securities_type.strip().lower()
    if normalized != "auto":
        return normalized
    if "." in normalize_index_code(code):
        return "us-s"
    return "kr-s"


def resolve_chart_window(
    chart_preset: str | None,
    chart_range: str | None,
    step: str | None,
) -> tuple[str, str]:
    preset = chart_preset or "intraday"
    if preset not in CHART_PRESETS:
        choices = ", ".join(sorted(CHART_PRESETS))
        raise ValueError(f"chart preset must be one of: {choices}")
    preset_range, preset_step = CHART_PRESETS[preset]
    return chart_range or preset_range, step or preset_step


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
    resolved_securities_type = infer_securities_type(code, securities_type)
    return api.build_path(
        (
            f"/api/v1/r-chart/{resolved_securities_type}/"
            f"{normalize_index_code(code)}/{chart_range}/{step}"
        ),
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


def build_mini_chart_path() -> str:
    return "/api/v3/dashboard/wts/overview/indicator/mini-chart"


def build_related_etfs_path(code: str) -> str:
    return f"/api/v3/dashboard/wts/overview/indicator/{normalize_index_code(code)}/related-etfs"


def build_net_buying_range_path(
    code: str,
    net_range: str,
    from_date: str,
    count: int,
) -> str:
    return api.build_path(
        "/api/v1/stock-infos/index/net-buying/range",
        {
            "code": normalize_index_code(code),
            "range": net_range,
            "from": from_date,
            "count": count,
        },
    )


def build_net_buying_daily_path(code: str, from_date: str, count: int) -> str:
    return api.build_path(
        "/api/v1/stock-infos/index/net-buying/daily",
        {"code": normalize_index_code(code), "count": count, "from": from_date},
    )


def build_exchange_rates_path() -> str:
    return "/api/v1/dashboard/wts/overview/exchange-rates"


def fetch_index_payload(
    *,
    code: str,
    securities_type: str,
    chart_preset: str | None,
    chart_range: str | None,
    step: str | None,
    invest_mode: str,
    include_chart: bool,
    include_fx_chart: bool,
    include_indicators: bool,
    include_exchange_rates: bool,
    include_mini_chart: bool,
    include_related_etfs: bool,
    include_net_buying: bool,
    fx_chart_range: str,
    fx_step: str,
    fx_currency: str,
    indicator_type: str,
    market: str | None,
    net_buying_from: str,
    net_buying_range: str,
    net_buying_count: int,
) -> dict[str, Any]:
    normalized_code = normalize_index_code(code)
    payload: dict[str, Any] = {
        "code": normalized_code,
        "info": api.get_result(build_index_info_path(code)),
        "price": api.get_result(build_index_price_path(code)),
    }
    if include_chart:
        resolved_range, resolved_step = resolve_chart_window(chart_preset, chart_range, step)
        payload["chart"] = api.get_result(
            build_index_chart_path(code, securities_type, resolved_range, resolved_step, invest_mode)
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
    if include_mini_chart:
        payload["miniChart"] = api.get_result(
            build_mini_chart_path(),
            base_url=CERT_BASE_URL,
        )
    if include_related_etfs:
        payload["relatedEtfs"] = api.get_result(
            build_related_etfs_path(code),
            method="POST",
            body={},
        )
    if include_net_buying:
        payload["netBuying"] = {
            "range": api.get_result(
                build_net_buying_range_path(
                    code,
                    net_buying_range,
                    net_buying_from,
                    net_buying_count,
                )
            ),
            "daily": api.get_result(
                build_net_buying_daily_path(code, net_buying_from, net_buying_count)
            ),
        }
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
        default="auto",
        help="Observed r-chart securitiesType, e.g. auto, kr-s, or us-s",
    )
    parser.add_argument(
        "--chart-preset",
        choices=sorted(CHART_PRESETS),
        default="intraday",
        help="Convenience chart window preset; explicit --range/--step override it",
    )
    parser.add_argument("--range", dest="chart_range")
    parser.add_argument("--step")
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
        "--include-mini-chart",
        action="store_true",
        help="Also fetch public-looking overview indicator mini-chart metadata",
    )
    parser.add_argument(
        "--include-related-etfs",
        action="store_true",
        help="Also fetch related ETF metadata for the selected index/indicator code",
    )
    parser.add_argument(
        "--include-net-buying",
        action="store_true",
        help="Also fetch index net-buying range and daily widgets",
    )
    parser.add_argument(
        "--net-buying-from",
        default=date.today().isoformat(),
        help="Anchor date for --include-net-buying, YYYY-MM-DD",
    )
    parser.add_argument(
        "--net-buying-range",
        default="week",
        help="Range query for the net-buying range widget",
    )
    parser.add_argument(
        "--net-buying-count",
        type=int,
        default=35,
        help="Row count for --include-net-buying range/daily widgets",
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
        chart_preset=args.chart_preset,
        chart_range=args.chart_range,
        step=args.step,
        invest_mode=args.invest_mode,
        include_chart=args.include_chart,
        include_fx_chart=args.include_fx_chart,
        include_indicators=args.include_indicators,
        include_exchange_rates=args.include_exchange_rates,
        include_mini_chart=args.include_mini_chart,
        include_related_etfs=args.include_related_etfs,
        include_net_buying=args.include_net_buying,
        fx_chart_range=args.fx_range,
        fx_step=args.fx_step,
        fx_currency=args.fx_currency,
        indicator_type=args.indicator_type,
        market=args.market,
        net_buying_from=args.net_buying_from,
        net_buying_range=args.net_buying_range,
        net_buying_count=args.net_buying_count,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
