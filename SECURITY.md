# Security Policy

## Scope

This repository catalogs and scripts unofficial, read-only TossInvest web API calls that are visible from public stock and market pages. It is not an official TossInvest, broker, trading, account, or investment-advice API.

## Do Not Share Sensitive Data

Do not include any of the following in GitHub issues, pull requests, discussions, logs, screenshots, or attachments:

- Cookies, authorization headers, tokens, session IDs, or storage-state files
- Ephemeral WebSocket guest values, complete STOMP `CONNECT` or `MESSAGE` frames, and raw WebSocket frame dumps
- Account numbers, balances, holdings, transfers, order data, or personal financial data
- Raw HAR files or full browser network exports
- Any data copied from authenticated TossInvest pages

If a report requires network evidence, provide sanitized endpoint paths, request methods, public page URLs, response shape notes, and the date checked. Remove all headers and user-specific data.

## Reporting Concerns

Open a GitHub issue for public-read-only endpoint drift, stale documentation, unsafe examples, or scripts that accidentally reach outside the documented safety scope.

If you discover a privacy, credential-handling, account-data, or order/trading safety issue, do not post sensitive details publicly. Use GitHub Private Vulnerability Reporting for this repository:

https://github.com/dd3ok/tossinvest-api-skill/security/advisories/new

If private vulnerability reporting is unavailable, open only a minimal public issue asking for a private contact path. Do not include endpoint payloads, cookies, tokens, raw HAR files, account data, screenshots of authenticated pages, or personal financial data.

## Project Safety Rules

- Do not add login, authentication, certificate mutation, account, holding, balance, transfer, order placement, order amendment, order cancellation, or orderable-amount endpoints.
- Do not add rate limit bypass, anti-bot bypass, bulk scraping, or access-control workaround behavior.
- Do not add high-frequency polling, unbounded concurrent fan-out, large batch scraping, or automatic retries after HTTP 403/429, challenge pages, login redirects, or other access-control failures.
- A standalone public read-only WebSocket client may use the anonymous browser guest bootstrap in memory only. It must not accept guest values from users, persist or log them, dump raw frames, or connect any market-data subscription to order, account, holding, or balance workflows.
- A top100 client is limited to one shared connection and at most 100 deduplicated product destinations for one ranking view at a time. Reconnects require bounded backoff, jitter, and a maximum retry count.
- Treat `wts-cert-api.tossinvest.com` as sensitive unless an endpoint is clearly public page metadata and works without cookies or authorization.
- Re-verify undocumented endpoints against current public browser traffic before changing scripts or catalog status.
