#!/usr/bin/env python3
"""Fetch read-only TossInvest index and market-indicator dashboard data."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from typing import Any

import tossinvest_api as api

CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"
CHART_PRESETS = {
    "intraday": ("1d", "min:5"),
    "quarter": ("3m", "day:1"),
    "daily": ("1y", "day:1"),
}
ALLOWED_SECURITIES_TYPES = {"auto", "crypto", "kr-s", "us-s"}
ALLOWED_INDICATOR_TYPES = {"bond", "commodity", "index"}
ALLOWED_MARKETS = {"kr", "us"}
ALLOWED_NET_BUYING_RANGES = {"month", "week", "year"}
ALLOWED_INVEST_MODES = {"krx"}


def normalize_index_code(code: str) -> str:
    value = code.strip()
    if "." in value:
        return value
    return value.upper()


def infer_securities_type(code: str, securities_type: str) -> str:
    normalized = securities_type.strip().lower()
    if normalized != "auto":
        _require_choice("securities_type", normalized, ALLOWED_SECURITIES_TYPES - {"auto"})
        return normalized
    normalized_code = normalize_index_code(code)
    if normalized_code.upper().startswith("VWAP.KRW-"):
        return "crypto"
    if "." in normalized_code:
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
    invest_mode = _require_choice("invest_mode", invest_mode, ALLOWED_INVEST_MODES)
    return api.build_path(
        (
            f"/api/v1/r-chart/{resolved_securities_type}/"
            f"{normalize_index_code(code)}/{chart_range}/{step}"
        ),
        {"session": "main", "investMode": invest_mode, "last": False},
    )


def build_index_daily_quotes_path(
    code: str,
    securities_type: str,
    count: int,
    from_cursor: str | None,
) -> str:
    resolved_securities_type = infer_securities_type(code, securities_type)
    count = api.require_int_range("daily-quote-count", count, minimum=1, maximum=100)
    cursor = _validate_daily_quote_cursor(from_cursor)
    return api.build_path(
        f"/api/v1/c-chart/{resolved_securities_type}/{normalize_index_code(code)}/day:1",
        {
            "count": count,
            "from": cursor,
            "useAdjustedRate": True,
        },
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


def build_crypto_prices_path(product_codes: list[str]) -> str:
    if not product_codes:
        raise ValueError("product_codes must contain at least one code")
    normalized_codes = ",".join(normalize_index_code(code) for code in product_codes)
    return api.build_path("/api/v1/crypto-prices", {"productCodes": normalized_codes})


def build_product_exchange_rate_path(buy_currency: str, sell_currency: str) -> str:
    return api.build_path(
        "/api/v1/product/exchange-rate",
        {
            "buyCurrency": buy_currency.strip().upper(),
            "sellCurrency": sell_currency.strip().upper(),
        },
    )


def build_indicator_path(indicator_type: str, market: str | None) -> str:
    indicator_type = _require_choice("indicator_type", indicator_type, ALLOWED_INDICATOR_TYPES)
    market = _require_optional_choice("market", market, ALLOWED_MARKETS)
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
    net_range = _require_choice("net_range", net_range, ALLOWED_NET_BUYING_RANGES)
    return api.build_path(
        "/api/v1/stock-infos/index/net-buying/range",
        {
            "code": normalize_index_code(code),
            "range": net_range,
            "from": from_date,
            "count": count,
        },
    )


def _require_choice(name: str, value: str, choices: set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in choices:
        expected = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {expected}")
    return normalized


def _require_optional_choice(name: str, value: str | None, choices: set[str]) -> str | None:
    if value is None:
        return None
    return _require_choice(name, value, choices)


def _validate_daily_quote_cursor(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("daily quote cursor must be an ISO 8601 datetime with timezone") from exc
    if parsed.tzinfo is None:
        raise ValueError("daily quote cursor must include a timezone")
    return normalized


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
    include_crypto_prices: bool,
    include_product_exchange_rate: bool,
    include_mini_chart: bool,
    include_related_etfs: bool,
    include_net_buying: bool,
    fx_chart_range: str,
    fx_step: str,
    fx_currency: str,
    exchange_buy_currency: str,
    exchange_sell_currency: str,
    indicator_type: str,
    market: str | None,
    net_buying_from: str,
    net_buying_range: str,
    net_buying_count: int,
    include_daily_quotes: bool = False,
    daily_quote_count: int = 20,
    daily_quote_from: str | None = None,
) -> dict[str, Any]:
    net_buying_count = api.require_int_range(
        "net-buying-count",
        net_buying_count,
        minimum=1,
        maximum=120,
    )
    normalized_code = normalize_index_code(code)
    payload: dict[str, Any] = {
        "code": normalized_code,
        "info": api.get_result(build_index_info_path(code)),
        "price": api.get_result(build_index_price_path(code)),
    }
    if include_chart:
        resolved_range, resolved_step = resolve_chart_window(chart_preset, chart_range, step)
        payload["chart"] = api.get_result(
            build_index_chart_path(
                code, securities_type, resolved_range, resolved_step, invest_mode
            )
        )
    if include_daily_quotes:
        payload["dailyQuoteRequest"] = {
            "count": daily_quote_count,
            "from": daily_quote_from,
        }
        payload["dailyQuotes"] = api.get_result(
            build_index_daily_quotes_path(
                code,
                securities_type,
                daily_quote_count,
                daily_quote_from,
            )
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
    if include_crypto_prices:
        payload["cryptoPrices"] = api.get_result(build_crypto_prices_path([normalized_code]))
    if include_product_exchange_rate:
        payload["productExchangeRate"] = api.get_result(
            build_product_exchange_rate_path(exchange_buy_currency, exchange_sell_currency)
        )
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
        choices=sorted(ALLOWED_SECURITIES_TYPES),
        help="Verified r-chart securitiesType",
    )
    parser.add_argument(
        "--chart-preset",
        choices=sorted(CHART_PRESETS),
        default="intraday",
        help="Convenience chart window preset; explicit --range/--step override it",
    )
    parser.add_argument("--range", dest="chart_range")
    parser.add_argument("--step")
    parser.add_argument("--invest-mode", default="krx", choices=sorted(ALLOWED_INVEST_MODES))
    parser.add_argument("--include-chart", action="store_true")
    parser.add_argument(
        "--include-daily-quotes",
        action="store_true",
        help="Also fetch the visible daily quote table with cursor paging metadata",
    )
    parser.add_argument(
        "--daily-quote-count",
        type=int,
        default=20,
        help="Rows for --include-daily-quotes (1-100)",
    )
    parser.add_argument(
        "--daily-quote-from",
        help="Optional nextDateTime cursor from a previous daily quote response",
    )
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
        help="Also fetch the public dashboard exchange-rates widget",
    )
    parser.add_argument(
        "--include-crypto-prices",
        action="store_true",
        help="Also fetch crypto price metadata for the selected index-like crypto code",
    )
    parser.add_argument(
        "--include-product-exchange-rate",
        action="store_true",
        help="Also fetch the public product exchange-rate pair",
    )
    parser.add_argument(
        "--exchange-buy-currency",
        default="USD",
        help="Buy currency for --include-product-exchange-rate",
    )
    parser.add_argument(
        "--exchange-sell-currency",
        default="KRW",
        help="Sell currency for --include-product-exchange-rate",
    )
    parser.add_argument(
        "--include-mini-chart",
        action="store_true",
        help="Also fetch public overview indicator mini-chart metadata",
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
        choices=sorted(ALLOWED_NET_BUYING_RANGES),
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
        choices=sorted(ALLOWED_INDICATOR_TYPES),
        help="Verified dashboard indicator type",
    )
    parser.add_argument(
        "--market",
        default="kr",
        choices=sorted(ALLOWED_MARKETS),
        help="Indicator market query value",
    )
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
        include_crypto_prices=args.include_crypto_prices,
        include_product_exchange_rate=args.include_product_exchange_rate,
        include_mini_chart=args.include_mini_chart,
        include_related_etfs=args.include_related_etfs,
        include_net_buying=args.include_net_buying,
        fx_chart_range=args.fx_range,
        fx_step=args.fx_step,
        fx_currency=args.fx_currency,
        exchange_buy_currency=args.exchange_buy_currency,
        exchange_sell_currency=args.exchange_sell_currency,
        indicator_type=args.indicator_type,
        market=args.market,
        net_buying_from=args.net_buying_from,
        net_buying_range=args.net_buying_range,
        net_buying_count=args.net_buying_count,
        include_daily_quotes=args.include_daily_quotes,
        daily_quote_count=args.daily_quote_count,
        daily_quote_from=args.daily_quote_from,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
