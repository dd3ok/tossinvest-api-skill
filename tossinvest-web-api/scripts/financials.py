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


def fetch_financials(code: str, kind: str, body: dict[str, Any] | None) -> dict[str, Any]:
    method = "GET" if kind in GET_KINDS else "POST"
    result = api.get_result(
        build_financial_path(code, kind),
        method=method,
        body=None if method == "GET" else body or {},
    )
    return {
        "code": api.normalize_product_code(code),
        "kind": kind,
        "result": result,
    }


def load_body(path: str | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("body file must contain a JSON object")
    return payload


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
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_financials(args.code, args.kind, load_body(args.body_file))
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
