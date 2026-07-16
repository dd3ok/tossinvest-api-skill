#!/usr/bin/env python3
"""Fetch read-only TossInvest screener counts and optional result pages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import tossinvest_api as api

CERT_URL = "https://wts-cert-api.tossinvest.com"
RSI_FILTER_ID = "RSI_범위"
NUMBER_RANGE_CONDITION_ID = "NUMBER_RANGE_DEFAULT"
SORT_COLUMNS = {
    "price-change-1w": {"column": "C_주가등락률_1W", "label": "주가등락률"},
    "market-cap": {"column": "C_시가총액", "label": "시가총액"},
    "volume": {"column": "C_거래량", "label": "거래량"},
    "analyst-rating": {"column": "C_애널리스트평점", "label": "애널리스트 분석"},
}
PRICE_PRESETS = {
    "price-change-5d-up-5": {
        "filter_id": "주가등락률",
        "conditions": [
            {"id": "기간_선택_DAY_TO_MONTH", "type": "PERIOD", "value": "DAY_5"},
            {
                "id": NUMBER_RANGE_CONDITION_ID,
                "type": "NUMBER_RANGE",
                "value": {"from": 0.05, "to": None, "includeFrom": True, "includeTo": None},
            },
        ],
    },
    "price-change-20d-up-10": {
        "filter_id": "주가등락률",
        "conditions": [
            {"id": "기간_선택_DAY_TO_MONTH", "type": "PERIOD", "value": "DAY_20"},
            {
                "id": NUMBER_RANGE_CONDITION_ID,
                "type": "NUMBER_RANGE",
                "value": {"from": 0.10, "to": None, "includeFrom": True, "includeTo": None},
            },
        ],
    },
    "price-change-5d-down-5": {
        "filter_id": "주가등락률",
        "conditions": [
            {"id": "기간_선택_DAY_TO_MONTH", "type": "PERIOD", "value": "DAY_5"},
            {
                "id": NUMBER_RANGE_CONDITION_ID,
                "type": "NUMBER_RANGE",
                "value": {"from": None, "to": -0.05, "includeFrom": None, "includeTo": True},
            },
        ],
    },
    "consecutive-rise-5": {
        "filter_id": "주가_연속_상승",
        "conditions": [
            {
                "id": NUMBER_RANGE_CONDITION_ID,
                "type": "NUMBER_RANGE",
                "value": {"from": 5, "to": None, "includeFrom": True, "includeTo": None},
            }
        ],
    },
    "consecutive-fall-5": {
        "filter_id": "주가_연속_하락",
        "conditions": [
            {
                "id": NUMBER_RANGE_CONDITION_ID,
                "type": "NUMBER_RANGE",
                "value": {"from": 5, "to": None, "includeFrom": True, "includeTo": None},
            }
        ],
    },
    "new-high-52w-within-20d": {
        "filter_id": "CUSTOM_N주_신고가_달성_경과일",
        "conditions": [
            {
                "id": "WEEK_NEW_PRICE_HIT",
                "type": "WEEK_NEW_PRICE_HIT_WITHIN",
                "value": {"numberOfWeeks": 52, "within": 20},
            }
        ],
    },
    "new-low-52w-within-20d": {
        "filter_id": "CUSTOM_N주_신저가_달성_경과일",
        "conditions": [
            {
                "id": "WEEK_NEW_PRICE_HIT",
                "type": "WEEK_NEW_PRICE_HIT_WITHIN",
                "value": {"numberOfWeeks": 52, "within": 20},
            }
        ],
    },
}
TECHNICAL_PRESETS = {
    "price-ma-cross-up": {
        "filter_id": "CUSTOM_주가_이동평균선_돌파",
        "condition_id": "주가_이동평균선_돌파",
        "type": "PRICE_MOVING_AVERAGE_CROSS_ARRAY",
        "value": [{"period": 20, "within": 5, "crossDirection": "upward"}],
    },
    "price-ma-cross-down": {
        "filter_id": "CUSTOM_주가_이동평균선_돌파",
        "condition_id": "주가_이동평균선_돌파",
        "type": "PRICE_MOVING_AVERAGE_CROSS_ARRAY",
        "value": [{"period": 20, "within": 5, "crossDirection": "downward"}],
    },
    "ma-cross-up": {
        "filter_id": "CUSTOM_이동평균선_돌파",
        "condition_id": "이동평균선_돌파",
        "type": "MOVING_AVERAGE_CROSS_ARRAY",
        "value": [{"shortPeriod": 5, "longPeriod": 20, "within": 5, "crossDirection": "upward"}],
    },
    "ma-cross-down": {
        "filter_id": "CUSTOM_이동평균선_돌파",
        "condition_id": "이동평균선_돌파",
        "type": "MOVING_AVERAGE_CROSS_ARRAY",
        "value": [{"shortPeriod": 5, "longPeriod": 20, "within": 5, "crossDirection": "downward"}],
    },
    "volume-ma-cross-up": {
        "filter_id": "CUSTOM_거래량_이동평균선_돌파",
        "condition_id": "이동평균선_돌파",
        "type": "MOVING_AVERAGE_CROSS_ARRAY",
        "value": [{"shortPeriod": 5, "longPeriod": 20, "within": 5, "crossDirection": "upward"}],
    },
    "volume-ma-cross-down": {
        "filter_id": "CUSTOM_거래량_이동평균선_돌파",
        "condition_id": "이동평균선_돌파",
        "type": "MOVING_AVERAGE_CROSS_ARRAY",
        "value": [{"shortPeriod": 5, "longPeriod": 20, "within": 5, "crossDirection": "downward"}],
    },
    "ma-align-positive": {
        "filter_id": "CUSTOM_이동평균선_배열",
        "condition_id": "이동평균선_배열",
        "type": "MOVING_AVERAGE_ALIGN_ARRAY",
        "value": [
            {
                "shortPeriod": 5,
                "midPeriod": 20,
                "longPeriod": 60,
                "within": 5,
                "alignType": "positive",
            }
        ],
    },
    "ma-align-negative": {
        "filter_id": "CUSTOM_이동평균선_배열",
        "condition_id": "이동평균선_배열",
        "type": "MOVING_AVERAGE_ALIGN_ARRAY",
        "value": [
            {
                "shortPeriod": 5,
                "midPeriod": 20,
                "longPeriod": 60,
                "within": 5,
                "alignType": "negative",
            }
        ],
    },
    "bollinger-upper-up": {
        "filter_id": "CUSTOM_주가_볼린저밴드_돌파",
        "condition_id": "주가_볼린저밴드_돌파",
        "type": "PRICE_BOLLINGER_BAND_CROSS_ARRAY",
        "value": [{"within": 5, "crossBand": "upper", "crossDirection": "upward"}],
    },
    "bollinger-lower-down": {
        "filter_id": "CUSTOM_주가_볼린저밴드_돌파",
        "condition_id": "주가_볼린저밴드_돌파",
        "type": "PRICE_BOLLINGER_BAND_CROSS_ARRAY",
        "value": [{"within": 5, "crossBand": "lower", "crossDirection": "downward"}],
    },
}

ALLOWED_FILTER_IDS = {
    RSI_FILTER_ID,
    *(config["filter_id"] for config in PRICE_PRESETS.values()),
    *(config["filter_id"] for config in TECHNICAL_PRESETS.values()),
}
ALLOWED_CONDITION_IDS = {
    NUMBER_RANGE_CONDITION_ID,
    "기간_선택_DAY_TO_MONTH",
    "WEEK_NEW_PRICE_HIT",
    *(config["condition_id"] for config in TECHNICAL_PRESETS.values()),
}
ALLOWED_CONDITION_TYPES = {
    "MOVING_AVERAGE_ALIGN_ARRAY",
    "MOVING_AVERAGE_CROSS_ARRAY",
    "NUMBER_RANGE",
    "PERIOD",
    "PRICE_BOLLINGER_BAND_CROSS_ARRAY",
    "PRICE_MOVING_AVERAGE_CROSS_ARRAY",
    "WEEK_NEW_PRICE_HIT_WITHIN",
}


def normalize_nation(nation: str) -> str:
    normalized = nation.strip().lower()
    if normalized not in {"kr", "us"}:
        raise ValueError("nation must be 'kr' or 'us'")
    return normalized


def build_count_body(nation: str, filters: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"filters": validate_filters(filters or []), "nation": normalize_nation(nation)}


def build_common_presets_path(use_custom: bool = True) -> str:
    return api.build_path(
        "/api/v2/screener/presets/common",
        {"useCustom": use_custom},
    )


def build_search_modal_path() -> str:
    return "/api/v2/screener/screen/search/modal"


def build_filter_base_body(nation: str, filter_id: str) -> dict[str, Any]:
    if filter_id not in ALLOWED_FILTER_IDS:
        raise ValueError(f"undocumented screener filter id: {filter_id}")
    return {"filterId": filter_id, "nation": normalize_nation(nation)}


def build_filter_range_body(nation: str, filter_body: dict[str, Any]) -> dict[str, Any]:
    validated = validate_filters([filter_body])[0]
    return {"filter": validated, "nation": normalize_nation(nation)}


def validate_filter_metadata_selection(
    filters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validated = validate_filters(filters)
    api.require_int_range("filter metadata count", len(validated), minimum=1, maximum=10)
    filter_ids = [filter_body["id"] for filter_body in validated]
    if len(filter_ids) != len(set(filter_ids)):
        raise ValueError("filter metadata requires unique filter ids")
    return validated


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


def build_technical_filter(preset: str) -> dict[str, Any]:
    try:
        config = TECHNICAL_PRESETS[preset.strip().lower()]
    except KeyError as exc:
        choices = ", ".join(sorted(TECHNICAL_PRESETS))
        raise ValueError(f"technical preset must be one of: {choices}") from exc
    return {
        "id": config["filter_id"],
        "conditions": [
            {
                "id": config["condition_id"],
                "type": config["type"],
                "value": config["value"],
            }
        ],
    }


def build_price_filter(preset: str) -> dict[str, Any]:
    try:
        config = PRICE_PRESETS[preset.strip().lower()]
    except KeyError as exc:
        choices = ", ".join(sorted(PRICE_PRESETS))
        raise ValueError(f"price preset must be one of: {choices}") from exc
    return {"id": config["filter_id"], "conditions": config["conditions"]}


def build_sort(sort_key: str, order: str = "desc") -> dict[str, Any]:
    try:
        column = SORT_COLUMNS[sort_key.strip().lower()]
    except KeyError as exc:
        choices = ", ".join(sorted(SORT_COLUMNS))
        raise ValueError(f"sort must be one of: {choices}") from exc
    normalized_order = order.strip().upper()
    if normalized_order not in {"ASC", "DESC"}:
        raise ValueError("sort order must be 'asc' or 'desc'")
    return {**column, "order": normalized_order}


def build_screen_body(
    nation: str,
    filters: list[dict[str, Any]] | None = None,
    size: int = 20,
    page: int = 1,
    sort: dict[str, Any] | None = None,
) -> dict[str, Any]:
    size = api.require_int_range("size", size, minimum=1, maximum=100)
    page = api.require_int_range("page", page, minimum=1, maximum=100)
    body = {
        "filters": filters or [],
        "nation": normalize_nation(nation),
        "pagingParam": {"number": page, "size": size},
    }
    if sort is not None:
        body["sort"] = sort
    return body


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
    page: int = 1,
    sort: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = build_screen_body(nation, filters, size, page, sort)
    return api.get_result(
        "/api/v2/screener/screen",
        method="POST",
        body=body,
        base_url=CERT_URL,
    )


def fetch_common_presets(use_custom: bool = True) -> Any:
    return api.get_result(build_common_presets_path(use_custom), base_url=CERT_URL)


def fetch_search_modal() -> Any:
    return api.get_result(build_search_modal_path(), base_url=CERT_URL)


def fetch_filter_base(nation: str, filter_id: str) -> Any:
    return api.get_result(
        "/api/v1/screener/filters/base",
        method="POST",
        body=build_filter_base_body(nation, filter_id),
        base_url=CERT_URL,
    )


def fetch_filter_range(nation: str, filter_body: dict[str, Any]) -> Any:
    return api.get_result(
        "/api/v1/screener/filters/range",
        method="POST",
        body=build_filter_range_body(nation, filter_body),
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
    return validate_filters(payload)


def validate_filters(filters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for filter_body in filters:
        filter_id = filter_body.get("id")
        if filter_id not in ALLOWED_FILTER_IDS:
            raise ValueError(f"undocumented screener filter id: {filter_id}")
        conditions = filter_body.get("conditions")
        if not isinstance(conditions, list):
            raise ValueError(f"filter {filter_id} must include a conditions list")
        for condition in conditions:
            if not isinstance(condition, dict):
                raise ValueError(f"filter {filter_id} conditions must be JSON objects")
            condition_id = condition.get("id")
            condition_type = condition.get("type")
            if condition_id not in ALLOWED_CONDITION_IDS:
                raise ValueError(f"undocumented screener condition id: {condition_id}")
            if condition_type not in ALLOWED_CONDITION_TYPES:
                raise ValueError(f"undocumented screener condition type: {condition_type}")
    return filters


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
    parser.add_argument(
        "--include-common-presets",
        action="store_true",
        help="Also fetch public common screener preset metadata",
    )
    parser.add_argument(
        "--no-custom-presets",
        action="store_true",
        help="Use useCustom=false when --include-common-presets is set",
    )
    parser.add_argument(
        "--include-search-modal",
        action="store_true",
        help="Also fetch public screener search modal metadata",
    )
    parser.add_argument(
        "--include-filter-base",
        action="store_true",
        help="Fetch based-at metadata for each selected filter",
    )
    parser.add_argument(
        "--include-filter-range",
        action="store_true",
        help="Fetch the current public min/max range for each selected filter",
    )
    parser.add_argument(
        "--technical-filter",
        action="append",
        choices=sorted(TECHNICAL_PRESETS),
        help="Add a built-in technical screener filter preset; can be repeated",
    )
    parser.add_argument(
        "--price-filter",
        action="append",
        choices=sorted(PRICE_PRESETS),
        help="Add a built-in price-condition screener filter preset; can be repeated",
    )
    parser.add_argument(
        "--sort",
        choices=sorted(SORT_COLUMNS),
        help="Sort result rows by an observed sortable column",
    )
    parser.add_argument(
        "--sort-order",
        choices=["asc", "desc"],
        default="desc",
        help="Sort direction when --sort is used",
    )
    parser.add_argument("--page", type=int, default=1, help="Result page number when used")
    parser.add_argument("--size", type=int, default=20, help="Result page size when used")
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    filters = load_filters(args.filters_file)
    if args.rsi:
        filters.append(build_rsi_filter(args.rsi))
    for preset in args.price_filter or []:
        filters.append(build_price_filter(preset))
    for preset in args.technical_filter or []:
        filters.append(build_technical_filter(preset))
    payload = fetch_screener_count(args.nation, filters)
    if args.include_results:
        sort = build_sort(args.sort, args.sort_order) if args.sort else None
        payload["results"] = fetch_screener_results(
            args.nation,
            filters,
            args.size,
            args.page,
            sort,
        )
    if args.include_common_presets:
        payload["commonPresets"] = fetch_common_presets(not args.no_custom_presets)
    if args.include_search_modal:
        payload["searchModal"] = fetch_search_modal()
    if args.include_filter_base or args.include_filter_range:
        metadata_filters = validate_filter_metadata_selection(filters)
        if args.include_filter_base:
            payload["filterBase"] = {
                filter_body["id"]: fetch_filter_base(args.nation, filter_body["id"])
                for filter_body in metadata_filters
            }
        if args.include_filter_range:
            payload["filterRange"] = {
                filter_body["id"]: fetch_filter_range(args.nation, filter_body)
                for filter_body in metadata_filters
            }
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
