#!/usr/bin/env python3
"""Fetch a public TossInvest stock page composite payload."""

from __future__ import annotations

import argparse
from typing import Any

import community_comments
import tossinvest_api as api

AI_PRODUCT_TYPES = {"stocks": "STOCKS", "index": "INDEX", "currency": "CURRENCY"}


def build_ai_signal_detail_path(code: str, product_type: str) -> str:
    normalized_type = _require_ai_product_type(product_type)
    return api.build_path(
        "/api/v1/dashboard/wts/overview/ai-signals/detail",
        {"productCode": api.normalize_product_code(code), "productType": normalized_type},
    )


def resolve_stock_info(code_or_symbol: str) -> dict[str, Any]:
    code = api.normalize_product_code(code_or_symbol)
    result = api.get_result(f"/api/v2/stock-infos/code-or-symbol/{code}")
    if not isinstance(result, dict):
        raise RuntimeError("Unexpected TossInvest response: stock info is not a dictionary")
    return result


def fetch_stock_page(
    code_or_symbol: str,
    *,
    include_ai_detail: bool,
    include_comments: bool,
    comment_sort: str,
    comment_limit: int,
    comment_pages: int,
    include_replies: bool,
) -> dict[str, Any]:
    info = resolve_stock_info(code_or_symbol)
    product_code = api.normalize_product_code(str(info.get("code") or code_or_symbol))
    price_rows = api.get_result(
        api.build_path("/api/v3/stock-prices/details", {"productCodes": product_code})
    )
    if not isinstance(price_rows, list):
        raise RuntimeError("Unexpected TossInvest response: price details is not a list")
    payload: dict[str, Any] = {
        "productCode": product_code,
        "info": info,
        "price": api.find_by_code(price_rows, product_code),
    }
    if include_ai_detail:
        payload["aiSignalDetail"] = api.get_result(
            build_ai_signal_detail_path(product_code, "stocks")
        )
    if include_comments:
        payload["community"] = community_comments.fetch_stock_comments(
            product_code,
            sort=comment_sort,
            pages=comment_pages,
            limit=comment_limit,
            include_replies=include_replies,
        )
    return payload


def _require_ai_product_type(product_type: str) -> str:
    key = product_type.strip().lower()
    if key not in AI_PRODUCT_TYPES:
        raise ValueError(f"product_type must be one of: {', '.join(sorted(AI_PRODUCT_TYPES))}")
    return AI_PRODUCT_TYPES[key]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a public TossInvest stock page composite payload."
    )
    parser.add_argument("--code", required=True, help="TossInvest product code or symbol")
    parser.add_argument(
        "--no-ai-detail",
        action="store_true",
        help="Skip public AI signal detail fetch",
    )
    parser.add_argument(
        "--no-comments",
        action="store_true",
        help="Skip sanitized public community comments",
    )
    parser.add_argument(
        "--comment-sort", choices=sorted(community_comments.COMMENT_SORTS), default="popular"
    )
    parser.add_argument("--comment-limit", type=int, default=5)
    parser.add_argument("--comment-pages", type=int, default=1)
    parser.add_argument("--include-replies", action="store_true")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_stock_page(
        args.code,
        include_ai_detail=not args.no_ai_detail,
        include_comments=not args.no_comments,
        comment_sort=args.comment_sort,
        comment_limit=args.comment_limit,
        comment_pages=args.comment_pages,
        include_replies=args.include_replies,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
