#!/usr/bin/env python3
"""Shared helpers for read-only TossInvest web API scripts."""

from __future__ import annotations

import csv
import io
import json
import argparse
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://wts-info-api.tossinvest.com"
DEFAULT_TIMEOUT = 30


def normalize_product_code(code: str) -> str:
    value = code.strip().upper()
    if value.isdigit() and len(value) == 6:
        return f"A{value}"
    return value


def to_company_code(code: str) -> str:
    value = code.strip().upper()
    if len(value) == 7 and value.startswith("A") and value[1:].isdigit():
        return value[1:]
    return value


def build_path(path: str, params: dict[str, Any] | None = None) -> str:
    if not params:
        return path
    query = urllib.parse.urlencode(
        {key: _query_value(value) for key, value in params.items() if value is not None}
    )
    if not query:
        return path
    return f"{path}?{query}"


def request_json(
    path: str,
    *,
    method: str = "GET",
    body: Any | None = None,
    base_url: str = BASE_URL,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        base_url + path,
        data=data,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.tossinvest.com",
            "Referer": "https://www.tossinvest.com/",
            "User-Agent": "Mozilla/5.0 tossinvest-web-api-skill/1.0",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"TossInvest API returned HTTP {exc.code}: {detail}") from exc


def result_or_raise(payload: dict[str, Any]) -> Any:
    if "result" not in payload:
        raise RuntimeError("Unexpected TossInvest response: missing top-level result")
    return payload["result"]


def get_result(path: str, **kwargs: Any) -> Any:
    return result_or_raise(request_json(path, **kwargs))


def find_by_code(rows: list[dict[str, Any]], code: str) -> dict[str, Any] | None:
    product_code = normalize_product_code(code)
    for row in rows:
        if row.get("code") == product_code or row.get("productCode") == product_code:
            return row
    return None


def render_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def add_json_format_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=["json"],
        default="json",
        help="Output format; only json is supported",
    )


def render_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def emit_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    else:
        print(text, end="" if text.endswith("\n") else "\n")


def _query_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
