#!/usr/bin/env python3
"""Fetch read-only quote and tick data from TossInvest web APIs."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

MAX_TICK_COUNT = 100


def build_quote_path(
    code: str,
    invest_mode: str | None,
    view_type: str | None,
    fallback_krx: bool | None,
) -> str:
    return api.build_path(
        f"/api/v3/stock-prices/{api.normalize_product_code(code)}/quotes",
        {
            "investMode": invest_mode,
            "viewType": view_type,
            "fallbackKrx": fallback_krx,
        },
    )


def build_ticks_path(code: str, invest_mode: str | None, view_type: str | None, count: int) -> str:
    return api.build_path(
        f"/api/v2/stock-prices/{api.normalize_product_code(code)}/ticks",
        {
            "viewType": view_type,
            "count": count,
            "investMode": invest_mode,
        },
    )


def fetch_quote(
    code: str,
    *,
    invest_mode: str | None,
    view_type: str | None,
    fallback_krx: bool | None,
    tick_count: int | None,
) -> dict[str, Any]:
    if tick_count is not None:
        tick_count = api.require_int_range(
            "ticks",
            tick_count,
            minimum=1,
            maximum=MAX_TICK_COUNT,
        )
    payload: dict[str, Any] = {
        "code": api.normalize_product_code(code),
        "quote": api.get_result(build_quote_path(code, invest_mode, view_type, fallback_krx)),
    }
    if tick_count is not None:
        payload["ticks"] = api.get_result(
            build_ticks_path(code, invest_mode, view_type, tick_count)
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest quote book and optional intraday ticks."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--invest-mode",
        default="krx",
        help="Observed investMode query value, e.g. krx for Korean stocks",
    )
    parser.add_argument("--view-type", help="Optional quote/tick viewType")
    parser.add_argument(
        "--fallback-krx",
        action="store_true",
        help="Include fallbackKrx=true in the quote query",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        metavar="COUNT",
        help="Also fetch this many intraday tick rows",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_quote(
        args.code,
        invest_mode=args.invest_mode,
        view_type=args.view_type,
        fallback_krx=True if args.fallback_krx else None,
        tick_count=args.ticks,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
