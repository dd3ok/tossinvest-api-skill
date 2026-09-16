#!/usr/bin/env python3
"""Fetch read-only TossInvest trading trend endpoints."""

from __future__ import annotations

import argparse
import re
from datetime import date
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
    "margin-loan": "margin-loan",
    "securities-landing": "securities-landing",
    "lending-trading": "lending-trading",
    "short-selling-trend": "short-selling-trend",
    "cfd": "cfd",
}
_PAGING_KEY_RE = re.compile(r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$")

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

INTRADAY_INVESTOR_GROUPS = (
    (
        "netInsuranceOtherBuyVolume",
        "금융투자·보험·기타금융",
        ("financial_investment", "insurance", "other_financial"),
        "net",
    ),
    (
        "trustAndPrivateEquityFundBuyVolume",
        "투신·사모펀드",
        ("trust", "private_equity_fund"),
        "unspecified",
    ),
)
_INTRADAY_GROUP_FIELDS = {
    investor_type: field
    for field, _, investor_types, _ in INTRADAY_INVESTOR_GROUPS
    for investor_type in investor_types
}


def _investor_metadata(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": row.get("baseDate") or row.get("date") or row.get("tradeDate"),
        **{
            field: row.get(field)
            for field in (
                "hasIndividual",
                "hasForeigner",
                "hasInstitution",
                "inMarketTime",
                "updatedAt",
            )
        },
    }


def _has_investor_data(row: dict[str, Any], field: str, flag: str) -> bool | None:
    if row.get(field) is None:
        return False
    available = row.get(flag)
    return available if isinstance(available, bool) else None


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
        for investor_type, label_ko, field_name in INVESTOR_NET_FIELDS:
            if field_name not in row:
                continue
            availability_flag = {
                "individual": "hasIndividual",
                "foreigner": "hasForeigner",
            }.get(investor_type, "hasInstitution")
            group_field = (
                _INTRADAY_GROUP_FIELDS.get(investor_type)
                if row.get("inMarketTime") is True
                else None
            )
            has_data = (
                False
                if group_field is not None
                else _has_investor_data(row, field_name, availability_flag)
            )
            normalized.append(
                {
                    **_investor_metadata(row),
                    "investorType": investor_type,
                    "labelKo": label_ko,
                    "field": field_name,
                    "netBuyVolume": None if has_data is False else row.get(field_name),
                    "hasData": has_data,
                    "dataGrouping": "intraday-group" if group_field is not None else "category",
                    **({"groupField": group_field} if group_field is not None else {}),
                }
            )
    return normalized


def normalize_investor_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for row in rows:
        if row.get("inMarketTime") is not True:
            continue
        for field, label_ko, investor_types, value_kind in INTRADAY_INVESTOR_GROUPS:
            if field not in row:
                continue
            has_data = _has_investor_data(row, field, "hasInstitution")
            groups.append(
                {
                    **_investor_metadata(row),
                    "labelKo": label_ko,
                    "investorTypes": list(investor_types),
                    "sourceField": field,
                    "value": None if has_data is False else row.get(field),
                    "valueKind": value_kind,
                    "hasData": has_data,
                }
            )
    return groups


def normalize_investor_result(result: Any) -> list[dict[str, Any]]:
    return normalize_investor_rows(_rows_from_result(result))


def build_trend_path(
    code: str,
    trend_type: str,
    size: int | None,
    start: str | None,
    end: str | None,
    page: int = 1,
    key: str | None = None,
) -> str:
    product_code = api.normalize_product_code(code)
    if trend_type in RECENT_TYPES:
        page = _validate_paging(page, key)
        return api.build_path(
            f"/api/v1/stock-infos/trade/trend/{RECENT_TYPES[trend_type]}",
            {
                "productCode": product_code,
                "size": size,
                "number": page if page != 1 or key is not None else None,
                "key": key,
            },
        )
    if trend_type not in MDS_INFO_TYPES and (page != 1 or key is not None):
        raise ValueError(
            "--page and --key are supported only for recent investor/program or MDS data"
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
        return build_mds_info_path(product_code, trend_type, size, page, key)
    raise ValueError(f"unknown trend type: {trend_type}")


def _validate_paging(page: int, key: str | None) -> int:
    page = api.require_int_range("page", page, minimum=1, maximum=1000)
    if key is not None:
        if not isinstance(key, str) or not _PAGING_KEY_RE.fullmatch(key):
            raise ValueError("key must be a YYYY-MM-DD paging key")
        try:
            date.fromisoformat(key)
        except ValueError as exc:
            raise ValueError("key must be a YYYY-MM-DD paging key") from exc
    return page


def build_mds_info_path(
    code: str,
    mds_type: str,
    size: int | None,
    page: int = 1,
    key: str | None = None,
) -> str:
    product_code = api.normalize_product_code(code)
    if mds_type not in MDS_INFO_TYPES:
        raise ValueError(f"unknown mds info type: {mds_type}")
    page = _validate_paging(page, key)
    return api.build_path(
        f"/api/v1/mds/info/{MDS_INFO_TYPES[mds_type]}",
        {"stockCode": product_code, "number": page, "size": size, "key": key},
    )


def fetch_trading_trend(
    code: str,
    trend_type: str,
    size: int | None,
    start: str | None,
    end: str | None,
    normalize_investors: bool = False,
    page: int = 1,
    key: str | None = None,
) -> dict[str, Any]:
    if size is not None:
        size = api.require_int_range("size", size, minimum=1, maximum=120)
    result = api.get_result(build_trend_path(code, trend_type, size, start, end, page, key))
    payload = {
        "code": api.normalize_product_code(code),
        "type": trend_type,
        "request": {
            "size": size,
            "from": start,
            "to": end,
            **(
                {"page": page, "key": key}
                if trend_type in RECENT_TYPES or trend_type in MDS_INFO_TYPES
                else {}
            ),
        },
        "result": result,
    }
    if normalize_investors and trend_type in {"investor", "fixed"}:
        payload["normalizedInvestorRows"] = normalize_investor_result(result)
        payload["normalizedInvestorGroups"] = normalize_investor_groups(_rows_from_result(result))
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
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number for recent investor/program or MDS credit/lending/short-selling/CFD",
    )
    parser.add_argument(
        "--key",
        help="YYYY-MM-DD paging key from the previous response pagingParam",
    )
    parser.add_argument("--from", dest="start", help="Start date YYYY-MM-DD")
    parser.add_argument("--to", dest="end", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--normalize-investors",
        action="store_true",
        help="Add KR investor net-buy rows with availability metadata and separate intraday groups",
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
        page=args.page,
        key=args.key,
    )
    api.emit_output(api.render_json(payload), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(api.run_cli(main))
