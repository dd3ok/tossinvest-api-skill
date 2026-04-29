#!/usr/bin/env python3
"""Fetch stock candle chart data and optional local indicators from TossInvest APIs."""

from __future__ import annotations

import argparse
import math
from typing import Any

import tossinvest_api as api

MAX_CANDLE_COUNT = 500
ALLOWED_SECURITIES_TYPES = {"kr-s", "us-s"}
ALLOWED_RANGES = {"min:1", "day:1", "week:1", "month:1"}
ALLOWED_SESSIONS = {"all"}
ALLOWED_INVEST_MODES = {"krx"}
ALLOWED_CURRENCIES = {"KRW", "USD"}


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
    securities_type = _require_choice("securities_type", securities_type, ALLOWED_SECURITIES_TYPES)
    range_value = _require_choice("range_value", range_value, ALLOWED_RANGES)
    session = _require_optional_choice("session", session, ALLOWED_SESSIONS)
    invest_mode = _require_optional_choice("invest_mode", invest_mode, ALLOWED_INVEST_MODES)
    currency = _require_optional_choice(
        "currency", currency, ALLOWED_CURRENCIES, normalize=str.upper
    )
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


def _require_choice(name: str, value: str, choices: set[str]) -> str:
    normalized = value.strip()
    if normalized not in choices:
        expected = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {expected}")
    return normalized


def _require_optional_choice(
    name: str,
    value: str | None,
    choices: set[str],
    *,
    normalize: Any | None = None,
) -> str | None:
    if value is None:
        return None
    normalized = normalize(value.strip()) if normalize else value.strip()
    if normalized not in choices:
        expected = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {expected}")
    return normalized


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


def add_sma(candles: list[dict[str, Any]], *, period: int) -> list[dict[str, Any]]:
    _validate_period(period, "period")
    return _add_calculated_values(
        candles,
        f"sma{period}",
        _calculate_chronological(candles, lambda closes: _calculate_sma(closes, period)),
    )


def add_ema(candles: list[dict[str, Any]], *, period: int) -> list[dict[str, Any]]:
    _validate_period(period, "period")
    return _add_calculated_values(
        candles,
        f"ema{period}",
        _calculate_chronological(candles, lambda closes: _calculate_ema(closes, period)),
    )


def add_bollinger_bands(
    candles: list[dict[str, Any]], *, period: int = 20, stddev: float = 2.0
) -> list[dict[str, Any]]:
    _validate_period(period, "period")
    if stddev <= 0:
        raise ValueError("stddev must be positive")

    middle = _calculate_chronological(candles, lambda closes: _calculate_sma(closes, period))
    upper = _calculate_chronological(
        candles, lambda closes: _calculate_bollinger_side(closes, period, stddev, "upper")
    )
    lower = _calculate_chronological(
        candles, lambda closes: _calculate_bollinger_side(closes, period, stddev, "lower")
    )

    enriched = _add_calculated_values(candles, f"bb{period}Middle", middle)
    enriched = _add_calculated_values(enriched, f"bb{period}Upper", upper)
    return _add_calculated_values(enriched, f"bb{period}Lower", lower)


