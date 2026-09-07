#!/usr/bin/env python3
"""Fetch sanitized public TossInvest stock or lounge community comments."""

from __future__ import annotations

import argparse
import re
from typing import Any

import tossinvest_api as api

CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"

COMMENT_SORTS = {"popular": "POPULAR", "recent": "RECENT"}
_PRODUCT_CODE_RE = re.compile(r"^[A-Z0-9._-]{2,48}$")
_LOUNGE_ID_RE = re.compile(r"^LOUNGE_\d{1,30}$")
_DIGIT_ID_RE = re.compile(r"^[0-9]{1,30}$")
_PHONE_RE = re.compile(
    r"(?<!\w)(?:\+82[\s.-]?)?(?:0?1[016789]|0\d{1,2})[\s.-]?\d{3,4}[\s.-]?\d{4}(?!\w)"
)
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_LONG_DIGIT_RE = re.compile(r"\b\d{8,}\b")
_MENTION_PROFILE_RE = re.compile(r"(\#\[[^\]\r\n]{1,80}\])\([0-9]{1,30}\)")


def build_stock_comments_path(
    subject_id: str,
    sort: str,
    last_comment_id: str | int | None,
) -> str:
    """Build a comment path using an already resolved stock metadata GUID."""
    return build_subject_comments_path("STOCK", subject_id, sort, last_comment_id)


def build_lounge_comments_path(
    lounge_id: str,
    sort: str,
    last_comment_id: str | int | None,
) -> str:
    return build_subject_comments_path(
        "LOUNGE",
        validate_lounge_id(lounge_id),
        sort,
        last_comment_id,
    )


def build_subject_comments_path(
    subject_type: str,
    subject_id: str,
    sort: str,
    last_comment_id: str | int | None,
) -> str:
    normalized_subject_type = subject_type.strip().upper()
    if normalized_subject_type == "STOCK":
        normalized_subject_id = validate_stock_subject_id(subject_id)
    elif normalized_subject_type == "LOUNGE":
        normalized_subject_id = validate_lounge_id(subject_id)
    else:
        raise ValueError("subject type must be STOCK or LOUNGE")
    sort_value = _require_sort(sort)
    params: dict[str, Any] = {
        "subjectType": normalized_subject_type,
        "subjectId": normalized_subject_id,
        "commentSortType": sort_value,
    }
    if last_comment_id is not None:
        params["lastCommentId"] = validate_digit_id("last_comment_id", last_comment_id)
    return api.build_path("/api/v4/comments", params)


def build_comment_replies_path(comment_id: str | int) -> str:
    return f"/api/v2/comments/{validate_digit_id('comment_id', comment_id)}/replies"


def build_community_post_path(
    post_id: str | int,
    last_reply_id: str | int | None,
) -> str:
    path = f"/api/v1/comments/{validate_digit_id('post_id', post_id)}/replies"
    return api.build_path(
        path,
        {
            "lastReplyId": (
                validate_digit_id("last_reply_id", last_reply_id)
                if last_reply_id is not None
                else None
            )
        },
    )


def validate_product_code(code: str) -> str:
    value = code.strip().upper()
    if not _PRODUCT_CODE_RE.fullmatch(value):
        raise ValueError(
            "product code must be 2-48 uppercase letters, numbers, dots, underscores, or hyphens"
        )
    return value


def validate_lounge_id(lounge_id: str) -> str:
    value = lounge_id.strip().upper()
    if not _LOUNGE_ID_RE.fullmatch(value):
        raise ValueError("lounge id must match LOUNGE_<digits>")
    return value


def validate_stock_subject_id(subject_id: str) -> str:
    if (
        not isinstance(subject_id, str)
        or not _PRODUCT_CODE_RE.fullmatch(subject_id)
        or subject_id.startswith("LOUNGE_")
    ):
        raise ValueError("stock subject ID must be a valid public stock metadata GUID")
    return subject_id


