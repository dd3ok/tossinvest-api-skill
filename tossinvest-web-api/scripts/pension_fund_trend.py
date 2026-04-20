#!/usr/bin/env python3
"""Fetch TossInvest pension-fund net-buy history for a stock code.

This script uses only read-only public web API endpoints observed from
tossinvest.com pages. The API is undocumented and may change.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


BASE_URL = "https://wts-info-api.tossinvest.com"
DEFAULT_HISTORY_START = "2019-04-01"


def request_json(path: str) -> dict:
    req = urllib.request.Request(
        BASE_URL + path,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.tossinvest.com",
            "Referer": "https://www.tossinvest.com/",
            "User-Agent": "Mozilla/5.0 tossinvest-web-api-skill/1.0",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fixed_trend(product_code: str, start: str, end: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {"productCode": product_code, "from": start, "to": end}
    )
    payload = request_json(
        f"/api/v1/stock-infos/trade/trend/fixed-trading-trend?{query}"
    )
    result = payload.get("result")
    if not isinstance(result, list):
        raise RuntimeError("Unexpected fixed-trading-trend response shape")
    return result


def year_window(year: int) -> tuple[str, str]:
    return f"{year:04d}-01-01", f"{year:04d}-12-31"


def year_windows(start: str, end: str) -> list[tuple[str, str]]:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if start_date > end_date:
        raise ValueError("start date must be before or equal to end date")

    windows = []
    current_year = start_date.year
    while current_year <= end_date.year:
        window_start = max(start_date, date(current_year, 1, 1))
        window_end = min(end_date, date(current_year, 12, 31))
        windows.append((window_start.isoformat(), window_end.isoformat()))
        current_year += 1
    return windows


def fetch_history(
    product_code: str, start: str, end: str, chunk_yearly: bool
) -> list[dict]:
    ranges = year_windows(start, end) if chunk_yearly else [(start, end)]
    rows_by_date = {}
    for window_start, window_end in ranges:
        for row in fixed_trend(product_code, window_start, window_end):
            base_date = row.get("baseDate")
            if base_date:
                rows_by_date[base_date] = row
    return [rows_by_date[key] for key in sorted(rows_by_date, reverse=True)]


def recent_gross_buy(product_code: str, size: int) -> dict[str, int | None]:
    query = urllib.parse.urlencode({"productCode": product_code, "size": size})
    payload = request_json(
        f"/api/v1/stock-infos/trade/trend/trading-trend?{query}"
    )
    result = payload.get("result")
    rows = result.get("body") if isinstance(result, dict) else None
    if not isinstance(rows, list):
        raise RuntimeError("Unexpected trading-trend response shape")
    return {
        row.get("baseDate"): row.get("pensionFundBuyVolume")
        for row in rows
        if row.get("baseDate")
    }


def normalize_rows(
    rows: list[dict], gross_by_date: dict[str, int | None] | None
) -> list[dict]:
    output = []
    for row in rows:
        net = row.get("netPensionFundBuyVolume")
        if (net or 0) > 0:
            direction = "NET_BUY"
        elif (net or 0) < 0:
            direction = "NET_SELL"
        else:
            direction = "FLAT"
        item = {
            "date": row.get("baseDate"),
            "netPensionFundBuyVolume": net,
            "direction": direction,
        }
        if gross_by_date is not None:
            item["pensionFundBuyVolumeReference"] = gross_by_date.get(
                row.get("baseDate")
            )
        output.append(item)
    return output


def summarize_rows(rows: list[dict]) -> dict:
    net_values = [row.get("netPensionFundBuyVolume") or 0 for row in rows]
    return {
        "rowCount": len(rows),
        "totalNetPensionFundBuyVolume": sum(net_values),
        "netBuyDays": sum(1 for value in net_values if value > 0),
        "netSellDays": sum(1 for value in net_values if value < 0),
        "flatDays": sum(1 for value in net_values if value == 0),
    }


def render_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def emit_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    else:
        print(text, end="" if text.endswith("\n") else "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch TossInvest pension-fund net-buy history."
    )
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument("--year", type=int, help="Calendar year to fetch")
    date_group.add_argument(
        "--all-history",
        action="store_true",
        help=f"Fetch yearly windows from {DEFAULT_HISTORY_START}",
    )
    date_group.add_argument(
        "--from", dest="start", help="Start date YYYY-MM-DD; requires --to"
    )
    parser.add_argument("--to", dest="end", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--history-start",
        default=DEFAULT_HISTORY_START,
        help="Start date used with --all-history",
    )
    parser.add_argument(
        "--include-gross-reference",
        action="store_true",
        help="Include recent pensionFundBuyVolume reference values when available",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format",
    )
    parser.add_argument("--output", help="Write output to a file instead of stdout")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Include summary metadata; JSON output only",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only summary metadata; JSON output only",
    )
    args = parser.parse_args()

    if (args.summary or args.summary_only) and args.format != "json":
        parser.error("--summary and --summary-only require --format json")

    if args.year is not None:
        start, end = year_window(args.year)
        chunk_yearly = False
    elif args.all_history:
        start, end = args.history_start, date.today().isoformat()
        chunk_yearly = True
    else:
        if not args.end:
            parser.error("--from requires --to")
        start, end = args.start, args.end
        chunk_yearly = False

    rows = fetch_history(args.code, start, end, chunk_yearly)
    gross = (
        recent_gross_buy(args.code, min(max(len(rows), 1), 120))
        if args.include_gross_reference
        else None
    )
    normalized = normalize_rows(rows, gross)
    summary = {
        "code": args.code,
        "from": start,
        "to": end,
        **summarize_rows(normalized),
    }

    if args.summary_only:
        payload = summary
    elif args.summary:
        payload = {"summary": summary, "rows": normalized}
    else:
        payload = normalized

    if args.format == "csv":
        text = render_csv(normalized)
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    emit_output(text, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
