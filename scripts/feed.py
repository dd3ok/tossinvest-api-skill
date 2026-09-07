#!/usr/bin/env python3
"""Fetch read-only TossInvest public market feed and dashboard-news payloads."""

from __future__ import annotations

import argparse
import re
from typing import Any

import community_comments
import indices
import tossinvest_api as api

CERT_BASE_URL = "https://wts-cert-api.tossinvest.com"

FEED_PATHS = {
    "recommended": "/api/v4/feed/recommend/ranking-posts",
    "recommended-ranking": "/api/v4/feed/recommend/ranking-posts",
}
FEED_BASE_URLS = {
    "recommended": CERT_BASE_URL,
    "recommended-ranking": CERT_BASE_URL,
}
_RECOMMEND_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

NEWS_TYPES = {
    "ALL_HIGHLIGHT",
    "HOT",
    "SOARING_STOCK",
    "INDEX",
}
COMMUNITY_RANKINGS = {
    "followers": "TOP_10_FOLLOWING_INCREASE",
    "profit": "TOP_10_PROFIT_ROSS_AMOUNT",
}


def build_feed_path(kind: str, last_recommend_id: str | None) -> str:
    if kind not in FEED_PATHS:
        raise ValueError(f"unknown feed kind: {kind}")
    params: dict[str, Any] = {}
    if last_recommend_id is not None and kind.startswith("recommended"):
        params["lastRecommendId"] = last_recommend_id
    return api.build_path(FEED_PATHS[kind], params)


def build_news_body(news_type: str, index_code: str | None) -> dict[str, Any]:
    normalized_type = news_type.strip().upper()
    if normalized_type not in NEWS_TYPES:
        raise ValueError(f"unknown news type: {news_type}")
    body: dict[str, Any] = {"type": normalized_type}
    if normalized_type == "INDEX":
        if index_code is None:
            raise ValueError("INDEX news requires --index-code")
        body["indexCode"] = indices.normalize_index_code(index_code)
    return body


def fetch_feed(kind: str, last_recommend_id: str | None) -> dict[str, Any]:
    if kind not in FEED_PATHS:
        raise ValueError(f"unknown feed kind: {kind}")
    result = api.get_result(
        build_feed_path(kind, last_recommend_id),
        base_url=FEED_BASE_URLS.get(kind, api.BASE_URL),
    )
    sanitized = sanitize_recommended_feed_result(result)
    return {
        "kind": kind,
        "lastRecommendId": last_recommend_id,
        **sanitized,
    }


def sanitize_recommended_feed_result(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict) or not isinstance(result.get("feeds"), list):
        raise RuntimeError("Unexpected TossInvest response: recommended feed rows are missing")
    feeds: list[dict[str, Any]] = []
    for row in result["feeds"]:
        if not isinstance(row, dict):
            continue
        comment = row.get("comment")
        if not isinstance(comment, dict):
            continue
        sanitized_row: dict[str, Any] = {
            "comment": community_comments.sanitize_post_comment(comment),
        }
        if isinstance(row.get("type"), str):
            sanitized_row["type"] = row["type"]
        feeds.append(sanitized_row)

    key = result.get("key") if isinstance(result.get("key"), dict) else {}
    next_id = key.get("lastRecommendId")
    if not isinstance(next_id, str) or not _RECOMMEND_ID_RE.fullmatch(next_id):
        next_id = None
    return {
        "feedCount": len(feeds),
        "hasNext": next_id is not None,
        "nextLastRecommendId": next_id,
        "feeds": feeds,
    }


def fetch_dashboard_news(news_type: str, index_code: str | None) -> dict[str, Any]:
    body = build_news_body(news_type, index_code)
    return {
        "kind": "news",
        "body": body,
        "result": api.get_result(
            "/api/v1/dashboard/wts/news",
            method="POST",
            body=body,
        ),
    }


def fetch_community_ranking(ranking: str, limit: int) -> dict[str, Any]:
    if ranking not in COMMUNITY_RANKINGS:
        raise ValueError(
            f"community ranking must be one of: {', '.join(sorted(COMMUNITY_RANKINGS))}"
        )
    limit = api.require_int_range("community-limit", limit, minimum=1, maximum=10)
    ranking_id = COMMUNITY_RANKINGS[ranking]
    result = api.get_result(
        f"/api/v1/community/top-rankings/{ranking_id}",
        base_url=CERT_BASE_URL,
    )
    if not isinstance(result, dict) or not isinstance(result.get("items"), list):
        raise RuntimeError("Unexpected TossInvest response: community ranking items are missing")
    items = [
        sanitize_community_ranking_item(row, rank)
        for rank, row in enumerate(result["items"][:limit], start=1)
        if isinstance(row, dict)
    ]
    return {
        "kind": "community-ranking",
        "ranking": ranking,
        "rankingId": ranking_id,
        "items": items,
    }


def sanitize_community_ranking_item(item: dict[str, Any], rank: int) -> dict[str, Any]:
    target = item.get("target") if isinstance(item.get("target"), dict) else {}
    nickname = target.get("nickname")
    sanitized: dict[str, Any] = {
        "rank": rank,
        "nickname": community_comments.redact_public_text(nickname)
        if isinstance(nickname, str)
        else None,
        "type": item.get("type") if isinstance(item.get("type"), str) else None,
    }
    for key in (
        "profitLossAmountKrw",
        "profitLossRateKrw",
        "followingCount",
        "followingIncrease",
    ):
        value = item.get(key)
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            sanitized[key] = value
    return {key: value for key, value in sanitized.items() if value is not None}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest feed recommendations or dashboard news."
    )
    parser.add_argument(
        "--kind",
        choices=[*sorted(FEED_PATHS), "community-ranking", "news"],
        default="recommended",
    )
    parser.add_argument("--last-recommend-id")
    parser.add_argument("--news-type", default="HOT", choices=sorted(NEWS_TYPES))
    parser.add_argument("--index-code", help="Required for --news-type INDEX")
    parser.add_argument(
        "--community-ranking",
        choices=sorted(COMMUNITY_RANKINGS),
        default="profit",
    )
    parser.add_argument("--community-limit", type=int, default=10)
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    if args.kind == "community-ranking":
        payload = fetch_community_ranking(args.community_ranking, args.community_limit)
    elif args.kind == "news":
        payload = fetch_dashboard_news(args.news_type, args.index_code)
    else:
        payload = fetch_feed(args.kind, args.last_recommend_id)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
