#!/usr/bin/env python3
"""Search public TossInvest products, news, industries, screens, and market indices."""

from __future__ import annotations

import argparse
import math
import re
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
        "keyword",
        "symbol",
        "market",
        "companyCode",
        "close",
        "base",
        "subKeyword",
    ),
    "NEWS": ("id", "title", "summary", "source", "createdAt", "updatedAt"),
    "TICS": ("id", "ticsId", "name", "title", "summary", "nation"),
    "SCREENER": ("id", "name", "description", "nation"),
    "MARKET_INDEX": ("code", "name", "productCode", "symbol", "market"),
}
RELATED_SECTIONS = {
    "related-topic": ("RELATED_TOPIC", "product_code", "productCode"),
    "company-tics": ("COMPANY_TICS", "company_code", "companyCode"),
    "tics-product": ("TICS_PRODUCT", "tics_id", "ticsId"),
    "index-description": ("MARKET_INDEX_DESCRIPTION", "index_code", "code"),
}
_PUBLIC_CODE_RE = re.compile(r"^[A-Za-z0-9._-]{2,48}$")
_TICS_ID_RE = re.compile(r"^[0-9]{1,30}$")


def normalize_query(query: str) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be blank")
    if len(normalized_query) > 100:
        raise ValueError("query must be at most 100 characters")
    return normalized_query


def build_search_body(query: str, sections: list[str] | None) -> dict[str, Any]:
    normalized_query = normalize_query(query)
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


def build_related_search_body(
    query: str,
    related_kind: str,
    *,
    product_code: str | None = None,
    company_code: str | None = None,
    tics_id: str | None = None,
    index_code: str | None = None,
) -> dict[str, Any]:
    if related_kind not in RELATED_SECTIONS:
        raise ValueError(f"related-kind must be one of: {', '.join(RELATED_SECTIONS)}")
    section_type, required_target, option_name = RELATED_SECTIONS[related_kind]
    targets = {
        "product_code": product_code,
        "company_code": company_code,
        "tics_id": tics_id,
        "index_code": index_code,
    }
    supplied = {name: value for name, value in targets.items() if value is not None}
    if set(supplied) != {required_target}:
        raise ValueError(f"{related_kind} requires only --{required_target.replace('_', '-')}")
    value = supplied[required_target]
    if not isinstance(value, str):
        raise ValueError(f"{required_target} must be a public identifier string")
    normalized_value: str | int = value.strip()
    if required_target == "tics_id":
        if not _TICS_ID_RE.fullmatch(normalized_value):
            raise ValueError("tics-id must contain 1-30 ASCII digits")
        normalized_value = int(normalized_value)
    else:
        if not _PUBLIC_CODE_RE.fullmatch(normalized_value):
            raise ValueError(f"{required_target} must be a 2-48 character public code")
        if required_target == "product_code":
            normalized_value = api.normalize_product_code(normalized_value)
    return {
        "query": normalize_query(query),
        "sections": [{"type": section_type, "option": {option_name: normalized_value}}],
    }


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
        sanitized_items = []
        for item in items[:limit]:
            if not isinstance(item, dict):
                continue
            sanitized = {key: item[key] for key in safe_fields if item.get(key) is not None}
            subquery = item.get("subSectionQuery")
            if (
                isinstance(subquery, str)
                and subquery.strip()
                and len(subquery) <= 100
                and not any(ord(character) < 32 or ord(character) == 127 for character in subquery)
            ):
                sanitized["subSectionQuery"] = subquery
            sanitized_items.append(sanitized)
        sections.append({"type": section_type, "items": sanitized_items})
    return sections


def sanitize_related_results(result: Any, section_type: str, limit: int) -> list[dict[str, Any]]:
    limit = api.require_int_range("limit", limit, minimum=1, maximum=20)
    if not isinstance(result, list):
        raise RuntimeError("Unexpected TossInvest response: related search result is not a list")
    sections = []
    for section in result:
        if not isinstance(section, dict) or section.get("type") != section_type:
            continue
        data = section.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            raise RuntimeError("Unexpected TossInvest response: related search items are missing")
        fields = (
            ("code", "description")
            if section_type == "MARKET_INDEX_DESCRIPTION"
            else ("productCode", "productName", "companyName", "code")
        )
        items = []
        for row in data["items"][:limit]:
            if not isinstance(row, dict):
                continue
            sanitized: dict[str, Any] = {
                field: row[field] for field in fields if isinstance(row.get(field), str)
            }
            if section_type != "MARKET_INDEX_DESCRIPTION":
                for field in ("base", "close"):
                    prices = row.get(field)
                    if isinstance(prices, dict):
                        sanitized[field] = {
                            currency: value
                            for currency in ("krw", "usd")
                            if currency in prices
                            and (
                                (value := prices[currency]) is None
                                or (
                                    isinstance(value, (int, float))
                                    and not isinstance(value, bool)
                                    and math.isfinite(value)
                                )
                            )
                        }
            items.append(sanitized)
        sanitized_section = {
            "type": section_type,
            "receivedItems": len(data["items"]),
            "emittedItems": len(items),
            "truncated": len(data["items"]) > limit,
            "items": items,
        }
        if isinstance(data.get("id"), (str, int)) and not isinstance(data["id"], bool):
            sanitized_section["id"] = data["id"]
        if isinstance(data.get("title"), str):
            sanitized_section["title"] = data["title"]
        sections.append(sanitized_section)
    return sections


def fetch_related_search(
    query: str, related_kind: str, limit: int, **targets: str | None
) -> dict[str, Any]:
    limit = api.require_int_range("limit", limit, minimum=1, maximum=20)
    body = build_related_search_body(query, related_kind, **targets)
    section = body["sections"][0]
    result = api.get_result("/api/v3/search-all/wts-auto-complete", method="POST", body=body)
    return {
        "query": body["query"],
        "relatedKind": related_kind,
        "target": section["option"],
        "sections": sanitize_related_results(result, section["type"], limit),
    }


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
    parser.add_argument(
        "--query",
        required=True,
        help="Search text; for related lookup, use the selected result's subSectionQuery or name",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--section",
        action="append",
        choices=sorted(SEARCH_SECTIONS),
        help="Limit results to a section; repeat to combine sections",
    )
    mode.add_argument("--related-kind", choices=sorted(RELATED_SECTIONS))
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--product-code", help="RELATED_TOPIC target from a selected product")
    target.add_argument("--company-code", help="COMPANY_TICS target from a selected product")
    target.add_argument("--tics-id", help="TICS_PRODUCT target from a selected industry")
    target.add_argument("--index-code", help="Index-description target from a selected index")
    parser.add_argument("--limit", type=int, default=10, help="Maximum rows per section (1-20)")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    targets = {
        "product_code": args.product_code,
        "company_code": args.company_code,
        "tics_id": args.tics_id,
        "index_code": args.index_code,
    }
    if args.related_kind is not None:
        payload = fetch_related_search(args.query, args.related_kind, args.limit, **targets)
    else:
        if any(value is not None for value in targets.values()):
            parser.error("target options require --related-kind")
        payload = fetch_market_search(args.query, args.section, args.limit)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
