# TossInvest API Skills

Codex skill for exploring and using read-only TossInvest web APIs observed from
[tossinvest.com](https://www.tossinvest.com).

The current skill focuses on stock information workflows: stock summaries,
quotes/ticks, filings, news, financial statements, investor trading trends,
themes/TICS, market indices, dashboard rankings, feed/news discovery, and
screener counts.

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
python3 scripts/filings.py --code A005930 --size 5
python3 scripts/news.py --code A005930 --size 5
python3 scripts/financials.py --code A005930 --kind comprehensive
python3 scripts/trading_trend.py --code A005930 --type fixed --from 2026-01-01 --to 2026-01-31
python3 scripts/theme.py --tag kr --tics-id 289 --include-details --company-ranking marketcap
python3 scripts/indices.py --code KGG01P --include-chart
python3 scripts/dashboard_ranking.py --kind investors --side sell
python3 scripts/feed.py --kind news --news-type HOT
python3 scripts/screener_count.py --nation kr
```

## Safety

This skill is for read-only public-looking web API discovery and lookup.

- Do not use it for order placement, account actions, or trading mutations.
- Do not store cookies, tokens, account numbers, session files, or raw HAR files.
- Treat undocumented TossInvest APIs as unstable and re-check current browser traffic before relying on them.

## Skill Contents

- [`tossinvest-web-api/SKILL.md`](tossinvest-web-api/SKILL.md): skill entry point
- [`tossinvest-web-api/references/api-catalog.md`](tossinvest-web-api/references/api-catalog.md): observed endpoint catalog
- [`tossinvest-web-api/scripts/`](tossinvest-web-api/scripts): bundled lookup scripts

Validation tests are kept local and are intentionally not included in the published skill.
