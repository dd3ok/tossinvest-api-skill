#!/usr/bin/env python3
"""Fetch read-only TossInvest company news."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

ORDER_BY_VALUES = {"latest", "relevant"}


def build_company_news_path(
    code: str,
    size: int,
    page: int = 1,
    order_by: str | None = None,
) -> str:
    page = api.require_int_range("page", page, minimum=1, maximum=1000)
    normalized_order_by = validate_order_by(order_by)
    return api.build_path(
        f"/api/v2/news/companies/{api.to_company_code(code)}",
        {
            "size": size,
            "number": page if page > 1 else None,
            "orderBy": normalized_order_by,
        },
    )


def validate_order_by(order_by: str | None) -> str | None:
    if order_by is None:
        return None
    normalized = order_by.strip().lower()
    if normalized not in ORDER_BY_VALUES:
        expected = ", ".join(sorted(ORDER_BY_VALUES))
        raise ValueError(f"order-by must be one of: {expected}")
    return normalized


def build_news_detail_path(news_id: str) -> str:
    return f"/api/v2/news/{news_id}"


def fetch_news(
    code: str,
    size: int,
    news_id: str | None,
    *,
    page: int = 1,
    order_by: str | None = None,
) -> dict[str, Any]:
    size = api.require_int_range("size", size, minimum=1, maximum=100)
    page = api.require_int_range("page", page, minimum=1, maximum=1000)
    payload: dict[str, Any] = {
        "code": api.normalize_product_code(code),
        "companyCode": api.to_company_code(code),
        "page": page,
        "size": size,
        "orderBy": validate_order_by(order_by),
        "news": api.get_result(build_company_news_path(code, size, page, order_by)),
    }
    if news_id is not None:
        payload["detail"] = api.get_result(build_news_detail_path(news_id))
    return payload


def rows_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    news = payload.get("news")
    body = news.get("body") if isinstance(news, dict) else None
    if not isinstance(body, list):
        raise RuntimeError("Unexpected company news response shape")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest company news for a stock/company code."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument("--size", type=int, default=10, help="Rows to request")
    parser.add_argument("--page", type=int, default=1, help="Company-news page number")
    parser.add_argument(
        "--order-by",
        choices=sorted(ORDER_BY_VALUES),
        help="Observed company-news ordering selector",
    )
    parser.add_argument("--news-id", help="Also fetch a specific news detail")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--output", help="Write output to a file")
    args = parser.parse_args()

    payload = fetch_news(args.code, args.size, args.news_id, page=args.page, order_by=args.order_by)
    text = (
        api.render_csv(rows_from_payload(payload))
        if args.format == "csv"
        else api.render_json(payload)
    )
    api.emit_output(text, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
