#!/usr/bin/env python3
"""Fetch read-only TossInvest company filing lists."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api


def build_filings_path(code: str, page: int, size: int, key: str | None) -> str:
    return api.build_path(
        f"/api/v1/stock-detail/companies/{api.company_code_path_segment(code)}/filings",
        {"number": page, "size": size, "key": key},
    )


def fetch_filings(
    code: str,
    page: int,
    size: int,
    key: str | None,
    *,
    company_code: str | None = None,
) -> dict[str, Any]:
    page = api.require_int_range("page", page, minimum=1, maximum=1000)
    size = api.require_int_range("size", size, minimum=1, maximum=100)
    if key is not None and not isinstance(key, str):
        raise ValueError("key must be a string returned by the previous response")
    resolved_company_code = api.resolve_company_code(code, company_code=company_code)
    result = api.get_result(build_filings_path(resolved_company_code, page, size, key))
    return {
        "code": api.normalize_product_code(code),
        "companyCode": resolved_company_code,
        "page": page,
        "size": size,
        "key": key,
        "result": result,
    }


def rows_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("result")
    body = result.get("body") if isinstance(result, dict) else None
    if not isinstance(body, list):
        raise RuntimeError("Unexpected filings response shape")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest filing list for a stock/company code."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--company-code",
        help="Use an already observed company ID for --code without metadata lookup",
    )
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--size", type=int, default=20, help="Rows per page")
    parser.add_argument("--key", help="Paging key from a previous response")
    parser.add_argument("--format", choices=["json", "csv"], default="json")
    parser.add_argument("--output", help="Write output to a file")
    args = parser.parse_args()

    payload = fetch_filings(
        args.code, args.page, args.size, args.key, company_code=args.company_code
    )
    if args.format == "csv":
        text = api.render_csv(rows_from_payload(payload))
    else:
        text = api.render_json(payload)
    api.emit_output(text, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
