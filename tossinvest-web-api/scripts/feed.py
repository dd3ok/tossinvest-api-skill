#!/usr/bin/env python3
"""Fetch read-only TossInvest feed and dashboard-news payloads."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api


FEED_PATHS = {
    "recommended": "/api/v3/feed/recommend/posts",
    "recommended-ranking": "/api/v4/feed/recommend/ranking-posts",
    "subscription": "/api/v3/feed/subscription/posts",
}

NEWS_TYPES = {
    "PERSONALIZED",
    "PERSONALIZE_HOLD",
    "PERSONALIZE_WATCH",
    "ALL_HIGHLIGHT",
    "HOT",
    "SOARING_STOCK",
    "INDEX",
}


def build_feed_path(kind: str, last_recommend_id: str | None) -> str:
    if kind not in FEED_PATHS:
        raise ValueError(f"unknown feed kind: {kind}")
    params: dict[str, Any] = {}
    if kind == "subscription":
        params["filterType"] = "COMMENT"
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
        body["indexCode"] = index_code.strip().upper()
    return body


def fetch_feed(kind: str, last_recommend_id: str | None) -> dict[str, Any]:
    return {
        "kind": kind,
        "result": api.get_result(build_feed_path(kind, last_recommend_id)),
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest feed recommendations or dashboard news."
    )
    parser.add_argument(
        "--kind",
        choices=[*sorted(FEED_PATHS), "news"],
        default="recommended",
    )
    parser.add_argument("--last-recommend-id")
    parser.add_argument("--news-type", default="HOT", choices=sorted(NEWS_TYPES))
    parser.add_argument("--index-code", help="Required for --news-type INDEX")
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    if args.kind == "news":
        payload = fetch_dashboard_news(args.news_type, args.index_code)
    else:
        payload = fetch_feed(args.kind, args.last_recommend_id)
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
