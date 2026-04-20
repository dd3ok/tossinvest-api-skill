#!/usr/bin/env python3
"""Fetch stock candle chart data and optional local RSI from TossInvest APIs."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api


def build_chart_path(
    code: str,
    securities_type: str,
    range_value: str,
    count: int,
    session: str | None,
    invest_mode: str | None,
    use_adjusted_rate: bool | None,
    from_datetime: str | None = None,
    currency: str | None = None,
) -> str:
    return api.build_path(
        f"/api/v1/c-chart/{securities_type}/{api.normalize_product_code(code)}/{range_value}",
        {
            "count": count,
            "from": from_datetime,
            "session": session,
            "investMode": invest_mode,
            "useAdjustedRate": use_adjusted_rate,
            "currency": currency,
        },
    )


def add_rsi(candles: list[dict[str, Any]], *, period: int = 14) -> list[dict[str, Any]]:
    if period <= 0:
        raise ValueError("period must be positive")

    enriched = [dict(candle) for candle in candles]
    field_name = f"rsi{period}"
    for candle in enriched:
        candle[field_name] = None

    ordered = _chronological_order(candles)
    closes = [_to_float(candle.get("close")) for _, candle in ordered]
    if any(close is None for close in closes):
        return enriched

    values = _calculate_wilder_rsi([close for close in closes if close is not None], period)
    for (original_index, _), value in zip(ordered, values):
        enriched[original_index][field_name] = value
    return enriched


def fetch_chart(
    code: str,
    *,
    securities_type: str,
    range_value: str,
    count: int,
    session: str | None,
    invest_mode: str | None,
    use_adjusted_rate: bool | None,
    from_datetime: str | None,
    currency: str | None,
    rsi_period: int | None,
) -> dict[str, Any]:
    path = build_chart_path(
        code,
        securities_type,
        range_value,
        count,
        session,
        invest_mode,
        use_adjusted_rate,
        from_datetime,
        currency,
    )
    chart = api.get_result(path)
    payload: dict[str, Any] = {
        "code": api.normalize_product_code(code),
        "path": path,
        "chart": chart,
    }
    if rsi_period is not None:
        chart = dict(chart)
        chart["candles"] = add_rsi(chart.get("candles", []), period=rsi_period)
        payload["chart"] = chart
        payload["technicalIndicators"] = {
            "rsi": {
                "period": rsi_period,
                "source": "local-calculation-from-c-chart-candles",
                "priceField": "close",
            }
        }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest c-chart candles and optionally add local RSI."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--securities-type",
        default="kr-s",
        help="Observed c-chart securities type, e.g. kr-s for Korean stocks",
    )
    parser.add_argument(
        "--range",
        dest="range_value",
        default="day:1",
        help="Observed c-chart range such as min:1, day:1, week:1, month:1",
    )
    parser.add_argument("--count", type=int, default=61, help="Number of candles")
    parser.add_argument("--session", default="all", help="Observed session query value")
    parser.add_argument(
        "--invest-mode",
        default="krx",
        help="Observed investMode query value, e.g. krx for Korean stocks",
    )
    parser.add_argument(
        "--no-adjusted-rate",
        action="store_true",
        help="Send useAdjustedRate=false instead of the observed default true",
    )
    parser.add_argument("--from", dest="from_datetime", help="Optional from query value")
    parser.add_argument("--currency", help="Optional currency query value")
    parser.add_argument(
        "--rsi-period",
        type=int,
        metavar="N",
        help="Add locally calculated Wilder RSI using close prices",
    )
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_chart(
        args.code,
        securities_type=args.securities_type,
        range_value=args.range_value,
        count=args.count,
        session=args.session,
        invest_mode=args.invest_mode,
        use_adjusted_rate=not args.no_adjusted_rate,
        from_datetime=args.from_datetime,
        currency=args.currency,
        rsi_period=args.rsi_period,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


def _chronological_order(candles: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    indexed = list(enumerate(candles))
    if all(isinstance(candle.get("dt"), str) for _, candle in indexed):
        return sorted(indexed, key=lambda item: item[1]["dt"])
    return indexed


def _calculate_wilder_rsi(closes: list[float], period: int) -> list[float | None]:
    values: list[float | None] = [None] * len(closes)
    if len(closes) <= period:
        return values

    gains = []
    losses = []
    for index in range(1, period + 1):
        delta = closes[index] - closes[index - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period
    values[period] = _rsi_value(average_gain, average_loss)

    for index in range(period + 1, len(closes)):
        delta = closes[index] - closes[index - 1]
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)
        average_gain = ((average_gain * (period - 1)) + gain) / period
        average_loss = ((average_loss * (period - 1)) + loss) / period
        values[index] = _rsi_value(average_gain, average_loss)

    return values


def _rsi_value(average_gain: float, average_loss: float) -> float:
    if average_loss == 0:
        return 100.0 if average_gain > 0 else 50.0
    relative_strength = average_gain / average_loss
    return round(100 - (100 / (1 + relative_strength)), 2)


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
