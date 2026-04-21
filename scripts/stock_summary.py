#!/usr/bin/env python3
"""Fetch a compact TossInvest stock summary."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api


def merge_summary(
    code: str,
    *,
    info: dict[str, Any],
    price_rows: list[dict[str, Any]],
    overview: dict[str, Any] | None,
) -> dict[str, Any]:
    product_code = api.normalize_product_code(code)
    return {
        "code": product_code,
        "info": info,
        "price": api.find_by_code(price_rows, product_code),
        "overview": overview,
    }


def fetch_stock_summary(code: str, include_overview: bool) -> dict[str, Any]:
    product_code = api.normalize_product_code(code)
    info = api.get_result(f"/api/v2/stock-infos/{product_code}")
    price_rows = api.get_result(
        api.build_path(
            "/api/v3/stock-prices/details",
            {"productCodes": product_code},
        )
    )
    if not isinstance(price_rows, list):
        raise RuntimeError("Unexpected price details response shape")
    overview = (
        api.get_result(f"/api/v2/stock-infos/{product_code}/overview") if include_overview else None
    )
    return merge_summary(
        product_code,
        info=info,
        price_rows=price_rows,
        overview=overview,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest stock metadata, price detail, and overview."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--no-overview",
        action="store_true",
        help="Skip /overview request and return only info plus price",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_stock_summary(args.code, include_overview=not args.no_overview)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
