#!/usr/bin/env python3
"""Fetch read-only TossInvest market-calendar page data."""

from __future__ import annotations

import argparse
import re
from datetime import date
from typing import Any

import tossinvest_api as api

CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"

_YEAR_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
MONTHLY_KINDS = {"monthly", "economic", "earnings", "domestic", "overseas"}
SPECIAL_KINDS = {"key-events", "weekly-summary", "overview-economic"}
KINDS = MONTHLY_KINDS | SPECIAL_KINDS
CATEGORIES = {"all", "economic", "earnings"}
COUNTRIES = {"all", "kr", "us"}
EARNINGS_GROUPS = {"KRX_EARNINGS_ANNOUNCEMENT", "USD_EARNINGS_ANNOUNCEMENT"}


def build_monthly_path(year_month: str) -> str:
    year_month = validate_year_month(year_month)
    return f"/api/v4/calendar/monthly/{year_month}"


def build_key_events_path() -> str:
    return "/api/v1/calendar/ai-summary/key-events"


def build_weekly_summary_path() -> str:
    return "/api/v1/nova-calendar/ai/summary/weekly"


def build_overview_economic_events_path() -> str:
    return "/api/v2/dashboard/wts/overview/calendar/economic-events"


def validate_year_month(year_month: str) -> str:
    value = year_month.strip()
    if not _YEAR_MONTH_RE.fullmatch(value):
        raise ValueError("year-month must be YYYY-MM with month 01-12")
    return value


def filter_monthly_events(
    events: list[dict[str, Any]],
    category: str,
    country: str,
) -> list[dict[str, Any]]:
    category = _require_choice("category", category, CATEGORIES)
    country = _require_choice("country", country, COUNTRIES)
    filtered = []
    for event in events:
        if not isinstance(event, dict):
            raise RuntimeError(
                "Unexpected TossInvest response: monthly calendar event is not a dictionary"
            )
        if _matches_category(event, category) and _matches_country(event, country):
            filtered.append(event)
    return filtered


def apply_event_window(
    payload: dict[str, Any],
    *,
    limit: int | None,
    offset: int,
    summary_only: bool,
) -> dict[str, Any]:
    offset = api.require_int_range("offset", offset, minimum=0, maximum=10_000)
    if limit is not None:
        limit = api.require_int_range("limit", limit, minimum=1, maximum=10_000)
    if "events" not in payload:
        return payload
    events = payload["events"]
    if not isinstance(events, list):
        raise RuntimeError("Unexpected TossInvest response: calendar events is not a list")
    windowed = dict(payload)
    windowed["filteredEvents"] = len(events)
    windowed["offset"] = offset
    windowed["limit"] = limit
    if summary_only:
        windowed.pop("events", None)
        return windowed
    windowed["events"] = events[offset : None if limit is None else offset + limit]
    return windowed


def fetch_calendar(
    year_month: str,
    kind: str,
    category: str,
    country: str,
) -> dict[str, Any]:
    kind = _require_choice("kind", kind, KINDS)
    if kind == "key-events":
        return {
            "kind": kind,
            "result": api.get_result(build_key_events_path(), base_url=CERT_BASE_URL),
        }
    if kind == "weekly-summary":
        return {
            "kind": kind,
            "result": api.get_result(build_weekly_summary_path(), base_url=CERT_BASE_URL),
        }
    if kind == "overview-economic":
        return {
            "kind": kind,
            "result": api.get_result(
                build_overview_economic_events_path(),
                base_url=CERT_BASE_URL,
            ),
        }

    resolved_category, resolved_country = resolve_monthly_filters(kind, category, country)
    result = api.get_result(
        build_monthly_path(year_month),
        method="POST",
        body={},
        base_url=CERT_BASE_URL,
    )
    if not isinstance(result, dict):
        raise RuntimeError(
            "Unexpected TossInvest response: monthly calendar result is not a dictionary"
        )
    events = result.get("events", [])
    if not isinstance(events, list):
        raise RuntimeError("Unexpected TossInvest response: monthly calendar events is not a list")
    return {
        "kind": kind,
        "yearMonth": validate_year_month(year_month),
        "category": resolved_category,
        "country": resolved_country,
        "totalEvents": len(events),
        "events": filter_monthly_events(events, resolved_category, resolved_country),
    }


def resolve_monthly_filters(kind: str, category: str, country: str) -> tuple[str, str]:
    kind = _require_choice("kind", kind, MONTHLY_KINDS)
    category = _require_choice("category", category, CATEGORIES)
    country = _require_choice("country", country, COUNTRIES)
    if kind == "economic":
        category = "economic"
    elif kind == "earnings":
        category = "earnings"
    elif kind == "domestic":
        country = "kr"
    elif kind == "overseas":
        country = "us"
    return category, country


def _matches_category(event: dict[str, Any], category: str) -> bool:
    group = _event_group(event)
    if category == "all":
        return not bool(event.get("excludeFromAll"))
    if category == "economic":
        return group == "ECONOMIC"
    return group in EARNINGS_GROUPS


def _matches_country(event: dict[str, Any], country: str) -> bool:
    if country == "all":
        return True
    return _event_country(event) == country


def _event_group(event: dict[str, Any]) -> str:
    event_id = event.get("id")
    if isinstance(event_id, dict):
        return str(event_id.get("group") or "")
    return ""


def _event_country(event: dict[str, Any]) -> str | None:
    view = event.get("view")
    if isinstance(view, dict):
        economic = view.get("economicIndicatorValue")
        if isinstance(economic, dict) and economic.get("countryType"):
            return str(economic["countryType"]).lower()
    earnings = event.get("stockEarnings")
    if isinstance(earnings, dict) and earnings.get("countryType"):
        return str(earnings["countryType"]).lower()
    event_id = event.get("id")
    unique_name = ""
    if isinstance(event_id, dict):
        unique_name = str(event_id.get("uniqueName") or "").upper()
    if unique_name.endswith("_KR"):
        return "kr"
    if unique_name.endswith("_US"):
        return "us"
    return None


def _require_choice(name: str, value: str, choices: set[str]) -> str:
    normalized = value.strip().lower()
    if normalized not in choices:
        expected = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {expected}")
    return normalized


def default_year_month() -> str:
    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch public read-only TossInvest /calendar monthly events, "
            "economic indicators, earnings dates, and AI summary widgets."
        )
    )
    parser.add_argument(
        "--year-month",
        default=default_year_month(),
        help="Calendar month in YYYY-MM format for monthly event kinds",
    )
    parser.add_argument(
        "--kind",
        choices=sorted(KINDS),
        default="monthly",
        help=(
            "monthly data alias or summary endpoint: economic, earnings, domestic, "
            "overseas, key-events, weekly-summary, overview-economic"
        ),
    )
    parser.add_argument(
        "--category",
        choices=sorted(CATEGORIES),
        default="all",
        help="Monthly event category filter; economic and earnings kinds override this",
    )
    parser.add_argument(
        "--country",
        choices=sorted(COUNTRIES),
        default="all",
        help="Monthly country filter; domestic/overseas kinds override this",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum monthly events to print after filtering",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Monthly event offset after filtering",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="For monthly event kinds, print counts and filters without the events array",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_calendar(args.year_month, args.kind, args.category, args.country)
    payload = apply_event_window(
        payload,
        limit=args.limit,
        offset=args.offset,
        summary_only=args.summary_only,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