def add_macd(
    candles: list[dict[str, Any]],
    *,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> list[dict[str, Any]]:
    _validate_period(fast_period, "fast_period")
    _validate_period(slow_period, "slow_period")
    _validate_period(signal_period, "signal_period")
    if fast_period >= slow_period:
        raise ValueError("fast_period must be smaller than slow_period")

    closes = _ordered_close_values(candles)[1]
    fast = _calculate_ema(closes, fast_period)
    slow = _calculate_ema(closes, slow_period)
    macd = [
        None if fast_value is None or slow_value is None else round(fast_value - slow_value, 2)
        for fast_value, slow_value in zip(fast, slow)
    ]
    signal = _calculate_ema_from_optional(macd, signal_period)
    histogram = [
        None if macd_value is None or signal_value is None else round(macd_value - signal_value, 2)
        for macd_value, signal_value in zip(macd, signal)
    ]

    macd = _restore_original_order(candles, macd)
    signal = _restore_original_order(candles, signal)
    histogram = _restore_original_order(candles, histogram)

    enriched = _add_calculated_values(candles, "macd", macd)
    enriched = _add_calculated_values(enriched, "macdSignal", signal)
    return _add_calculated_values(enriched, "macdHistogram", histogram)


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
    sma_periods: list[int],
    ema_periods: list[int],
    bollinger_period: int | None,
    bollinger_stddev: float,
    include_macd: bool,
    macd_fast: int,
    macd_slow: int,
    macd_signal: int,
) -> dict[str, Any]:
    count = api.require_int_range("count", count, minimum=1, maximum=MAX_CANDLE_COUNT)
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
    indicators: dict[str, Any] = {}
    if rsi_period is not None:
        chart = dict(chart)
        chart["candles"] = add_rsi(chart.get("candles", []), period=rsi_period)
        payload["chart"] = chart
        indicators["rsi"] = {
            "period": rsi_period,
            "source": "local-calculation-from-c-chart-candles",
            "priceField": "close",
        }
    for period in sma_periods:
        chart = dict(payload["chart"])
        chart["candles"] = add_sma(chart.get("candles", []), period=period)
        payload["chart"] = chart
        indicators[f"sma{period}"] = _indicator_note(period)
    for period in ema_periods:
        chart = dict(payload["chart"])
        chart["candles"] = add_ema(chart.get("candles", []), period=period)
        payload["chart"] = chart
        indicators[f"ema{period}"] = _indicator_note(period)
    if bollinger_period is not None:
        chart = dict(payload["chart"])
        chart["candles"] = add_bollinger_bands(
            chart.get("candles", []), period=bollinger_period, stddev=bollinger_stddev
        )
        payload["chart"] = chart
        indicators[f"bollinger{bollinger_period}"] = {
            **_indicator_note(bollinger_period),
            "stddev": bollinger_stddev,
        }
    if include_macd:
        chart = dict(payload["chart"])
        chart["candles"] = add_macd(
            chart.get("candles", []),
            fast_period=macd_fast,
            slow_period=macd_slow,
            signal_period=macd_signal,
        )
        payload["chart"] = chart
        indicators["macd"] = {
            "fastPeriod": macd_fast,
            "slowPeriod": macd_slow,
            "signalPeriod": macd_signal,
            "source": "local-calculation-from-c-chart-candles",
            "priceField": "close",
        }
    if indicators:
        payload["technicalIndicators"] = indicators
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch TossInvest c-chart candles and optionally add local RSI, "
            "SMA, EMA, MACD, and Bollinger Bands."
        )
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--securities-type",
        default="kr-s",
        choices=sorted(ALLOWED_SECURITIES_TYPES),
        help="Verified c-chart securities type",
    )
    parser.add_argument(
        "--range",
        dest="range_value",
        default="day:1",
        choices=sorted(ALLOWED_RANGES),
        help="Verified c-chart range",
    )
    parser.add_argument("--count", type=int, default=61, help="Number of candles")
    parser.add_argument(
        "--session",
        default="all",
        choices=sorted(ALLOWED_SESSIONS),
        help="Verified session query value",
    )
    parser.add_argument(
        "--invest-mode",
        default="krx",
        choices=sorted(ALLOWED_INVEST_MODES),
        help="Verified investMode query value",
    )
    parser.add_argument(
        "--no-adjusted-rate",
        action="store_true",
        help="Send useAdjustedRate=false instead of the observed default true",
    )
    parser.add_argument("--from", dest="from_datetime", help="Optional from query value")
    parser.add_argument(
        "--currency", choices=sorted(ALLOWED_CURRENCIES), help="Optional currency query value"
    )
    parser.add_argument(
        "--rsi-period",
        type=int,
        metavar="N",
        help="Add locally calculated Wilder RSI using close prices",
    )
    parser.add_argument(
        "--sma-period",
        type=int,
        action="append",
        default=[],
        metavar="N",
        help="Add locally calculated simple moving average; repeatable",
    )
    parser.add_argument(
        "--ema-period",
        type=int,
        action="append",
        default=[],
        metavar="N",
        help="Add locally calculated exponential moving average; repeatable",
    )
    parser.add_argument(
        "--bollinger-period",
        type=int,
        metavar="N",
        help="Add locally calculated Bollinger Bands using this period",
    )
    parser.add_argument(
        "--bollinger-stddev",
        type=float,
        default=2.0,
        help="Standard deviation multiplier for Bollinger Bands",
    )
    parser.add_argument(
        "--macd",
        action="store_true",
        help="Add locally calculated MACD using close prices",
    )
    parser.add_argument("--macd-fast", type=int, default=12, help="MACD fast EMA period")
    parser.add_argument("--macd-slow", type=int, default=26, help="MACD slow EMA period")
    parser.add_argument("--macd-signal", type=int, default=9, help="MACD signal EMA period")
    api.add_json_format_argument(parser)
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
        sma_periods=args.sma_period,
        ema_periods=args.ema_period,
        bollinger_period=args.bollinger_period,
        bollinger_stddev=args.bollinger_stddev,
        include_macd=args.macd,
        macd_fast=args.macd_fast,
        macd_slow=args.macd_slow,
        macd_signal=args.macd_signal,
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