def resolve_comment_subject_id(code_or_symbol: str) -> str:
    """Resolve every code or symbol to the GUID used by stock comment subjects."""
    value = validate_product_code(api.normalize_product_code(code_or_symbol))
    result = api.get_result(f"/api/v2/stock-infos/code-or-symbol/{value}")
    if not isinstance(result, dict) or not isinstance(result.get("guid"), str):
        raise RuntimeError("Unexpected TossInvest response: stock info is missing a GUID")
    try:
        return validate_stock_subject_id(result["guid"])
    except ValueError as exc:
        raise RuntimeError(
            "Unexpected TossInvest response: stock info contains an invalid GUID"
        ) from exc


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
        "commentId": _digit_id_or_none(comment.get("commentId")),
        "type": _string_or_none(comment.get("type")),
        "authorNickname": redact_public_text(author.get("nickname")),
        "message": {
            "title": redact_public_text(message.get("title")),
            "message": redact_public_text(message.get("message")),
        },
        "board": {
            "subjectType": _string_or_none(board.get("subjectType")),
            "subjectId": _string_or_none(board.get("subjectId")),
            "stockCode": _string_or_none(board.get("stockCode")),
            "topic": redact_public_text(board.get("topic")),
        },
        "statistic": {
            "likeCount": _integer_or_none(statistic.get("likeCount")),
            "replyCount": _integer_or_none(statistic.get("replyCount")),
            "readCount": _integer_or_none(statistic.get("readCount")),
        },
        "holding": {
            "shareHoldingStatus": _string_or_none(holding.get("shareHoldingStatus")),
        },
        "createdAt": _string_or_none(comment.get("createdAt")),
        "updatedAt": _string_or_none(comment.get("updatedAt")),
        "edited": _boolean_or_none(comment.get("edited")),
    }
    if comment.get("media"):
        sanitized["media"] = _summarize_media(comment.get("media"))
    if comment.get("image"):
        sanitized["hasImage"] = True
    return _drop_none(sanitized)


def sanitize_post_comment(comment: dict[str, Any]) -> dict[str, Any]:
    """Normalize the public permalink response without profile/social metadata."""
    if "commentId" in comment:
        return sanitize_comment(comment)
    normalized = {
        "commentId": comment.get("id"),
        "type": comment.get("type"),
        "author": comment.get("author"),
        "message": {
            "title": comment.get("title"),
            "message": comment.get("message"),
        },
        "board": {
            "subjectType": comment.get("subjectType"),
            "subjectId": comment.get("subjectId"),
            "stockCode": comment.get("stockCode"),
            "topic": comment.get("topic"),
        },
        "statistic": {
            "likeCount": comment.get("likeCount"),
            "replyCount": comment.get("replyCount"),
            "readCount": comment.get("readCount"),
        },
        "holding": {
            "shareHoldingStatus": comment.get("instrumentHoldingStatus"),
        },
        "createdAt": comment.get("createdAt"),
        "updatedAt": comment.get("updatedAt"),
        "edited": comment.get("edited"),
        "media": comment.get("media"),
        "image": comment.get("commentPictureUrl"),
    }
    return sanitize_comment(normalized)


def fetch_stock_comments(
    code: str,
    *,
    sort: str,
    pages: int,
    limit: int,
    include_replies: bool,
    last_comment_id: str | int | None = None,
) -> dict[str, Any]:
    # Reject invalid local paging inputs before the metadata lookup as well.
    api.require_int_range("pages", pages, minimum=1, maximum=5)
    api.require_int_range("limit", limit, minimum=1, maximum=100)
    _require_sort(sort)
    if last_comment_id is not None:
        validate_digit_id("last_comment_id", last_comment_id)
    subject_id = resolve_comment_subject_id(code)
    return _fetch_subject_comments(
        "STOCK",
        subject_id,
        sort=sort,
        pages=pages,
        limit=limit,
        include_replies=include_replies,
        last_comment_id=last_comment_id,
    )


def fetch_lounge_comments(
    lounge_id: str,
    *,
    sort: str,
    pages: int,
    limit: int,
    include_replies: bool,
    last_comment_id: str | int | None = None,
) -> dict[str, Any]:
    return _fetch_subject_comments(
        "LOUNGE",
        validate_lounge_id(lounge_id),
        sort=sort,
        pages=pages,
        limit=limit,
        include_replies=include_replies,
        last_comment_id=last_comment_id,
    )


