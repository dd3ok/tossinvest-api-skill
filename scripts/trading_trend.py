#!/usr/bin/env python3
"""Fetch read-only TossInvest trading trend endpoints."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

RECENT_TYPES = {
    "investor": "trading-trend",
    "program": "program-trading",
}

FIXED_TYPES = {
    "fixed": "fixed-trading-trend",
    "accumulated": "accumulated-fixed-trading-trend",
    "accumulated-detail": "accumulated-fixed-trading-trend/detail",
}


def build_trend_path(
    code: str,
    trend_type: str,
    size: int | None,
    start: str | None,
    end: str | None,
) -> str:
    product_code = api.normalize_product_code(code)
    if trend_type in RECENT_TYPES:
        return api.build_path(
            f"/api/v1/stock-infos/trade/trend/{RECENT_TYPES[trend_type]}",
            {"productCode": product_code, "size": size},
        )
    if trend_type in FIXED_TYPES:
        if start is None or end is None:
            raise ValueError(f"{trend_type} requires --from and --to")
        return api.build_path(
            f"/api/v1/stock-infos/trade/trend/{FIXED_TYPES[trend_type]}",
            {"productCode": product_code, "from": start, "to": end},
        )
    if trend_type == "broker":
        return api.build_path("/api/v1/mds/broker/trading-ranking", {"code": product_code})
    if trend_type == "credit":
        return api.build_path(
            "/api/v1/mds/info/credit",
            {"stockCode": product_code, "number": 1, "size": size},
        )
    raise ValueError(f"unknown trend type: {trend_type}")


def fetch_trading_trend(
    code: str,
    trend_type: str,
    size: int | None,
    start: str | None,
    end: str | None,
) -> dict[str, Any]:
    if size is not None:
        size = api.require_int_range("size", size, minimum=1, maximum=120)
    return {
        "code": api.normalize_product_code(code),
        "type": trend_type,
        "result": api.get_result(build_trend_path(code, trend_type, size, start, end)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest investor, program, fixed, broker, or credit trend data."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--type",
        choices=sorted([*RECENT_TYPES, *FIXED_TYPES, "broker", "credit"]),
        default="investor",
        help="Trend endpoint to call",
    )
    parser.add_argument("--size", type=int, default=60, help="Rows for recent/paged endpoints")
    parser.add_argument("--from", dest="start", help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="end", help="End date YYYY-MM-DD")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_trading_trend(args.code, args.type, args.size, args.start, args.end)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
