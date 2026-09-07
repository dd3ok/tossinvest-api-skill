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
from datetime import date
from pathlib import Path

import tossinvest_api as api

DEFAULT_HISTORY_START = "2019-04-01"
MAX_HISTORY_YEARS = 20


def normalize_date(name: str, value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a valid YYYY-MM-DD date") from exc


def normalize_date_range(start: str, end: str) -> tuple[str, str]:
    normalized_start = normalize_date("from", start)
    normalized_end = normalize_date("to", end)
    if normalized_start > normalized_end:
        raise ValueError("start date must be before or equal to end date")
    return normalized_start, normalized_end


def fixed_trend(product_code: str, start: str, end: str) -> list[dict]:
    start, end = normalize_date_range(start, end)
    path = api.build_path(
        "/api/v1/stock-infos/trade/trend/fixed-trading-trend",
        {
            "productCode": api.normalize_product_code(product_code),
            "from": start,
            "to": end,
        },
    )
    payload = api.request_json(path)
    result = payload.get("result")
    if not isinstance(result, list):
        raise RuntimeError("Unexpected fixed-trading-trend response shape")
    return result


def year_window(year: int) -> tuple[str, str]:
    if year < 1 or year > 9999:
        raise ValueError("year must be between 1 and 9999")
    return f"{year:04d}-01-01", f"{year:04d}-12-31"


def year_windows(start: str, end: str) -> list[tuple[str, str]]:
    start, end = normalize_date_range(start, end)
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if end_date.year - start_date.year + 1 > MAX_HISTORY_YEARS:
        raise ValueError(f"history must span at most {MAX_HISTORY_YEARS} calendar years")

    windows = []
    current_year = start_date.year
    while current_year <= end_date.year:
        window_start = max(start_date, date(current_year, 1, 1))
        window_end = min(end_date, date(current_year, 12, 31))
        windows.append((window_start.isoformat(), window_end.isoformat()))
        current_year += 1
    return windows


def fetch_history(product_code: str, start: str, end: str, chunk_yearly: bool) -> list[dict]:
    validated_windows = year_windows(start, end)
    ranges = (
        validated_windows if chunk_yearly else [(validated_windows[0][0], validated_windows[-1][1])]
    )
    rows_by_date = {}
    for window_start, window_end in ranges:
        for row in fixed_trend(product_code, window_start, window_end):
            base_date = row.get("baseDate")
            if base_date:
                rows_by_date[base_date] = row
    return [rows_by_date[key] for key in sorted(rows_by_date, reverse=True)]


def normalize_rows(rows: list[dict]) -> list[dict]:
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
    parser = argparse.ArgumentParser(description="Fetch TossInvest pension-fund net-buy history.")
    parser.add_argument("--code", default="A005930", help="TossInvest product code")
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument("--year", type=int, help="Calendar year to fetch")
    date_group.add_argument(
        "--all-history",
        action="store_true",
        help=f"Fetch yearly windows from {DEFAULT_HISTORY_START}",
    )
    date_group.add_argument("--from", dest="start", help="Start date YYYY-MM-DD; requires --to")
    parser.add_argument("--to", dest="end", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--history-start",
        default=DEFAULT_HISTORY_START,
        help="Start date used with --all-history",
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

    normalized_code = api.normalize_product_code(args.code)
    rows = fetch_history(normalized_code, start, end, chunk_yearly)
    normalized = normalize_rows(rows)
    summary = {
        "code": normalized_code,
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
    raise SystemExit(api.run_cli(main))