def _fetch_subject_comments(
    subject_type: str,
    subject_id: str,
    *,
    sort: str,
    pages: int,
    limit: int,
    include_replies: bool,
    last_comment_id: str | int | None = None,
) -> dict[str, Any]:
    pages = api.require_int_range("pages", pages, minimum=1, maximum=5)
    limit = api.require_int_range("limit", limit, minimum=1, maximum=100)
    comments: list[dict[str, Any]] = []
    applied_last_comment_id = (
        validate_digit_id("last_comment_id", last_comment_id)
        if last_comment_id is not None
        else None
    )
    cursor = applied_last_comment_id
    seen_cursors = {cursor} if cursor is not None else set()
    has_next = False
    pages_fetched = 0
    next_key: Any = None

    for _ in range(pages):
        result = api.get_result(
            build_subject_comments_path(subject_type, subject_id, sort, cursor),
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
        last_emitted_comment_id: str | None = None
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
            last_emitted_comment_id = (
                validate_digit_id("comment_id", comment_id) if comment_id is not None else None
            )
            if len(comments) >= limit:
                truncated_mid_page = row_index < len(rows) - 1
                break
        server_has_next = bool(result.get("hasNext"))
        next_key = result.get("key") if server_has_next else None
        if truncated_mid_page:
            next_key = last_emitted_comment_id
        if next_key is not None:
            next_key = validate_digit_id("last_comment_id", next_key)
        if (server_has_next or truncated_mid_page) and next_key is None:
            raise RuntimeError("Unexpected TossInvest response: comment cursor is missing")
        if next_key is not None:
            if next_key in seen_cursors:
                raise RuntimeError("Unexpected TossInvest response: comment cursor did not advance")
            seen_cursors.add(next_key)
        has_next = bool(next_key is not None and (server_has_next or truncated_mid_page))
        if len(comments) >= limit or not has_next:
            break
        cursor = validate_digit_id("last_comment_id", next_key)

    return {
        "subjectType": subject_type,
        "subjectId": subject_id,
        "sort": _require_sort(sort),
        "lastCommentId": applied_last_comment_id,
        "pagesFetched": pages_fetched,
        "hasNext": has_next,
        "nextLastCommentId": next_key,
        "comments": comments,
    }


def fetch_community_post(
    post_id: str | int,
    *,
    pages: int,
    limit: int,
    last_reply_id: str | int | None = None,
) -> dict[str, Any]:
    normalized_post_id = validate_digit_id("post_id", post_id)
    pages = api.require_int_range("pages", pages, minimum=1, maximum=5)
    limit = api.require_int_range("limit", limit, minimum=1, maximum=100)
    replies: list[dict[str, Any]] = []
    applied_last_reply_id = (
        validate_digit_id("last_reply_id", last_reply_id) if last_reply_id is not None else None
    )
    cursor = applied_last_reply_id
    seen_cursors = {cursor} if cursor is not None else set()
    next_key: str | None = None
    has_next = False
    pages_fetched = 0
    sanitized_comment: dict[str, Any] | None = None
    topic: Any = None

    for _ in range(pages):
        result = api.get_result(
            build_community_post_path(normalized_post_id, cursor),
            base_url=CERT_BASE_URL,
        )
        if not isinstance(result, dict):
            raise RuntimeError(
                "Unexpected TossInvest response: community post result is not a dictionary"
            )
        raw_comment = result.get("comment")
        reply_page = result.get("replies")
        if not isinstance(raw_comment, dict) or not isinstance(reply_page, dict):
            raise RuntimeError(
                "Unexpected TossInvest response: community post or replies are missing"
            )
        rows = reply_page.get("body")
        if not isinstance(rows, list):
            raise RuntimeError(
                "Unexpected TossInvest response: community post replies body is not a list"
            )
        if sanitized_comment is None:
            sanitized_comment = sanitize_post_comment(raw_comment)
            raw_topic = result.get("topic")
            topic = redact_public_text(raw_topic) if isinstance(raw_topic, str) else None

        pages_fetched += 1
        truncated_mid_page = False
        last_emitted_reply_id: str | None = None
        for row_index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise RuntimeError(
                    "Unexpected TossInvest response: community post reply is not a dictionary"
                )
            sanitized = sanitize_post_comment(row)
            replies.append(sanitized)
            reply_id = sanitized.get("commentId")
            last_emitted_reply_id = (
                validate_digit_id("reply_id", reply_id) if reply_id is not None else None
            )
            if len(replies) >= limit:
                truncated_mid_page = row_index < len(rows) - 1
                break

        server_has_next = bool(reply_page.get("hasNext"))
        if truncated_mid_page:
            next_key = last_emitted_reply_id
        elif server_has_next and rows:
            next_key = last_emitted_reply_id
        else:
            next_key = None
        if (server_has_next or truncated_mid_page) and next_key is None:
            raise RuntimeError(
                "Unexpected TossInvest response: community post reply cursor is missing"
            )
        if next_key is not None:
            if next_key in seen_cursors:
                raise RuntimeError(
                    "Unexpected TossInvest response: community post reply cursor did not advance"
                )
            seen_cursors.add(next_key)
        has_next = bool(next_key is not None and (server_has_next or truncated_mid_page))
        if len(replies) >= limit or not has_next:
            break
        cursor = next_key

    if sanitized_comment is None:
        raise RuntimeError("Unexpected TossInvest response: community post comment is missing")
    return {
        "kind": "community-post",
        "postId": normalized_post_id,
        "lastReplyId": applied_last_reply_id,
        "topic": topic,
        "comment": sanitized_comment,
        "pagesFetched": pages_fetched,
        "hasNext": has_next,
        "nextLastReplyId": next_key,
        "replies": replies,
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


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _digit_id_or_none(value: Any) -> str | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if _DIGIT_ID_RE.fullmatch(str(value)) else None
    if isinstance(value, str) and _DIGIT_ID_RE.fullmatch(value):
        return value
    return None


def _integer_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _boolean_or_none(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def redact_public_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = _MENTION_PROFILE_RE.sub(r"\1", value)
    value = _EMAIL_RE.sub("[redacted-email]", value)
    value = _PHONE_RE.sub("[redacted-phone]", value)
    return _LONG_DIGIT_RE.sub("[redacted-number]", value)


def _summarize_media(value: Any) -> dict[str, Any]:
    if not isinstance(value, list):
        return {"count": 1}
    return {
        "count": len(value),
        "types": sorted(
            {
                item["type"]
                for item in value
                if isinstance(item, dict) and isinstance(item.get("type"), str)
            }
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
        description=("Fetch sanitized public TossInvest stock/lounge comments or a community post.")
    )
    subject_group = parser.add_mutually_exclusive_group(required=True)
    subject_group.add_argument("--code", help="TossInvest stock product code")
    subject_group.add_argument("--lounge-id", help="Public lounge id, e.g. LOUNGE_193394")
    subject_group.add_argument("--post-id", help="Public community post id from a permalink")
    parser.add_argument("--sort", choices=sorted(COMMENT_SORTS), default="popular")
    parser.add_argument("--pages", type=int, default=1, help="Maximum comment pages to fetch")
    parser.add_argument("--limit", type=int, default=10, help="Maximum sanitized comments to emit")
    parser.add_argument(
        "--last-comment-id",
        help="Stock/lounge cursor from a previous nextLastCommentId",
    )
    parser.add_argument(
        "--last-reply-id",
        help="Post cursor from a previous nextLastReplyId",
    )
    parser.add_argument(
        "--include-replies", action="store_true", help="Fetch replies for returned comments"
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    if args.post_id:
        if args.last_comment_id is not None:
            raise ValueError("--last-comment-id cannot be used with --post-id")
        payload = fetch_community_post(
            args.post_id,
            pages=args.pages,
            limit=args.limit,
            last_reply_id=args.last_reply_id,
        )
    elif args.lounge_id:
        if args.last_reply_id is not None:
            raise ValueError("--last-reply-id requires --post-id")
        payload = fetch_lounge_comments(
            args.lounge_id,
            sort=args.sort,
            pages=args.pages,
            limit=args.limit,
            include_replies=args.include_replies,
            last_comment_id=args.last_comment_id,
        )
    else:
        if args.last_reply_id is not None:
            raise ValueError("--last-reply-id requires --post-id")
        payload = fetch_stock_comments(
            args.code,
            sort=args.sort,
            pages=args.pages,
            limit=args.limit,
            include_replies=args.include_replies,
            last_comment_id=args.last_comment_id,
        )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
