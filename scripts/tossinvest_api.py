#!/usr/bin/env python3
"""Shared helpers for read-only TossInvest web API scripts."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import socket
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE_URL = "https://wts-info-api.tossinvest.com"
DEFAULT_TIMEOUT = 30
CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"

_ALLOWED_INFO_PREFIXES = ("/api/v1/", "/api/v2/", "/api/v3/", "/api/v4/")
_ALLOWED_CERT_EXACT_PATHS = (
    "/api/v1/dashboard/wts/overview/rankings/by-investors",
    "/api/v1/screener/screen/count",
    "/api/v2/dashboard/wts/overview/ranking",
    "/api/v2/screener/presets/common",
    "/api/v2/screener/screen",
    "/api/v3/dashboard/wts/overview/indicator/mini-chart",
)
_ALLOWED_CERT_SUBTREE_PREFIXES = ("/api/v1/dashboard/wts/overview/indicator",)
_DENIED_PATH_MARKERS = (
    "/account",
    "/accounts",
    "/authentication",
    "/balance",
    "/holding",
    "/holdings",
    "/login",
    "/order/",
    "/orderable",
    "/orders",
    "/trading/order",
    "/transfer",
)


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
    validate_request_target(base_url, path)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        base_url + path,
        data=data,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.tossinvest.com",
            "Referer": "https://www.tossinvest.com/",
            "User-Agent": "Mozilla/5.0 tossinvest-api-skills-skill/1.0",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8")
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"TossInvest API returned non-JSON content for {method} {path}; reverify the endpoint"
                ) from exc
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"TossInvest API returned HTTP {exc.code} for {method} {path}: {detail}"
        ) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        raise RuntimeError(
            f"TossInvest API request failed for {method} {path}: {exc}; reverify the endpoint"
        ) from exc


def result_or_raise(payload: dict[str, Any]) -> Any:
    if "result" not in payload:
        raise RuntimeError("Unexpected TossInvest response: missing top-level result")
    return payload["result"]


def get_result(path: str, **kwargs: Any) -> Any:
    return result_or_raise(request_json(path, **kwargs))


def validate_request_target(base_url: str, path: str) -> None:
    parsed_base = urllib.parse.urlsplit(base_url)
    host = parsed_base.netloc.lower()
    parsed_path = urllib.parse.urlsplit(path)
    if parsed_path.scheme or parsed_path.netloc:
        raise RuntimeError("Blocked TossInvest endpoint: path must be relative")
    request_path = _validation_path(parsed_path.path)
    lowered_path = request_path.lower()

    for marker in _DENIED_PATH_MARKERS:
        if marker in lowered_path:
            raise RuntimeError(f"Blocked TossInvest endpoint: denied path marker {marker}")

    if host == urllib.parse.urlsplit(BASE_URL).netloc:
        if request_path.startswith(_ALLOWED_INFO_PREFIXES):
            return
        raise RuntimeError(
            f"Blocked TossInvest endpoint: {request_path} is not in the approved info-api prefixes"
        )

    if host == urllib.parse.urlsplit(CERT_BASE_URL).netloc:
        if request_path in _ALLOWED_CERT_EXACT_PATHS or _matches_subtree_prefix(
            request_path, _ALLOWED_CERT_SUBTREE_PREFIXES
        ):
            return
        raise RuntimeError(
            f"Blocked TossInvest endpoint: {request_path} is not an approved cert-api endpoint"
        )

    raise RuntimeError(f"Blocked TossInvest endpoint: unapproved host {host}")


def _validation_path(path: str) -> str:
    if not path.startswith("/"):
        raise RuntimeError("Blocked TossInvest endpoint: path must start with /")
    lowered_raw = path.lower()
    if "\\" in path or "%2f" in lowered_raw or "%5c" in lowered_raw:
        raise RuntimeError("Blocked TossInvest endpoint: encoded path separators are not allowed")

    decoded_path = urllib.parse.unquote(path)
    if "\\" in decoded_path:
        raise RuntimeError("Blocked TossInvest endpoint: backslash path separators are not allowed")
    if any(segment in {".", ".."} for segment in decoded_path.split("/")):
        raise RuntimeError("Blocked TossInvest endpoint: dot segments are not allowed")
    return decoded_path


def _matches_subtree_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == prefix or path.startswith(f"{prefix}/") for prefix in prefixes)


def require_int_range(name: str, value: int, *, minimum: int, maximum: int) -> int:
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    if value > maximum:
        raise ValueError(f"{name} must be at most {maximum}")
    return value


def run_cli(main_func: Any) -> int:
    try:
        return int(main_func())
    except (
        RuntimeError,
        ValueError,
        OSError,
        json.JSONDecodeError,
        urllib.error.URLError,
        socket.timeout,
        TimeoutError,
    ) as exc:
        if os.environ.get("TOSSINVEST_DEBUG"):
            traceback.print_exc()
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1


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
