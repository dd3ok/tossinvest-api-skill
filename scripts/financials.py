#!/usr/bin/env python3
"""Fetch read-only TossInvest financial and valuation endpoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import tossinvest_api as api

FINANCIAL_PATHS = {
    "comprehensive": "/api/v2/companies/{code}/financial-statements/comprehensive",
    "records": "/api/v2/companies/{code}/financial-statement-records",
    "estimate-date": "/api/v2/companies/{code}/financial/estimate/date",
    "estimate-revenue": "/api/v2/companies/{code}/financial/estimate/revenue",
    "estimate-eps": "/api/v2/companies/{code}/financial/estimate/eps",
    "estimate-operating-income": "/api/v2/companies/{code}/financial/estimate/operating-income",
    "valuation": "/api/v2/stock-infos/evaluation/{code}",
    "valuation-comparison": "/api/v2/stock-infos/evaluation-comparison/{code}",
    "stability": "/api/v2/stock-infos/stability/{code}",
    "revenue-net-profit": "/api/v2/stock-infos/revenue-and-net-profit/{code}",
    "operating-income": "/api/v2/stock-infos/operating-income/{code}",
}

GET_KINDS = {"estimate-date"}


def build_financial_path(code: str, kind: str) -> str:
    if kind not in FINANCIAL_PATHS:
        raise ValueError(f"unknown financial kind: {kind}")
    return FINANCIAL_PATHS[kind].format(code=api.normalize_product_code(code))


def fetch_financials(
    code: str,
    kind: str,
    body: dict[str, Any] | None,
    *,
    allow_custom_body: bool = False,
) -> dict[str, Any]:
    method = "GET" if kind in GET_KINDS else "POST"
    result = api.get_result(
        build_financial_path(code, kind),
        method=method,
        body=None if method == "GET" else validate_body(body or {}, allow_custom_body),
    )
    return {
        "code": api.normalize_product_code(code),
        "kind": kind,
        "result": result,
    }


def validate_body(body: dict[str, Any], allow_custom: bool) -> dict[str, Any]:
    if body and not allow_custom:
        raise ValueError(
            "custom financial POST bodies require --allow-custom-body and current UI reverification"
        )
    return body


def load_body(path: str | None, *, allow_custom: bool = False) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("body file must contain a JSON object")
    return validate_body(payload, allow_custom)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest financial statement, estimate, or valuation data."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--kind",
        choices=sorted(FINANCIAL_PATHS),
        default="comprehensive",
        help="Financial endpoint to call",
    )
    parser.add_argument(
        "--body-file",
        help="Optional JSON object body for POST endpoints; defaults to {}",
    )
    parser.add_argument(
        "--allow-custom-body",
        action="store_true",
        help="Allow non-empty POST bodies after rechecking the current public UI request",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_financials(
        args.code,
        args.kind,
        load_body(args.body_file, allow_custom=args.allow_custom_body),
        allow_custom_body=args.allow_custom_body,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
