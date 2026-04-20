#!/usr/bin/env python3
"""Fetch read-only TossInvest screener result counts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import tossinvest_api as api


CERT_URL = "https://wts-cert-api.tossinvest.com"
RSI_FILTER_ID = "RSI_범위"
NUMBER_RANGE_CONDITION_ID = "NUMBER_RANGE_DEFAULT"


def normalize_nation(nation: str) -> str:
    normalized = nation.strip().lower()
    if normalized not in {"kr", "us"}:
        raise ValueError("nation must be 'kr' or 'us'")
    return normalized


def build_count_body(nation: str, filters: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"filters": filters or [], "nation": normalize_nation(nation)}


def build_rsi_filter(mode: str) -> dict[str, Any]:
    normalized = mode.strip().lower()
    if normalized == "oversold":
        value = {"from": None, "to": 30, "includeFrom": None, "includeTo": True}
    elif normalized == "overbought":
        value = {"from": 70, "to": None, "includeFrom": True, "includeTo": None}
    else:
        raise ValueError("rsi mode must be 'oversold' or 'overbought'")
    return {
        "id": RSI_FILTER_ID,
        "conditions": [
            {
                "id": NUMBER_RANGE_CONDITION_ID,
                "type": "NUMBER_RANGE",
                "value": value,
            }
        ],
    }


def build_screen_body(
    nation: str,
    filters: list[dict[str, Any]] | None = None,
    size: int = 20,
) -> dict[str, Any]:
    if size < 1:
        raise ValueError("size must be greater than 0")
    return {
        "filters": filters or [],
        "nation": normalize_nation(nation),
        "pagingParam": {"size": size},
    }


def fetch_screener_count(
    nation: str, filters: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    body = build_count_body(nation, filters)
    result = api.get_result(
        "/api/v1/screener/screen/count",
        method="POST",
        body=body,
        base_url=CERT_URL,
    )
    return {
        "nation": body["nation"],
        "filters": body["filters"],
        "count": result,
    }


def fetch_screener_results(
    nation: str,
    filters: list[dict[str, Any]] | None = None,
    size: int = 20,
) -> dict[str, Any]:
    body = build_screen_body(nation, filters, size)
    return api.get_result(
        "/api/v2/screener/screen",
        method="POST",
        body=body,
        base_url=CERT_URL,
    )


def load_filters(path: str | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("filters file must contain a JSON list")
    if not all(isinstance(item, dict) for item in payload):
        raise ValueError("filters file must contain a list of JSON objects")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest screener count for kr/us and optional filters."
    )
    parser.add_argument("--nation", default="kr", help="kr or us")
    parser.add_argument(
        "--filters-file",
        help="Optional JSON file containing the screener filters list",
    )
    parser.add_argument(
        "--rsi",
        choices=["oversold", "overbought"],
        help="Add a built-in RSI filter: oversold is RSI <= 30, overbought is RSI >= 70",
    )
    parser.add_argument(
        "--include-results",
        action="store_true",
        help="Also fetch the first page from /api/v2/screener/screen",
    )
    parser.add_argument("--size", type=int, default=20, help="Result page size when used")
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    filters = load_filters(args.filters_file)
    if args.rsi:
        filters.append(build_rsi_filter(args.rsi))
    payload = fetch_screener_count(args.nation, filters)
    if args.include_results:
        payload["results"] = fetch_screener_results(args.nation, filters, args.size)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
