---
name: tossinvest-web-api
description: Use when investigating or using TossInvest web internal read-only APIs from tossinvest.com pages, including stock detail, quote/tick data, chart, analytics, investor trading trend, broker trading ranking, filings, themes/TICS, screener counts, financial statements, consensus, dividend, market indices, dashboard rankings, feed/news discovery, and network-capture based endpoint cataloging.
---

# TossInvest Web API

## Overview

Use this skill to inspect TossInvest web pages and work with read-only internal API endpoints observed from browser network traffic. Do not use `tossctl` or `tossinvest-cli`.

## Workflow

1. Identify the target TossInvest page and stock code.
2. Capture browser network requests or inspect bundled JavaScript.
3. Classify endpoints by host and data domain.
4. Prefer `wts-info-api.tossinvest.com` read-only endpoints.
5. Read [references/api-catalog.md](references/api-catalog.md) for known endpoint patterns.
6. Read [references/capture-workflow.md](references/capture-workflow.md) when adding new endpoints.
7. Read [references/safety-rules.md](references/safety-rules.md) before handling HAR files, cookies, account data, authenticated APIs, or order-related endpoints.
8. For pension-fund investor trend checks, prefer `netPensionFundBuyVolume`; use `pensionFundBuyVolume` only as a reference gross-buy field unless re-verified against the current UI.

## Bundled Scripts

- `scripts/stock_summary.py`: Fetches stock metadata, price detail, and optional overview for a product code.
- `scripts/quote.py`: Fetches quote-book data from v3 quotes and optional intraday ticks.
- `scripts/stock_chart.py`: Fetches c-chart candle data and can add locally calculated RSI, SMA, EMA, MACD, and Bollinger Bands from close prices.
- `scripts/filings.py`: Fetches company filing lists; supports JSON or CSV output.
- `scripts/news.py`: Fetches company news lists and optional news detail payloads.
- `scripts/financials.py`: Fetches financial statement, estimate, valuation, stability, revenue/net-profit, and operating-income endpoints.
- `scripts/trading_trend.py`: Fetches investor, program, fixed-window, accumulated, broker-ranking, and credit trend endpoints.
- `scripts/theme.py`: Fetches theme/TICS rankings and optional related themes, news, and fluctuation data.
- `scripts/indices.py`: Fetches market index info, price, optional chart, and indicator lists.
- `scripts/dashboard_ranking.py`: Fetches dashboard overview rankings, home live-chart top100 rankings, and domestic investor buy/sell ranking widgets.
- `scripts/feed.py`: Fetches recommended feed payloads and dashboard news categories.
- `scripts/screener_count.py`: Fetches public-looking screener result counts for `kr` or `us`, with optional RSI, price-condition, and technical-analysis filter presets plus paged/sorted results; uses `wts-cert-api`, so keep sensitive-host caution.
- `scripts/pension_fund_trend.py`: Fetches pension-fund net-buy history from `fixed-trading-trend`; supports `--from/--to`, `--year`, `--all-history`, JSON/CSV output, `--output`, summary metadata, and optional reference gross-buy values from recent `trading-trend` rows.

## Script Examples

```bash
python3 scripts/stock_summary.py --code A005930
python3 scripts/quote.py --code A005930 --ticks 5
python3 scripts/stock_chart.py --code A005930 --range day:1 --count 61 --rsi-period 14 --sma-period 20 --ema-period 20 --macd --bollinger-period 20
python3 scripts/filings.py --code A005930 --size 5
python3 scripts/news.py --code A005930 --size 5
python3 scripts/financials.py --code A005930 --kind comprehensive
python3 scripts/trading_trend.py --code A005930 --type fixed --from 2026-01-01 --to 2026-01-31
python3 scripts/theme.py --tag kr --tics-id 289 --include-details --company-ranking marketcap
python3 scripts/indices.py --code KGG01P --include-chart
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart biggest_total_amount --market kr --duration realtime
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart heavy_soar --market us --duration 1d
python3 scripts/dashboard_ranking.py --kind investors --side sell
python3 scripts/feed.py --kind news --news-type HOT
python3 scripts/screener_count.py --nation kr
python3 scripts/screener_count.py --nation kr --rsi oversold --include-results --size 5
python3 scripts/screener_count.py --nation kr --price-filter new-high-52w-within-20d --include-results --sort market-cap --size 5
python3 scripts/screener_count.py --nation kr --price-filter price-change-5d-up-5 --technical-filter price-ma-cross-up --include-results --sort volume --size 5
python3 scripts/screener_count.py --nation kr --technical-filter price-ma-cross-up --include-results --sort market-cap --size 5
python3 scripts/screener_count.py --nation kr --technical-filter volume-ma-cross-up --technical-filter bollinger-lower-down --include-results --sort volume --page 1 --size 5
python3 scripts/screener_count.py --nation kr --filters-file examples/filters/new-high-momentum.json --include-results --sort market-cap --size 5
python3 scripts/pension_fund_trend.py --code A005930 --year 2026 --summary-only
```

## Usage Prompts

Use prompts like these after installing the skill:

- `Use $tossinvest-web-api to get a compact stock summary and current quote for A005930.`
- `Use $tossinvest-web-api to fetch daily candles and calculate RSI 14, MACD, and Bollinger Bands for A005930.`
- `Use $tossinvest-web-api to fetch recent filings and company news for A005930.`
- `Use $tossinvest-web-api to compare A005930 investor trading trend from 2026-01-01 through 2026-01-31.`
- `Use $tossinvest-web-api to fetch comprehensive financial statement and valuation data for A005930.`
- `Use $tossinvest-web-api to fetch KOSPI index price, chart, and index-related news for KGG01P.`
- `Use $tossinvest-web-api to fetch domestic and US top100 live-chart rankings by trading amount, volume, surge, and decline.`
- `Use $tossinvest-web-api to find Korean stocks where TossInvest screener RSI is oversold.`
- `Use $tossinvest-web-api to find Korean stocks where price crosses above the 20-day moving average.`
- `Use $tossinvest-web-api to find Korean stocks near a 52-week high with recent price momentum.`
- `Use $tossinvest-web-api to inspect TossInvest feed/news discovery APIs from /feed/news.`
- `Use $tossinvest-web-api to inspect TossInvest network calls for undocumented read-only stock-page endpoints.`

Prefer bundled scripts for direct lookups. Re-read [references/safety-rules.md](references/safety-rules.md) before any task involving cookies, account data, HAR files, authenticated APIs, or `wts-cert-api`.

Use [examples/filters](examples/filters) as starting JSON bodies for `--filters-file` when combining multiple screener filters.

## Hard Rules

- Never use, install, or run `tossctl`.
- Never use, install, or run `tossinvest-cli`.
- Never call trading mutation APIs.
- Do not describe TradingView chart studies such as RSI/MACD/Bollinger as TossInvest API fields unless a current endpoint is verified; chart studies are displayed by TradingView client logic over `c-chart` candles, and `stock_chart.py` calculates supported indicators locally.
- Never store raw cookies, tokens, account numbers, session files, storage state, or raw HAR captures.
- Treat undocumented APIs as unstable and re-verify them with current browser traffic.
