#!/usr/bin/env python3
"""Fetch read-only TossInvest financial, valuation, and dividend endpoints."""

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
    "dividend-summary": "/api/v1/stock-infos/dividend/{code}/summary",
    "dividend-years": "/api/v1/stock-infos/dividend/{code}/years",
    "dividend-yield-history": "/api/v1/stock-infos/{code}/dividends/yield-ratio/histories",
}

GET_KINDS = {"estimate-date", "dividend-summary", "dividend-years", "dividend-yield-history"}
STATEMENT_CODES = {"income": "INC", "balance": "BAL", "cash-flow": "CAS"}
PERIOD_CODES = {"quarter": "Q", "year": "Y"}


def build_financial_path(code: str, kind: str, *, years: int | None = None) -> str:
    if kind not in FINANCIAL_PATHS:
        raise ValueError(f"unknown financial kind: {kind}")
    path = FINANCIAL_PATHS[kind].format(code=api.normalize_product_code(code))
    if years is not None:
        if kind != "dividend-years":
            raise ValueError("--years requires --kind dividend-years")
        api.require_int_range("years", years, minimum=1, maximum=2_147_483_647)
        return api.build_path(path, {"years": years})
    return path


def fetch_financials(
    code: str,
    kind: str,
    body: dict[str, Any] | None,
    *,
    allow_custom_body: bool = False,
    statement: str | None = None,
    period: str | None = None,
    years: int | None = None,
) -> dict[str, Any]:
    path = build_financial_path(code, kind, years=years)
    method = "GET" if kind in GET_KINDS else "POST"
    if method == "GET" and body is not None:
        raise ValueError("GET financial endpoints do not accept a custom body")
    if statement is not None or period is not None:
        if kind != "records":
            raise ValueError("--statement and --period require --kind records")
        if body is not None:
            raise ValueError("--statement and --period cannot be combined with a custom body")
        request_body = build_records_body(
            "income" if statement is None else statement,
            "quarter" if period is None else period,
        )
    else:
        request_body = None if method == "GET" else validate_body(body or {}, allow_custom_body)
    result = api.get_result(
        path,
        method=method,
        body=request_body,
    )
    return {
        "code": api.normalize_product_code(code),
        "kind": kind,
        "result": result,
    }


def build_records_body(statement: str, period: str) -> dict[str, str]:
    if statement not in STATEMENT_CODES:
        raise ValueError(f"unknown financial statement: {statement}")
    if period not in PERIOD_CODES:
        raise ValueError(f"unknown financial period: {period}")
    return {"factorCode": STATEMENT_CODES[statement], "period": PERIOD_CODES[period]}


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
        description="Fetch TossInvest financial statement, estimate, valuation, or dividend data."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--kind",
        choices=sorted(FINANCIAL_PATHS),
        default="comprehensive",
        help="Financial endpoint to call",
    )
    parser.add_argument(
        "--statement",
        choices=sorted(STATEMENT_CODES),
        help="Statement for --kind records; defaults to income when --period is supplied",
    )
    parser.add_argument(
        "--period",
        choices=sorted(PERIOD_CODES),
        help="Period for --kind records; defaults to quarter when --statement is supplied",
    )
    parser.add_argument(
        "--years",
        type=int,
        help="Range code for --kind dividend-years; use selectableRanges from its default response",
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
    if args.body_file is not None and (args.statement is not None or args.period is not None):
        parser.error("--body-file cannot be combined with --statement or --period")

    payload = fetch_financials(
        args.code,
        args.kind,
        load_body(args.body_file, allow_custom=args.allow_custom_body)
        if args.body_file is not None
        else None,
        allow_custom_body=args.allow_custom_body,
        statement=args.statement,
        period=args.period,
        years=args.years,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
