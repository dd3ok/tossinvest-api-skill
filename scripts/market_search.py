#!/usr/bin/env python3
"""Search public TossInvest products, news, industries, screens, and market indices."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

SEARCH_SECTIONS = {
    "screener": {"type": "SCREENER"},
    "news": {"type": "NEWS"},
    "product": {"type": "PRODUCT", "option": {"addIntegratedSearchResult": True}},
    "tics": {"type": "TICS"},
    "market-index": {"type": "MARKET_INDEX"},
}
SAFE_ITEM_FIELDS = {
    "PRODUCT": (
        "productCode",
        "productName",
        "symbol",
        "market",
        "companyCode",
        "close",
        "base",
        "subKeyword",
    ),
    "NEWS": ("id", "title", "summary", "source", "createdAt", "updatedAt"),
    "TICS": ("id", "ticsId", "name", "summary", "nation"),
    "SCREENER": ("id", "name", "description", "nation"),
    "MARKET_INDEX": ("code", "name", "productCode", "symbol", "market"),
}


def build_search_body(query: str, sections: list[str] | None) -> dict[str, Any]:
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be blank")
    if len(normalized_query) > 100:
        raise ValueError("query must be at most 100 characters")
    section_names = sections or list(SEARCH_SECTIONS)
    normalized_sections: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section in section_names:
        key = section.strip().lower()
        if key not in SEARCH_SECTIONS:
            raise ValueError(f"section must be one of: {', '.join(sorted(SEARCH_SECTIONS))}")
        if key not in seen:
            normalized_sections.append(SEARCH_SECTIONS[key])
            seen.add(key)
    return {"query": normalized_query, "sections": normalized_sections}


def sanitize_search_results(result: Any, limit: int) -> list[dict[str, Any]]:
    limit = api.require_int_range("limit", limit, minimum=1, maximum=20)
    if not isinstance(result, list):
        raise RuntimeError("Unexpected TossInvest response: search result is not a list")
    sections: list[dict[str, Any]] = []
    for section in result:
        if not isinstance(section, dict):
            continue
        data = section.get("data") if isinstance(section.get("data"), dict) else {}
        section_type = str(data.get("type") or section.get("type") or "").upper()
        safe_fields = SAFE_ITEM_FIELDS.get(section_type)
        items = data.get("items")
        if safe_fields is None or not isinstance(items, list):
            continue
        sanitized_items = [
            {key: item[key] for key in safe_fields if item.get(key) is not None}
            for item in items[:limit]
            if isinstance(item, dict)
        ]
        sections.append({"type": section_type, "items": sanitized_items})
    return sections


def fetch_market_search(query: str, sections: list[str] | None, limit: int) -> dict[str, Any]:
    body = build_search_body(query, sections)
    result = api.get_result(
        "/api/v3/search-all/wts-auto-complete",
        method="POST",
        body=body,
    )
    return {
        "query": body["query"],
        "sections": sanitize_search_results(result, limit),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Search public TossInvest market information.")
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--section",
        action="append",
        choices=sorted(SEARCH_SECTIONS),
        help="Limit results to a section; repeat to combine sections",
    )
    parser.add_argument("--limit", type=int, default=10, help="Maximum rows per section (1-20)")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_market_search(args.query, args.section, args.limit)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
