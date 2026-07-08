#!/usr/bin/env python3
"""Fetch sanitized public TossInvest stock community comments."""

from __future__ import annotations

import argparse
import re
from typing import Any

import tossinvest_api as api

CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"

COMMENT_SORTS = {"popular": "POPULAR", "recent": "RECENT"}
_PRODUCT_CODE_RE = re.compile(r"^[A-Z0-9._-]{2,48}$")
_STOCK_PRODUCT_CODE_RE = re.compile(r"^(A\d{6}|US\d{11})$")
_DIGIT_ID_RE = re.compile(r"^\d{1,30}$")
_PHONE_RE = re.compile(
    r"(?<!\w)(?:\+82[\s.-]?)?(?:0?1[016789]|0\d{1,2})[\s.-]?\d{3,4}[\s.-]?\d{4}(?!\w)"
)
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_LONG_DIGIT_RE = re.compile(r"\b\d{8,}\b")


def build_stock_comments_path(
    code: str,
    sort: str,
    last_comment_id: str | int | None,
) -> str:
    product_code = validate_product_code(api.normalize_product_code(code))
    sort_value = _require_sort(sort)
    params: dict[str, Any] = {
        "subjectType": "STOCK",
        "subjectId": product_code,
        "commentSortType": sort_value,
    }
    if last_comment_id is not None:
        params["lastCommentId"] = validate_digit_id("last_comment_id", last_comment_id)
    return api.build_path("/api/v4/comments", params)


def build_comment_replies_path(comment_id: str | int) -> str:
    return f"/api/v2/comments/{validate_digit_id('comment_id', comment_id)}/replies"


def validate_product_code(code: str) -> str:
    value = code.strip().upper()
    if not _PRODUCT_CODE_RE.fullmatch(value):
        raise ValueError(
            "product code must be 2-48 uppercase letters, numbers, dots, underscores, or hyphens"
        )
    return value


def resolve_comment_subject_code(code_or_symbol: str) -> str:
    value = validate_product_code(api.normalize_product_code(code_or_symbol))
    if _STOCK_PRODUCT_CODE_RE.fullmatch(value):
        return value
    result = api.get_result(f"/api/v2/stock-infos/code-or-symbol/{value}")
    if not isinstance(result, dict) or not result.get("code"):
        raise RuntimeError("Unexpected TossInvest response: stock info is missing product code")
    return validate_product_code(str(result["code"]))


def validate_digit_id(name: str, value: str | int) -> str:
    normalized = str(value).strip()
    if not _DIGIT_ID_RE.fullmatch(normalized):
        raise ValueError(f"{name} must contain digits only")
    return normalized


def _require_sort(sort: str) -> str:
    key = sort.strip().lower()
    if key not in COMMENT_SORTS:
        raise ValueError(f"sort must be one of: {', '.join(sorted(COMMENT_SORTS))}")
    return COMMENT_SORTS[key]


def sanitize_comment(comment: dict[str, Any]) -> dict[str, Any]:
    author = _dict_or_empty(comment.get("author"))
    message = _dict_or_empty(comment.get("message"))
    statistic = _dict_or_empty(comment.get("statistic"))
    board = _dict_or_empty(comment.get("board"))
    holding = _dict_or_empty(comment.get("holding"))
    sanitized: dict[str, Any] = {
        "commentId": comment.get("commentId"),
        "type": comment.get("type"),
        "authorNickname": _redact_text(author.get("nickname")),
        "message": {
            "title": _redact_text(message.get("title")),
            "message": _redact_text(message.get("message")),
        },
        "board": {
            "subjectType": board.get("subjectType"),
            "subjectId": board.get("subjectId"),
            "stockCode": board.get("stockCode"),
            "topic": board.get("topic"),
        },
        "statistic": {
            "likeCount": statistic.get("likeCount"),
            "replyCount": statistic.get("replyCount"),
            "readCount": statistic.get("readCount"),
        },
        "holding": {
            "shareHoldingStatus": holding.get("shareHoldingStatus"),
        },
        "createdAt": comment.get("createdAt"),
        "updatedAt": comment.get("updatedAt"),
        "edited": comment.get("edited"),
    }
    if comment.get("media"):
        sanitized["media"] = _summarize_media(comment.get("media"))
    if comment.get("image"):
        sanitized["hasImage"] = True
    return _drop_none(sanitized)


