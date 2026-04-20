#!/usr/bin/env python3
"""Fetch read-only TossInvest screener result counts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import tossinvest_api as api


CERT_URL = "https://wts-cert-api.tossinvest.com"


def build_count_body(nation: str, filters: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    normalized = nation.strip().lower()
    if normalized not in {"kr", "us"}:
        raise ValueError("nation must be 'kr' or 'us'")
    return {"filters": filters or [], "nation": normalized}


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
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_screener_count(args.nation, load_filters(args.filters_file))
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
