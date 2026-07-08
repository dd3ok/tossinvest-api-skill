# Official Open API Boundary

Checked: 2026-07-08

Sources:

- `https://developers.tossinvest.com/docs`
- `https://developers.tossinvest.com/llms.txt`
- `https://openapi.tossinvest.com/openapi-docs/overview.md`
- `https://openapi.tossinvest.com/openapi-docs/latest/openapi.json`

Use this reference only to distinguish this skill from the official TossInvest
Open API or to answer a rate-limit question about the official API. Treat the
official limits as reference-only operational context, not as permission to set
traffic levels for this unauthenticated web-endpoint skill. Do not use this file
to add OAuth, account, asset, or order workflows to this skill.

## Boundary

This skill works with public TossInvest web pages and observed unauthenticated
page-data endpoints. It is not a client for the official Open API service at
`https://openapi.tossinvest.com`.

Because this skill does not call the official Open API, it does not need official
Open API app setup, OAuth credentials, `X-Tossinvest-Account`, or IP registration.
Do not ask users for those values for this skill, and do not add scripts that
handle them here.

If the user wants official Open API integration, treat it as a separate
authenticated client project and read the official docs directly.

## Official API Shape

Official OpenAPI JSON checked on 2026-07-08:

- OpenAPI version: `1.2.2`
- Base server: `https://openapi.tossinvest.com`
- Auth: OAuth 2.0 Client Credentials via `POST /oauth2/token`
- All official API calls use `Authorization: Bearer {access_token}`
- Account, asset, and order APIs also require `X-Tossinvest-Account`
- Coverage: Auth, Market Data, Stock Info, Market Info, Ranking, Market
  Indicators, Account, Asset, Order, Conditional Order, Conditional Order
  History, Order History, and Order Info

`llms.txt` mentions JWKS in its quick Auth summary, but the canonical OpenAPI
JSON checked on 2026-07-08 did not list a JWKS operation. Use the OpenAPI JSON as
the source of truth for exact official paths.

Official market-data overlap includes:

- `GET /api/v1/orderbook`
- `GET /api/v1/prices`
- `GET /api/v1/trades`
- `GET /api/v1/price-limits`
- `GET /api/v1/candles`
- `GET /api/v1/stocks`
- `GET /api/v1/stocks/{symbol}/warnings`
- `GET /api/v1/exchange-rate`
- `GET /api/v1/market-calendar/KR`
- `GET /api/v1/market-calendar/US`

This overlap does not make the official paths script-backed in this repository.
The bundled scripts continue to use the public page endpoint catalog.

Official public market-data READ endpoints present in `1.2.2` but not yet
script-backed in this skill:

- `GET /api/v1/rankings`
- `GET /api/v1/market-indicators/prices`
- `GET /api/v1/market-indicators/{symbol}/candles`
- `GET /api/v1/market-indicators/{symbol}/investor-trading`

Authenticated official-only READ endpoints must remain reference-only here:

- `GET /api/v1/accounts`
- `GET /api/v1/holdings`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{orderId}`
- `GET /api/v1/conditional-orders`
- `GET /api/v1/conditional-orders/{conditionalOrderId}`
- `GET /api/v1/buying-power`
- `GET /api/v1/sellable-quantity`
- `GET /api/v1/commissions`

These are authenticated official-only workflows because they require OAuth and,
for account, asset, and order information, `X-Tossinvest-Account`. Do not add
unauthenticated web-endpoint scripts for these operations.

## Official Rate Limits

The official docs describe rate limits as client x API group TPS limits. Values
can change without prior notice, and current limits should be checked from the
official response headers before making exact operational claims. These official
TPS values are not a throughput allowance for this skill, because this skill does
not call the official Open API and the public web endpoints do not publish a
separate quota.

| Official group | Limit in docs |
| --- | --- |
| `AUTH` | 5 TPS |
| `ACCOUNT` | 1 TPS |
| `ASSET` | 5 TPS |
| `STOCK` | 5 TPS |
| `MARKET_INFO` | 3 TPS |
| `MARKET_DATA` | 10 TPS |
| `MARKET_DATA_CHART` | 5 TPS |
| `RANKING` | 3 TPS |
| `MARKET_INDICATOR_PRICE` | 10 TPS |
| `MARKET_INDICATOR` | 3 TPS |
| `MARKET_INDICATOR_CHART` | 5 TPS |
| `ORDER` | 6 TPS; 3 TPS during 09:00-09:10 KST |
| `CONDITIONAL_ORDER` | 5 TPS |
| `CONDITIONAL_ORDER_HISTORY` | 5 TPS |
| `ORDER_HISTORY` | 5 TPS |
| `ORDER_INFO` | 6 TPS; 3 TPS during 09:00-09:10 KST |

Official normal and 429 responses include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After` on 429 responses

For this skill, keep the stricter safety rule: stop on 403, 429, login redirects,
challenge pages, or abnormal responses; do not retry, poll, fan out, or bypass
service protection; do not probe unpublished limits, including by testing higher
TPS than the official Open API documents.
