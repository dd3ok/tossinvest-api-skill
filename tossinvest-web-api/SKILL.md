---
name: tossinvest-web-api
description: Use when investigating or using TossInvest web internal read-only APIs from tossinvest.com pages, including stock detail, chart, analytics, investor trading trend, broker trading ranking, financial statements, consensus, dividend, and network-capture based endpoint cataloging.
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

- `scripts/pension_fund_trend.py`: Fetches pension-fund net-buy history from `fixed-trading-trend`; supports `--from/--to`, `--year`, `--all-history`, JSON/CSV output, `--output`, summary metadata, and optional reference gross-buy values from recent `trading-trend` rows.

## Hard Rules

- Never use, install, or run `tossctl`.
- Never use, install, or run `tossinvest-cli`.
- Never call trading mutation APIs.
- Never store raw cookies, tokens, account numbers, session files, storage state, or raw HAR captures.
- Treat undocumented APIs as unstable and re-verify them with current browser traffic.
