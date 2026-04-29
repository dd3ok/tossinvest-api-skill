# Script Cookbook

Use this cookbook when `SKILL.md` has selected the right script family but the task needs a more specific command. These recipes are read-only lookup examples; run `python3 scripts/<name>.py --help` for the complete current options.

## Contents

- [Stock Detail](#stock-detail)
- [Charts And Local Indicators](#charts-and-local-indicators)
- [Financials And Investor Trend](#financials-and-investor-trend)
- [Themes And TICS](#themes-and-tics)
- [Indices, FX, And Indicators](#indices-fx-and-indicators)
- [Rankings And Feed](#rankings-and-feed)
- [Screener](#screener)
- [Pension Fund Trend](#pension-fund-trend)
- [Page API Smoke Checks](#page-api-smoke-checks)

## Stock Detail

```bash
python3 scripts/stock_summary.py --code A005930 --no-overview
python3 scripts/stock_summary.py --code A005930
python3 scripts/quote.py --code A005930 --ticks 5
python3 scripts/filings.py --code A005930 --size 5
python3 scripts/news.py --code A005930 --size 5
```

## Charts And Local Indicators

`stock_chart.py` fetches `c-chart` candles and calculates supported studies locally from candle close prices. Do not describe RSI, MACD, SMA, EMA, or Bollinger values from this script as direct TossInvest API fields.

```bash
python3 scripts/stock_chart.py --code A005930 --range day:1 --count 61 --rsi-period 14 --sma-period 20 --ema-period 20 --macd --bollinger-period 20
python3 scripts/stock_chart.py --code A005930 --range min:1 --count 30
python3 scripts/stock_chart.py --code A005930 --range week:1 --count 52 --rsi-period 14
python3 scripts/stock_chart.py --code AMX0250122009 --securities-type us-s --range day:1 --count 20
```

Use `day:1` or `min:1` for US product candles unless a current browser capture
shows another accepted range. Do not use `1D`, `1H`, or `hour:1` as aliases.

## Financials And Investor Trend

```bash
python3 scripts/financials.py --code A005930 --kind comprehensive
python3 scripts/financials.py --code A005930 --kind valuation
python3 scripts/trading_trend.py --code A005930 --type fixed --from 2026-01-01 --to 2026-01-31
python3 scripts/trading_trend.py --code A005930 --type investor --size 20
python3 scripts/trading_trend.py --code A005930 --type fixed --from 2026-04-24 --to 2026-04-24 --normalize-investors
python3 scripts/trading_trend.py --code A005930 --type broker
```

## Themes And TICS

```bash
python3 scripts/theme.py --tag kr --tics-id 289 --include-details --company-ranking marketcap
python3 scripts/theme.py --tag kr --tics-id 289 --news-size 5
python3 scripts/theme.py --tag kr --tics-id 289
```

When `--tics-id` is set, `theme.py` fetches related themes, theme news, and
fluctuation data. Use `--include-details` and `--company-ranking` for the
additional detail and company-ranking endpoints.

## Indices, FX, And Indicators

```bash
python3 scripts/indices.py --code KGG01P --include-chart --include-fx-chart --include-exchange-rates --format json
python3 scripts/indices.py --code KGG01P --include-mini-chart --include-related-etfs --include-net-buying --net-buying-from 2026-04-20
python3 scripts/indices.py --code KGG01P --include-indicators --indicator-type bond
python3 scripts/indices.py --code KGG01P --include-indicators --indicator-type commodity
python3 scripts/indices.py --code RFU.GCv1 --include-chart --chart-preset daily
python3 scripts/indices.py --code KR1BENCH0010 --include-chart --chart-preset quarter
```

Preserve case-sensitive dotted indicator codes such as `RFU.GCv1`. The default `--securities-type auto` behavior infers dotted codes as `us-s` and non-dotted codes as `kr-s`.

## Rankings And Feed

```bash
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart biggest_total_amount --market kr --duration realtime
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart heavy_soar --market us --duration 1d
python3 scripts/dashboard_ranking.py --kind investors --side sell
python3 scripts/feed.py --kind news --news-type HOT
python3 scripts/feed.py --kind recommended
```

## Screener

`screener_count.py` uses public-looking `wts-cert-api` screener endpoints. Keep the sensitive-host rules: no cookies, auth headers, account identifiers, or personal data.

```bash
python3 scripts/screener_count.py --nation kr
python3 scripts/screener_count.py --nation kr --rsi oversold --include-results --size 5
python3 scripts/screener_count.py --nation kr --include-common-presets --include-search-modal
python3 scripts/screener_count.py --nation kr --price-filter new-high-52w-within-20d --include-results --sort market-cap --size 5
python3 scripts/screener_count.py --nation kr --price-filter price-change-5d-up-5 --technical-filter price-ma-cross-up --include-results --sort volume --size 5
python3 scripts/screener_count.py --nation kr --price-filter new-low-52w-within-20d --technical-filter bollinger-lower-down --include-results --sort volume --size 5
python3 scripts/screener_count.py --nation kr --technical-filter price-ma-cross-up --include-results --sort market-cap --size 5
python3 scripts/screener_count.py --nation kr --technical-filter volume-ma-cross-up --technical-filter bollinger-lower-down --include-results --sort volume --page 1 --size 5
python3 scripts/screener_count.py --nation kr --filters-file examples/filters/new-high-momentum.json --include-results --sort market-cap --size 5
```

## Pension Fund Trend

```bash
python3 scripts/pension_fund_trend.py --code A005930 --year 2026 --summary-only
python3 scripts/pension_fund_trend.py --code A005930 --from 2026-01-01 --to 2026-01-31 --format csv
```

## Page API Smoke Checks

Use `page_api_check.py` when a user asks whether the stock page APIs still call
cleanly for a single product. It checks only read-only stock information endpoint
groups and does not call order placement, order amendment, account, balance, or
orderable-amount APIs.

```bash
python3 scripts/page_api_check.py --code A005930
python3 scripts/page_api_check.py --code A005930 --pages order,analytics,news,transaction-status
python3 scripts/page_api_check.py --code A005930 --pages transaction-status --from 2026-04-01 --to 2026-04-24
```