def _calculate_sma(closes: list[float | None], period: int) -> list[float | None]:
    values: list[float | None] = [None] * len(closes)
    for index in range(period - 1, len(closes)):
        window = closes[index - period + 1 : index + 1]
        if any(value is None for value in window):
            continue
        numbers = [value for value in window if value is not None]
        values[index] = round(sum(numbers) / period, 2)
    return values


def _calculate_bollinger_side(
    closes: list[float | None], period: int, stddev: float, side: str
) -> list[float | None]:
    values: list[float | None] = [None] * len(closes)
    for index in range(period - 1, len(closes)):
        window = closes[index - period + 1 : index + 1]
        if any(value is None for value in window):
            continue
        numbers = [value for value in window if value is not None]
        mean = sum(numbers) / period
        deviation = math.sqrt(sum((value - mean) ** 2 for value in numbers) / period)
        if side == "upper":
            values[index] = round(mean + (stddev * deviation), 2)
        else:
            values[index] = round(mean - (stddev * deviation), 2)
    return values


def _calculate_ema(closes: list[float | None], period: int) -> list[float | None]:
    return _calculate_ema_from_optional(closes, period)


def _calculate_ema_from_optional(values: list[float | None], period: int) -> list[float | None]:
    results: list[float | None] = [None] * len(values)
    clean_start = _first_complete_window(values, period)
    if clean_start is None:
        return results

    window = values[clean_start : clean_start + period]
    seed = sum(value for value in window if value is not None) / period
    index = clean_start + period - 1
    results[index] = round(seed, 2)
    multiplier = 2 / (period + 1)
    previous: float | None = seed
    for index in range(index + 1, len(values)):
        value = values[index]
        if value is None:
            previous = None
            continue
        if previous is None:
            window = values[index - period + 1 : index + 1]
            if len(window) < period or any(window_value is None for window_value in window):
                continue
            previous = (
                sum(window_value for window_value in window if window_value is not None) / period
            )
            results[index] = round(previous, 2)
            continue
        previous = (value * multiplier) + (previous * (1 - multiplier))
        results[index] = round(previous, 2)
    return results


def _first_complete_window(values: list[float | None], period: int) -> int | None:
    for start in range(0, len(values) - period + 1):
        if all(value is not None for value in values[start : start + period]):
            return start
    return None


def _calculate_chronological(candles: list[dict[str, Any]], calculator: Any) -> list[float | None]:
    closes = _ordered_close_values(candles)[1]
    return _restore_original_order(candles, calculator(closes))


def _ordered_close_values(
    candles: list[dict[str, Any]],
) -> tuple[list[tuple[int, dict[str, Any]]], list[float | None]]:
    ordered = _chronological_order(candles)
    return ordered, [_to_float(candle.get("close")) for _, candle in ordered]


def _restore_original_order(
    candles: list[dict[str, Any]], ordered_values: list[float | None]
) -> list[float | None]:
    ordered = _chronological_order(candles)
    values: list[float | None] = [None] * len(candles)
    for (original_index, _), value in zip(ordered, ordered_values):
        values[original_index] = value
    return values


def _add_calculated_values(
    candles: list[dict[str, Any]], field_name: str, values: list[float | None]
) -> list[dict[str, Any]]:
    enriched = [dict(candle) for candle in candles]
    for candle, value in zip(enriched, values):
        candle[field_name] = value
    return enriched


def _indicator_note(period: int) -> dict[str, Any]:
    return {
        "period": period,
        "source": "local-calculation-from-c-chart-candles",
        "priceField": "close",
    }


def _validate_period(period: int, name: str) -> None:
    if period <= 0:
        raise ValueError(f"{name} must be positive")


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
    raise SystemExit(api.run_cli(main))
