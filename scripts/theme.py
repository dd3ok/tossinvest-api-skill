#!/usr/bin/env python3
"""Fetch read-only TossInvest theme/TICS discovery data."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

COMPANY_RANKINGS = {
    "marketcap": 1,
    "revenue": 3,
    "operating-margin": 4,
}


def build_theme_ranking_path(tag: str) -> str:
    return f"/api/v1/rankings/contents/tics_margin_depth1/tags/{tag.strip().lower()}"


def build_theme_details_path(tics_id: str) -> str:
    return f"/api/v1/tics/{tics_id}/details"


def build_theme_news_path(tics_id: str, size: int) -> str:
    return api.build_path(f"/api/v2/news/tics/{tics_id}", {"size": size})


def build_theme_company_ranking_path(tics_id: str, ranking: str) -> str:
    if ranking not in COMPANY_RANKINGS:
        raise ValueError(f"unknown company ranking: {ranking}")
    return api.build_path(
        "/api/v1/companies/tics/rankings",
        {"ticsId": tics_id, "ticsRanking": COMPANY_RANKINGS[ranking]},
    )


def build_related_path(tics_id: str) -> str:
    return f"/api/v1/tics/{tics_id}/related"


def build_fluctuations_path(tics_id: str) -> str:
    return f"/api/v2/tics/{tics_id}/fluctuations"


def fetch_theme_payload(
    *,
    tag: str,
    tics_id: str | None,
    news_size: int,
    include_all: bool,
    include_details: bool,
    company_rankings: list[str],
) -> dict[str, Any]:
    news_size = api.require_int_range("news-size", news_size, minimum=1, maximum=50)
    payload: dict[str, Any] = {
        "tag": tag.strip().lower(),
        "ranking": api.get_result(build_theme_ranking_path(tag)),
    }
    if include_all:
        payload["allThemes"] = api.get_result("/api/v1/tics/all")
    if tics_id is not None:
        payload["ticsId"] = tics_id
        if include_details:
            payload["details"] = api.get_result(build_theme_details_path(tics_id))
        payload["related"] = api.get_result(build_related_path(tics_id))
        payload["news"] = api.get_result(build_theme_news_path(tics_id, news_size))
        payload["fluctuations"] = api.get_result(build_fluctuations_path(tics_id))
        if company_rankings:
            payload["companyRankings"] = {
                ranking: api.get_result(build_theme_company_ranking_path(tics_id, ranking))
                for ranking in company_rankings
            }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest theme/TICS rankings and optional theme details."
    )
    parser.add_argument(
        "--tag",
        default="kr",
        help="Theme ranking tag observed in TossInvest, commonly kr or us",
    )
    parser.add_argument("--tics-id", help="Also fetch details for this TICS id")
    parser.add_argument(
        "--news-size",
        type=int,
        default=5,
        help="Number of theme news items to request when --tics-id is set",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Also fetch /api/v1/tics/all",
    )
    parser.add_argument(
        "--include-details",
        action="store_true",
        help="Also fetch /api/v1/tics/{id}/details when --tics-id is set",
    )
    parser.add_argument(
        "--company-ranking",
        action="append",
        choices=sorted(COMPANY_RANKINGS),
        default=[],
        help="Also fetch a TICS company ranking; repeat for multiple rankings",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_theme_payload(
        tag=args.tag,
        tics_id=args.tics_id,
        news_size=args.news_size,
        include_all=args.include_all,
        include_details=args.include_details,
        company_rankings=args.company_ranking,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