def fetch_stock_comments(
    code: str,
    *,
    sort: str,
    pages: int,
    limit: int,
    include_replies: bool,
) -> dict[str, Any]:
    product_code = resolve_comment_subject_code(code)
    pages = api.require_int_range("pages", pages, minimum=1, maximum=5)
    limit = api.require_int_range("limit", limit, minimum=1, maximum=100)
    comments: list[dict[str, Any]] = []
    last_comment_id: str | None = None
    has_next = False
    pages_fetched = 0
    next_key: Any = None
    last_emitted_comment_id: str | None = None

    for _ in range(pages):
        result = api.get_result(
            build_stock_comments_path(product_code, sort, last_comment_id),
            base_url=CERT_BASE_URL,
        )
        if not isinstance(result, dict):
            raise RuntimeError(
                "Unexpected TossInvest response: comments result is not a dictionary"
            )
        rows = result.get("results")
        if not isinstance(rows, list):
            raise RuntimeError("Unexpected TossInvest response: comments results is not a list")
        pages_fetched += 1
        truncated_mid_page = False
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise RuntimeError(
                    "Unexpected TossInvest response: comment row is not a dictionary"
                )
            sanitized = sanitize_comment(row)
            if include_replies and sanitized.get("commentId") is not None:
                sanitized["replies"] = fetch_comment_replies(sanitized["commentId"])
            comments.append(sanitized)
            comment_id = sanitized.get("commentId")
            if comment_id is not None:
                last_emitted_comment_id = validate_digit_id("comment_id", comment_id)
            if len(comments) >= limit:
                truncated_mid_page = row_index < len(rows) - 1
                break
        has_next = bool(result.get("hasNext"))
        next_key = result.get("key")
        if truncated_mid_page:
            next_key = last_emitted_comment_id
        if len(comments) >= limit or not has_next or next_key is None:
            break
        last_comment_id = validate_digit_id("last_comment_id", next_key)

    return {
        "subjectType": "STOCK",
        "subjectId": product_code,
        "sort": _require_sort(sort),
        "pagesFetched": pages_fetched,
        "hasNext": has_next,
        "nextLastCommentId": next_key,
        "comments": comments,
    }


def fetch_comment_replies(comment_id: str | int) -> list[dict[str, Any]]:
    result = api.get_result(build_comment_replies_path(comment_id), base_url=CERT_BASE_URL)
    if isinstance(result, dict) and isinstance(result.get("results"), list):
        return [sanitize_comment(row) for row in result["results"] if isinstance(row, dict)]
    if isinstance(result, dict) and isinstance(result.get("replies"), list):
        return [sanitize_comment(row) for row in result["replies"] if isinstance(row, dict)]
    raise RuntimeError("Unexpected TossInvest response: replies result does not contain a list")


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _redact_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    value = _EMAIL_RE.sub("[redacted-email]", value)
    value = _PHONE_RE.sub("[redacted-phone]", value)
    return _LONG_DIGIT_RE.sub("[redacted-number]", value)


def _summarize_media(value: Any) -> dict[str, Any]:
    if not isinstance(value, list):
        return {"count": 1}
    return {
        "count": len(value),
        "types": sorted(
            {str(item.get("type")) for item in value if isinstance(item, dict) and item.get("type")}
        ),
    }


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _drop_none(child) for key, child in value.items() if child is not None}
    if isinstance(value, list):
        return [_drop_none(child) for child in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch sanitized public TossInvest stock community comments."
    )
    parser.add_argument("--code", required=True, help="TossInvest stock product code")
    parser.add_argument("--sort", choices=sorted(COMMENT_SORTS), default="popular")
    parser.add_argument("--pages", type=int, default=1, help="Maximum comment pages to fetch")
    parser.add_argument("--limit", type=int, default=10, help="Maximum sanitized comments to emit")
    parser.add_argument(
        "--include-replies", action="store_true", help="Fetch replies for returned comments"
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_stock_comments(
        args.code,
        sort=args.sort,
        pages=args.pages,
        limit=args.limit,
        include_replies=args.include_replies,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
