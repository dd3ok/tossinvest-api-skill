# TossInvest API Skills

Codex skill for exploring and using read-only TossInvest web APIs observed from
[tossinvest.com](https://www.tossinvest.com).

The current skill focuses on stock information workflows: stock summaries,
quotes/ticks, filings, news, financial statements, investor trading trends,
themes/TICS, stock candle charts with local technical-indicator calculation,
market indices, dashboard rankings, feed/news discovery, screener counts, and
RSI/price/technical screener result lookups.

## Install

Ask Codex to install the skill from this public GitHub URL:

```text
Install the skill from https://github.com/dd3ok/tossinvest-api-skills/tree/main/tossinvest-web-api
```

After installation, restart Codex so the new skill is picked up.

Manual install is also possible:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skills.git /tmp/tossinvest-api-skills
cp -R /tmp/tossinvest-api-skills/tossinvest-web-api "${CODEX_HOME:-$HOME/.codex}/skills/tossinvest-web-api"
```

## Quick Prompts

Use prompts like these after installing:

```text
Use $tossinvest-web-api to get a compact stock summary and current quote for A005930.
```

```text
Use $tossinvest-web-api to fetch recent filings and company news for A005930.
```

```text
Use $tossinvest-web-api to compare A005930 investor trading trend from 2026-01-01 through 2026-01-31.
```

```text
Use $tossinvest-web-api to fetch comprehensive financial statement and valuation data for A005930.
```

```text
Use $tossinvest-web-api to fetch KOSPI index price, chart, and market indicators for KGG01P.
```

```text
Use $tossinvest-web-api to inspect TossInvest feed/news discovery APIs from /feed/news.
```

## Direct Script Examples

The skill includes small Python scripts for deterministic lookups:

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/tossinvest-web-api"

python3 scripts/stock_summary.py --code A005930 --no-overview
python3 scripts/quote.py --code A005930 --ticks 5
python3 scripts/stock_chart.py --code A005930 --range day:1 --count 61 --rsi-period 14 --sma-period 20 --ema-period 20 --macd --bollinger-period 20
python3 scripts/filings.py --code A005930 --size 5
python3 scripts/news.py --code A005930 --size 5
python3 scripts/financials.py --code A005930 --kind comprehensive
python3 scripts/trading_trend.py --code A005930 --type fixed --from 2026-01-01 --to 2026-01-31
python3 scripts/theme.py --tag kr --tics-id 289 --include-details --company-ranking marketcap
python3 scripts/indices.py --code KGG01P --include-chart --include-fx-chart --include-exchange-rates --format json
python3 scripts/indices.py --code KGG01P --include-indicators --indicator-type bond
python3 scripts/indices.py --code KGG01P --include-indicators --indicator-type commodity
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart biggest_total_amount --market kr --duration realtime
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart heavy_soar --market us --duration 1d
python3 scripts/dashboard_ranking.py --kind investors --side sell
python3 scripts/feed.py --kind news --news-type HOT
python3 scripts/screener_count.py --nation kr
python3 scripts/screener_count.py --nation kr --rsi oversold --include-results --size 5
python3 scripts/screener_count.py --nation kr --price-filter new-high-52w-within-20d --include-results --sort market-cap --size 5
python3 scripts/screener_count.py --nation kr --price-filter price-change-5d-up-5 --technical-filter price-ma-cross-up --include-results --sort volume --size 5
python3 scripts/screener_count.py --nation kr --technical-filter price-ma-cross-up --include-results --sort market-cap --size 5
python3 scripts/screener_count.py --nation kr --technical-filter bollinger-lower-down --include-results --page 1 --size 5
python3 scripts/screener_count.py --nation kr --filters-file examples/filters/price-momentum-and-ma.json --include-results --sort market-cap --size 5
```

## Safety

This skill is for read-only public-looking web API discovery and lookup.

- Do not use it for order placement, account actions, or trading mutations.
- Do not store cookies, tokens, account numbers, session files, or raw HAR files.
- Stop if a `wts-cert-api` endpoint requires authentication, cookies, account identifiers, or personal data.
- Treat undocumented TossInvest APIs as unstable and re-check current browser traffic before relying on them.

## Skill Contents

- [`tossinvest-web-api/SKILL.md`](tossinvest-web-api/SKILL.md): skill entry point
- [`tossinvest-web-api/references/api-catalog.md`](tossinvest-web-api/references/api-catalog.md): observed endpoint catalog
- [`tossinvest-web-api/references/eval-prompts.md`](tossinvest-web-api/references/eval-prompts.md): manual smoke prompts for skill selection, script routing, and safety refusals
- [`tossinvest-web-api/scripts/`](tossinvest-web-api/scripts): bundled lookup scripts
- [`tossinvest-web-api/examples/filters/`](tossinvest-web-api/examples/filters): example screener filter JSON files for `--filters-file`

Validation tests are kept local and are intentionally not included in the published skill.

## Changelog

### v0.1.8

- Added `--include-fx-chart` to `scripts/indices.py` for the USD/KRW FX r-chart endpoint.

### v0.1.7

- Added `--include-exchange-rates` to `scripts/indices.py` for the public-looking dashboard exchange-rates widget.
- Documented verified bond and commodity dashboard indicator types.
- Added `--format json` aliases to JSON-only lookup scripts.
- Improved skill discovery metadata, OpenAI UI prompt text, and chart/indices help descriptions.

### v0.1.6

- Improved skill discovery metadata for TossInvest/토스증권 unofficial read-only API workflows.
- Added explicit task routing, when-not-to-use boundaries, and manual eval prompts.
