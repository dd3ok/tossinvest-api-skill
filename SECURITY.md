# Security Policy

## Scope

This repository catalogs and scripts unofficial, read-only TossInvest web API calls that are visible from public stock and market pages. It is not an official TossInvest, broker, trading, account, or investment-advice API.

## Do Not Share Sensitive Data

Do not include any of the following in GitHub issues, pull requests, discussions, logs, screenshots, or attachments:

- Cookies, authorization headers, tokens, session IDs, or storage-state files
- Account numbers, balances, holdings, transfers, order data, or personal financial data
- Raw HAR files or full browser network exports
- Any data copied from authenticated TossInvest pages

If a report requires network evidence, provide sanitized endpoint paths, request methods, public page URLs, response shape notes, and the date checked. Remove all headers and user-specific data.

## Reporting Concerns

Open a GitHub issue for public-read-only endpoint drift, stale documentation, unsafe examples, or scripts that accidentally reach outside the documented safety scope.

If you discover a privacy, credential-handling, account-data, or order/trading safety issue, do not post sensitive details publicly. Open a minimal issue saying that a sensitive report is available, or contact the maintainer through the GitHub profile associated with this repository.

## Project Safety Rules

- Do not add login, authentication, certificate mutation, account, holding, balance, transfer, order placement, order amendment, order cancellation, or orderable-amount endpoints.
- Do not add rate-limit bypass, anti-bot bypass, bulk scraping, or access-control workaround behavior.
- Treat `wts-cert-api.tossinvest.com` as sensitive unless an endpoint is clearly public page metadata and works without cookies or authorization.
- Re-verify undocumented endpoints against current public browser traffic before changing scripts or catalog status.
