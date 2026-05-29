#!/usr/bin/env python3
"""Fetch read-only TossInvest trading trend endpoints."""

from __future__ import annotations

import argparse
from typing import Any

import tossinvest_api as api

RECENT_TYPES = {
    "investor": "trading-trend",
    "program": "program-trading",
}

FIXED_TYPES = {
    "fixed": "fixed-trading-trend",
    "accumulated": "accumulated-fixed-trading-trend",
    "accumulated-detail": "accumulated-fixed-trading-trend/detail",
}

MDS_INFO_TYPES = {
    "credit": "credit",
    "lending-trading": "lending-trading",
    "short-selling-trend": "short-selling-trend",
    "cfd": "cfd",
}

INVESTOR_NET_FIELDS = (
    ("individual", "개인", "netIndividualsBuyVolume"),
    ("foreigner", "외국인", "netForeignerBuyVolume"),
    ("institution_total", "기관계", "netInstitutionBuyVolume"),
    ("financial_investment", "금융투자", "netFinancialInvestmentBuyVolume"),
    ("insurance", "보험", "netInsuranceBuyVolume"),
    ("other_financial", "기타금융", "netOtherFinancialInstitutionsBuyVolume"),
    ("trust", "투신", "netTrustBuyVolume"),
    ("private_equity_fund", "사모펀드", "netPrivateEquityFundBuyVolume"),
    ("pension_fund", "연기금등", "netPensionFundBuyVolume"),
    ("bank", "은행", "netBankBuyVolume"),
    ("other_corporation", "기타법인", "netOtherCorporationBuyVolume"),
)


def _rows_from_result(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, list):
        return [row for row in result if isinstance(row, dict)]
    if not isinstance(result, dict):
        return []
    for key in ("body", "tradingTrends", "fixedTradingTrends"):
        rows = result.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    data = result.get("data")
    if isinstance(data, dict):
        for key in ("content", "items"):
            content = data.get(key)
            if isinstance(content, list):
                return [row for row in content if isinstance(row, dict)]
    return []


def normalize_investor_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        trade_date = row.get("baseDate") or row.get("date") or row.get("tradeDate")
        for investor_type, label_ko, field_name in INVESTOR_NET_FIELDS:
            if field_name not in row:
                continue
            normalized.append(
                {
                    "date": trade_date,
                    "investorType": investor_type,
                    "labelKo": label_ko,
                    "field": field_name,
                    "netBuyVolume": row.get(field_name),
                }
            )
    return normalized


def normalize_investor_result(result: Any) -> list[dict[str, Any]]:
    return normalize_investor_rows(_rows_from_result(result))


def build_trend_path(
    code: str,
    trend_type: str,
    size: int | None,
    start: str | None,
    end: str | None,
) -> str:
    product_code = api.normalize_product_code(code)
    if trend_type in RECENT_TYPES:
        return api.build_path(
            f"/api/v1/stock-infos/trade/trend/{RECENT_TYPES[trend_type]}",
            {"productCode": product_code, "size": size},
        )
    if trend_type in FIXED_TYPES:
        if start is None or end is None:
            raise ValueError(f"{trend_type} requires --from and --to")
        return api.build_path(
            f"/api/v1/stock-infos/trade/trend/{FIXED_TYPES[trend_type]}",
            {"productCode": product_code, "from": start, "to": end},
        )
    if trend_type == "broker":
        return api.build_path("/api/v1/mds/broker/trading-ranking", {"code": product_code})
    if trend_type in MDS_INFO_TYPES:
        return build_mds_info_path(product_code, trend_type, size)
    raise ValueError(f"unknown trend type: {trend_type}")


def build_mds_info_path(code: str, mds_type: str, size: int | None) -> str:
    product_code = api.normalize_product_code(code)
    if mds_type not in MDS_INFO_TYPES:
        raise ValueError(f"unknown mds info type: {mds_type}")
    return api.build_path(
        f"/api/v1/mds/info/{MDS_INFO_TYPES[mds_type]}",
        {"stockCode": product_code, "number": 1, "size": size},
    )


def fetch_trading_trend(
    code: str,
    trend_type: str,
    size: int | None,
    start: str | None,
    end: str | None,
    normalize_investors: bool = False,
) -> dict[str, Any]:
    if size is not None:
        size = api.require_int_range("size", size, minimum=1, maximum=120)
    result = api.get_result(build_trend_path(code, trend_type, size, start, end))
    payload = {
        "code": api.normalize_product_code(code),
        "type": trend_type,
        "result": result,
    }
    if normalize_investors and trend_type in {"investor", "fixed"}:
        payload["normalizedInvestorRows"] = normalize_investor_result(result)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch TossInvest investor, program, fixed, broker, credit, lending, "
            "short-selling, or CFD trend data."
        )
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    parser.add_argument(
        "--type",
        choices=sorted([*RECENT_TYPES, *FIXED_TYPES, *MDS_INFO_TYPES, "broker"]),
        default="investor",
        help="Trend endpoint to call",
    )
    parser.add_argument("--size", type=int, default=60, help="Rows for recent/paged endpoints")
    parser.add_argument("--from", dest="start", help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="end", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--normalize-investors",
        action="store_true",
        help="Add normalized KR investor net-buy rows for investor/fixed endpoints",
    )
    api.add_json_format_argument(parser)
    parser.add_argument("--output", help="Write JSON output to a file")
    args = parser.parse_args()

    payload = fetch_trading_trend(
        args.code,
        args.type,
        args.size,
        args.start,
        args.end,
        normalize_investors=args.normalize_investors,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
