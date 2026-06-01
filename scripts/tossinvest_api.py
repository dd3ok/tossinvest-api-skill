#!/usr/bin/env python3
"""Shared helpers for read-only TossInvest web API scripts."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import socket
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

BASE_URL = "https://wts-info-api.tossinvest.com"
DEFAULT_TIMEOUT = 30
CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"

_ALLOWED_INFO_PREFIXES = ("/api/v1/", "/api/v2/", "/api/v3/", "/api/v4/")
_CALENDAR_CERT_EXACT_PATHS = (
    "/api/v1/calendar/ai-summary/key-events",
    "/api/v1/nova-calendar/ai/analysis/indicators",
    "/api/v1/nova-calendar/ai/summary/weekly",
    "/api/v2/dashboard/wts/overview/calendar/economic-events",
)
_CALENDAR_MONTHLY_PATTERN = re.compile(r"^/api/v4/calendar/monthly/\d{4}-(0[1-9]|1[0-2])$")
_CALENDAR_INDEX_MONTHLY_PATTERN = re.compile(
    r"^/api/v4/calendar/monthly/\d{4}-(0[1-9]|1[0-2])/index$"
)
_CALENDAR_ECONOMIC_INDICATOR_PATTERN = re.compile(
    r"^/api/v1/calendar/economic-indicators/[A-Z0-9_.=-]{2,48}$"
)
_DATE_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
_DATE_TIME_PATTERN = re.compile(
    r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):[0-5]\d:[0-5]\d$"
)
_RIC_PATTERN = re.compile(r"^[A-Z0-9_.=-]{2,48}$")
_ALLOWED_CERT_EXACT_PATHS = (
    *_CALENDAR_CERT_EXACT_PATHS,
    "/api/v1/dashboard/wts/overview/rankings/by-investors",
    "/api/v1/dashboard/wts/overview/indicator/bond",
    "/api/v1/dashboard/wts/overview/indicator/commodity",
    "/api/v1/dashboard/wts/overview/indicator/index",
    "/api/v1/screener/screen/count",
    "/api/v2/dashboard/wts/overview/ranking",
    "/api/v2/screener/presets/common",
    "/api/v2/screener/screen",
    "/api/v2/screener/screen/search/modal",
    "/api/v3/dashboard/wts/overview/indicator/mini-chart",
)
_ALLOWED_CERT_PATH_PATTERNS = (
    _CALENDAR_MONTHLY_PATTERN,
    _CALENDAR_INDEX_MONTHLY_PATTERN,
    _CALENDAR_ECONOMIC_INDICATOR_PATTERN,
)
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
_DENIED_KEY_MARKERS = (
    "account",
    "authorization",
    "auth",
    "balance",
    "cookie",
    "customer",
    "holding",
    "holdings",
    "orderable",
    "personal",
    "token",
    "transfer",
)
_DENIED_EXACT_KEYS = {"ci"}


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
    validate_no_sensitive_keys(params)
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
    if body is not None:
        validate_no_sensitive_keys(body)
    validate_request_usage(base_url, path, method, body)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        base_url + path,
        data=data,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.tossinvest.com",
            "Referer": "https://www.tossinvest.com/",
            "User-Agent": "Mozilla/5.0 tossinvest-api-skill/1.0",
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
        raise RuntimeError(_http_error_message(exc, method, path)) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        raise RuntimeError(
            f"TossInvest API request failed for {method} {path}: {exc}; reverify the endpoint"
        ) from exc


def result_or_raise(payload: dict[str, Any]) -> Any:
    if "result" not in payload:
        raise RuntimeError("Unexpected TossInvest response: missing top-level result")
    return payload["result"]


def _http_error_message(exc: urllib.error.HTTPError, method: str, path: str) -> str:
    detail = "" if exc.fp is None else exc.read().decode("utf-8", errors="replace")
    message = f"TossInvest API returned HTTP {exc.code} for {method} {path}: {detail}"
    if exc.code in {403, 429}:
        message += (
            " stop automated retries; do not bypass rate limit or anti-bot checks; "
            "reverify the endpoint from current public browser traffic before trying again"
        )
    return message


def get_result(path: str, **kwargs: Any) -> Any:
    return result_or_raise(request_json(path, **kwargs))


def validate_request_target(base_url: str, path: str) -> None:
    parsed_base = urllib.parse.urlsplit(base_url)
    host = parsed_base.netloc.lower()
    parsed_path = urllib.parse.urlsplit(path)
    if parsed_path.scheme or parsed_path.netloc:
        raise RuntimeError("Blocked TossInvest endpoint: path must be relative")
    request_path = _validation_path(parsed_path.path)
    query_pairs = urllib.parse.parse_qsl(parsed_path.query, keep_blank_values=True)
    if parsed_path.query:
        validate_no_sensitive_keys({key: value for key, value in query_pairs})
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
        if _is_calendar_cert_path(request_path):
            _validate_calendar_cert_query(request_path, query_pairs)
            return
        if request_path in _ALLOWED_CERT_EXACT_PATHS or any(
            pattern.fullmatch(request_path) for pattern in _ALLOWED_CERT_PATH_PATTERNS
        ):
            return
        raise RuntimeError(
            f"Blocked TossInvest endpoint: {request_path} is not an approved cert-api endpoint"
        )

    raise RuntimeError(f"Blocked TossInvest endpoint: unapproved host {host}")


def validate_request_usage(
    base_url: str,
    path: str,
    method: str,
    body: Any | None,
) -> None:
    parsed_base = urllib.parse.urlsplit(base_url)
    if parsed_base.netloc.lower() != urllib.parse.urlsplit(CERT_BASE_URL).netloc:
        return
    request_path = _validation_path(urllib.parse.urlsplit(path).path)
    if not _is_calendar_cert_path(request_path):
        return
    method = method.upper()
    if _CALENDAR_MONTHLY_PATTERN.fullmatch(
        request_path
    ) or _CALENDAR_INDEX_MONTHLY_PATTERN.fullmatch(request_path):
        if method != "POST":
            raise RuntimeError("Blocked TossInvest endpoint: monthly calendar route must use POST")
        if body != {}:
            raise RuntimeError(
                "Blocked TossInvest endpoint: monthly calendar route requires an empty JSON body"
            )
    elif method != "GET":
        raise RuntimeError("Blocked TossInvest endpoint: calendar summary routes must use GET")
    elif body is not None:
        raise RuntimeError(
            "Blocked TossInvest endpoint: calendar summary routes do not accept request bodies"
        )
    if body is not None and body != {}:
        raise RuntimeError(
            "Blocked TossInvest endpoint: calendar routes do not accept request body fields"
        )


def _is_calendar_cert_path(request_path: str) -> bool:
    return request_path in _CALENDAR_CERT_EXACT_PATHS or bool(
        _CALENDAR_MONTHLY_PATTERN.fullmatch(request_path)
        or _CALENDAR_INDEX_MONTHLY_PATTERN.fullmatch(request_path)
        or _CALENDAR_ECONOMIC_INDICATOR_PATTERN.fullmatch(request_path)
    )


def _validate_calendar_cert_query(request_path: str, pairs: list[tuple[str, str]]) -> None:
    if _CALENDAR_INDEX_MONTHLY_PATTERN.fullmatch(request_path):
        params = _single_query_params(pairs)
        if set(params) != {"countryType"}:
            raise RuntimeError(
                "Blocked TossInvest endpoint: unexpected query parameters for index calendar route"
            )
        if params["countryType"] not in {"kr", "us"}:
            raise RuntimeError("Blocked TossInvest endpoint: countryType must be kr or us")
        return

    if _CALENDAR_ECONOMIC_INDICATOR_PATTERN.fullmatch(request_path):
        params = _single_query_params(pairs)
        if set(params) != {"announceDate"}:
            raise RuntimeError(
                "Blocked TossInvest endpoint: unexpected query parameters for calendar economic indicator route"
            )
        if not _DATE_PATTERN.fullmatch(params["announceDate"]):
            raise RuntimeError("Blocked TossInvest endpoint: announceDate must be YYYY-MM-DD")
        if not _is_valid_date(params["announceDate"]):
            raise RuntimeError(
                "Blocked TossInvest endpoint: announceDate must be a valid calendar date"
            )
        return

    if request_path == "/api/v1/nova-calendar/ai/analysis/indicators":
        params = _single_query_params(pairs)
        if set(params) != {"announceDateTime", "ricId"}:
            raise RuntimeError(
                "Blocked TossInvest endpoint: unexpected query parameters for calendar AI analysis route"
            )
        if not _DATE_TIME_PATTERN.fullmatch(params["announceDateTime"]):
            raise RuntimeError(
                "Blocked TossInvest endpoint: announceDateTime must be YYYY-MM-DDTHH:MM:SS"
            )
        if not _is_valid_datetime(params["announceDateTime"]):
            raise RuntimeError(
                "Blocked TossInvest endpoint: announceDateTime must be a valid calendar datetime"
            )
        if not _RIC_PATTERN.fullmatch(params["ricId"]):
            raise RuntimeError("Blocked TossInvest endpoint: ricId is not an approved RIC shape")
        return

    if pairs:
        raise RuntimeError(
            "Blocked TossInvest endpoint: calendar routes do not accept query parameters"
        )


def _single_query_params(pairs: list[tuple[str, str]]) -> dict[str, str]:
    params: dict[str, str] = {}
    for key, value in pairs:
        if key in params:
            raise RuntimeError(f"Blocked TossInvest endpoint: duplicate query parameter {key}")
        params[key] = value
    return params


def _is_valid_date(value: str) -> bool:
    year, month, day = (int(part) for part in value.split("-"))
    try:
        date(year, month, day)
    except ValueError:
        return False
    return True


def _is_valid_datetime(value: str) -> bool:
    return _is_valid_date(value.split("T", 1)[0])


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


def validate_no_sensitive_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _raise_if_sensitive_key(str(key))
            validate_no_sensitive_keys(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            validate_no_sensitive_keys(child)


def _raise_if_sensitive_key(key: str) -> None:
    normalized = _normalize_payload_key(key)
    if normalized in _DENIED_EXACT_KEYS or any(
        marker in normalized for marker in _DENIED_KEY_MARKERS
    ):
        raise RuntimeError(f"Blocked TossInvest request: sensitive key {key}")


def _normalize_payload_key(key: str) -> str:
    return "".join(char for char in key.lower() if char.isalnum())


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
