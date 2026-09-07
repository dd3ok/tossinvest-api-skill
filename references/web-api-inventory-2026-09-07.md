# Web API Inventory — 2026-09-07

This is the full static table inventory (153 catalog entries and 11 WebSocket-reference entries, including duplicates). Candidate code matches are not exact contract matches; use the linked source table for the authoritative original status/method. Current live dispositions and confirmed changes are in [the update audit](update-audit-2026-09-07.md). Unchecked rows retain their historical status and are **unverified in this run**.

작성일: 2026-09-07. 저장소 source/catalog/test만 조사했고 네트워크 요청은 실행하지 않았다.

`script-backed`는 코드 존재를 뜻하며 현재 서버 성공을 뜻하지 않는다. 검증상태는 원문을 보존했다. 코드 연결은 AST의 endpoint template 후보를 대조했으며 공통 transport allowlist만 있는 경우는 구현으로 세지 않았다. `{...}` 자리의 서로 다른 값은 일치 후보이므로 같은 구조의 주식/지수 c-chart는 복수 후보로 표시된다. 최근 실제 브라우저 결과는 root 조사와 함께 판단해야 한다.

## Contents

- [파일별 호출 template](#파일별-호출-template)
- [api-catalog.md — Stock Summary APIs](#api-catalogmd-stock-summary-apis)
- [api-catalog.md — Chart APIs](#api-catalogmd-chart-apis)
- [api-catalog.md — Index And Market Indicator APIs](#api-catalogmd-index-and-market-indicator-apis)
- [api-catalog.md — Bond APIs](#api-catalogmd-bond-apis)
- [api-catalog.md — Analytics APIs](#api-catalogmd-analytics-apis)
- [api-catalog.md — Filings And News APIs](#api-catalogmd-filings-and-news-apis)
- [api-catalog.md — Transaction Status APIs](#api-catalogmd-transaction-status-apis)
- [api-catalog.md — Dashboard And Discovery APIs](#api-catalogmd-dashboard-and-discovery-apis)
- [api-catalog.md — Calendar APIs](#api-catalogmd-calendar-apis)
- [api-catalog.md — Feed And News APIs](#api-catalogmd-feed-and-news-apis)
- [api-catalog.md — Screener APIs](#api-catalogmd-screener-apis)
- [api-catalog.md — Cert And Status Helpers](#api-catalogmd-cert-and-status-helpers)
- [api-catalog.md — Public Community And Main-Page APIs](#api-catalogmd-public-community-and-main-page-apis)
- [api-catalog.md — Route-manifest scope review](#api-catalogmd-route-manifest-scope-review)
- [websocket-api-reference.md — Available logged-out page channels](#websocket-api-referencemd-available-logged-out-page-channels)
- [websocket-api-reference.md — Experimental or unverified destinations](#websocket-api-referencemd-experimental-or-unverified-destinations)
- [websocket-api-reference.md — HTTP Snapshot And Stream Semantics](#websocket-api-referencemd-http-snapshot-and-stream-semantics)

## 파일별 호출 template

| 스크립트 | 호출 endpoint template 개수 (문자열/동적 template) |
|---|---:|
| `calendar.py` | 7 |
| `community_comments.py` | 4 |
| `dashboard_ranking.py` | 5 |
| `feed.py` | 4 |
| `filings.py` | 1 |
| `financials.py` | 11 |
| `indices.py` | 13 |
| `market_search.py` | 1 |
| `news.py` | 2 |
| `page_api_check.py` | 40 |
| `pension_fund_trend.py` | 1 |
| `quote.py` | 2 |
| `screener_count.py` | 6 |
| `sector.py` | 7 |
| `stock_chart.py` | 1 |
| `stock_page.py` | 6 |
| `stock_summary.py` | 3 |
| `theme.py` | 10 |
| `trading_trend.py` | 4 |
| `websocket_prices.py` | 5 |

## api-catalog.md — Stock Summary APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Common stock detail UI](api-catalog.md) | script-backed | `/api/v1/stock-detail/ui/{productCode}/common` | [page_api_check.py:100](../scripts/page_api_check.py) |
| [Header info](api-catalog.md) | script-backed | `/api/v1/stock-infos/header/{productCode}` | [page_api_check.py:106](../scripts/page_api_check.py), [page_api_check.py:112](../scripts/page_api_check.py), [stock_page.py:30](../scripts/stock_page.py) |
| [WTS badges](api-catalog.md) | script-backed | `/api/v1/stock-infos/{productCode}/wts-badges` | [page_api_check.py:106](../scripts/page_api_check.py), [page_api_check.py:112](../scripts/page_api_check.py) |
| [Stock info](api-catalog.md) | script-backed | `/api/v2/stock-infos/{productCode}` | [page_api_check.py:115](../scripts/page_api_check.py), [stock_summary.py:30](../scripts/stock_summary.py) |
| [Code or symbol lookup](api-catalog.md) | script-backed | `/api/v2/stock-infos/code-or-symbol/{productCode}` | [community_comments.py:114](../scripts/community_comments.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [stock_page.py:43](../scripts/stock_page.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Batch stock info](api-catalog.md) | observed | `/api/v1/stock-infos?codes={codes}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Price batch v1](api-catalog.md) | observed | `/api/v1/product/stock-prices?meta=true&productCodes={codes}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Price batch v3](api-catalog.md) | observed | `/api/v3/stock-prices?meta=true&productCodes={codes}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Price details](api-catalog.md) | script-backed | `/api/v3/stock-prices/details?productCodes={codes}` | [page_api_check.py:121](../scripts/page_api_check.py), [stock_page.py:65](../scripts/stock_page.py), [stock_summary.py:33](../scripts/stock_summary.py) |
| [Quote book v2](api-catalog.md) | observed | `/api/v2/stock-prices/{productCode}/quotes` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Quote book v3](api-catalog.md) | script-backed, observed | `/api/v3/stock-prices/{productCode}/quotes` | [page_api_check.py:128](../scripts/page_api_check.py), [quote.py:21](../scripts/quote.py) |
| [Intraday ticks](api-catalog.md) | script-backed, observed | `/api/v2/stock-prices/{productCode}/ticks` | [page_api_check.py:136](../scripts/page_api_check.py), [quote.py:32](../scripts/quote.py) |
| [Main-session prices](api-catalog.md) | observed | `/api/v1/stock-prices/mainsession?codes={codes}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [After-session prices](api-catalog.md) | observed | `/api/v1/stock-prices/after?codes={codes}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Upper/lower price bounds](api-catalog.md) | script-backed | `/api/v2/stock-prices/{productCode}/upper-lower` | [page_api_check.py:144](../scripts/page_api_check.py) |

## api-catalog.md — Chart APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [KR stock candle chart](api-catalog.md) | script-backed | `/api/v1/c-chart/kr-s/{productCode}/{range}` | [indices.py:94](../scripts/indices.py), [page_api_check.py:151](../scripts/page_api_check.py), [stock_chart.py:39](../scripts/stock_chart.py) |
| [US stock candle chart](api-catalog.md) | script-backed | `/api/v1/c-chart/us-s/{productCode}/{range}` | [indices.py:94](../scripts/indices.py), [stock_chart.py:39](../scripts/stock_chart.py) |

## api-catalog.md — Index And Market Indicator APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Index info](api-catalog.md) | script-backed | `/api/v2/index-infos/{indexCode}` | [indices.py:59](../scripts/indices.py) |
| [Index price](api-catalog.md) | script-backed | `/api/v1/index-prices/{indexCode}` | [indices.py:63](../scripts/indices.py) |
| [Index/market chart](api-catalog.md) | script-backed | `/api/v1/r-chart/{securitiesType}/{indexCode}/{range}/{step}` | [indices.py:77](../scripts/indices.py), [indices.py:105](../scripts/indices.py) |
| [Index daily quote table](api-catalog.md) | script-backed | `/api/v1/c-chart/{securitiesType}/{indexCode}/day:1` | [indices.py:94](../scripts/indices.py), [page_api_check.py:151](../scripts/page_api_check.py), [stock_chart.py:39](../scripts/stock_chart.py) |
| [Crypto prices](api-catalog.md) | script-backed | `/api/v1/crypto-prices?productCodes={codes}` | [indices.py:118](../scripts/indices.py) |
| [USD/KRW product exchange rate](api-catalog.md) | script-backed | `/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW` | [indices.py:123](../scripts/indices.py) |
| [FX chart](api-catalog.md) | script-backed | `/api/v1/r-chart/fx/EXCHANGE_RATE/{range}/{step}` | [indices.py:77](../scripts/indices.py), [indices.py:105](../scripts/indices.py) |
| [Overview indicators v3](api-catalog.md) | observed | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Overview indicator by type](api-catalog.md) | script-backed, observed | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/{type}` | [indices.py:135](../scripts/indices.py) |
| [Overview indicator mini-chart](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/mini-chart` | [indices.py:141](../scripts/indices.py) |
| [Related ETFs](api-catalog.md) | script-backed | `/api/v3/dashboard/wts/overview/indicator/{indexCode}/related-etfs` | [indices.py:145](../scripts/indices.py) |
| [Index net buying range](api-catalog.md) | script-backed | `/api/v1/stock-infos/index/net-buying/range` | [indices.py:156](../scripts/indices.py) |
| [Index net buying daily](api-catalog.md) | script-backed | `/api/v1/stock-infos/index/net-buying/daily` | [indices.py:195](../scripts/indices.py) |
| [Exchange rates widget](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/overview/exchange-rates` | [indices.py:201](../scripts/indices.py) |

## api-catalog.md — Bond APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Bond detail](api-catalog.md) | observed | `/api/v1/bond-infos` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Simple bond metadata](api-catalog.md) | observed | `/api/v1/bond-infos/simple` | — (호출 코드 없음; 문서 관찰/재확인 대상) |

## api-catalog.md — Analytics APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Sales composition](api-catalog.md) | script-backed | `/api/v1/companies/{companyCode}/sales-compositions` | [page_api_check.py:199](../scripts/page_api_check.py) |
| [Related themes/categories](api-catalog.md) | script-backed | `/api/v2/companies/{companyCode}/tics` | [page_api_check.py:202](../scripts/page_api_check.py) |
| [Stock overview](api-catalog.md) | script-backed | `/api/v2/stock-infos/{productCode}/overview` | [community_comments.py:114](../scripts/community_comments.py), [financials.py:20](../scripts/financials.py), [financials.py:21](../scripts/financials.py), [financials.py:22](../scripts/financials.py), [financials.py:23](../scripts/financials.py), [financials.py:24](../scripts/financials.py), [page_api_check.py:182](../scripts/page_api_check.py), [page_api_check.py:185](../scripts/page_api_check.py), [page_api_check.py:187](../scripts/page_api_check.py), [page_api_check.py:190](../scripts/page_api_check.py), [page_api_check.py:192](../scripts/page_api_check.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:220](../scripts/page_api_check.py), [stock_page.py:43](../scripts/stock_page.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Business/holding composition](api-catalog.md) | script-backed | `/api/v2/stock-infos/{productCode}/compositions` | [community_comments.py:114](../scripts/community_comments.py), [financials.py:20](../scripts/financials.py), [financials.py:21](../scripts/financials.py), [financials.py:22](../scripts/financials.py), [financials.py:23](../scripts/financials.py), [financials.py:24](../scripts/financials.py), [page_api_check.py:182](../scripts/page_api_check.py), [page_api_check.py:185](../scripts/page_api_check.py), [page_api_check.py:187](../scripts/page_api_check.py), [page_api_check.py:190](../scripts/page_api_check.py), [page_api_check.py:192](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [page_api_check.py:220](../scripts/page_api_check.py), [stock_page.py:43](../scripts/stock_page.py) |
| [ETF/ETN investment detail](api-catalog.md) | observed | `/api/v2/stock-infos/{productCode}/investment` | [community_comments.py:114](../scripts/community_comments.py), [financials.py:20](../scripts/financials.py), [financials.py:21](../scripts/financials.py), [financials.py:22](../scripts/financials.py), [financials.py:23](../scripts/financials.py), [financials.py:24](../scripts/financials.py), [page_api_check.py:182](../scripts/page_api_check.py), [page_api_check.py:185](../scripts/page_api_check.py), [page_api_check.py:187](../scripts/page_api_check.py), [page_api_check.py:190](../scripts/page_api_check.py), [page_api_check.py:192](../scripts/page_api_check.py), [page_api_check.py:220](../scripts/page_api_check.py), [stock_page.py:43](../scripts/stock_page.py) |
| [Consensus](api-catalog.md) | script-backed | `/api/v2/stock-infos/consensus/{productCode}` | [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [page_api_check.py:220](../scripts/page_api_check.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Analyst opinion](api-catalog.md) | script-backed | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-opinion` | [page_api_check.py:226](../scripts/page_api_check.py) |
| [Analyst reports](api-catalog.md) | script-backed | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-reports` | [page_api_check.py:232](../scripts/page_api_check.py) |
| [Investment indicators](api-catalog.md) | script-backed | `/api/v1/stock-detail/ui/wts/{productCode}/investment-indicators` | [page_api_check.py:238](../scripts/page_api_check.py) |
| [Analytics section order](api-catalog.md) | script-backed | `/api/v1/stock-detail/ui/wts/{productCode}/section-orders` | [page_api_check.py:244](../scripts/page_api_check.py) |
| [Dividend summary](api-catalog.md) | script-backed | `/api/v1/stock-infos/dividend/{productCode}/summary` | [page_api_check.py:250](../scripts/page_api_check.py) |
| [Dividend years](api-catalog.md) | script-backed | `/api/v1/stock-infos/dividend/{productCode}/years` | [page_api_check.py:256](../scripts/page_api_check.py) |
| [Dividend yield history](api-catalog.md) | script-backed | `/api/v1/stock-infos/{productCode}/dividends/yield-ratio/histories` | [page_api_check.py:262](../scripts/page_api_check.py) |
| [Comprehensive financial statements](api-catalog.md) | script-backed | `/api/v2/companies/{productCode}/financial-statements/comprehensive` | [financials.py:14](../scripts/financials.py), [page_api_check.py:167](../scripts/page_api_check.py) |
| [Financial statement records](api-catalog.md) | script-backed | `/api/v2/companies/{productCode}/financial-statement-records` | [financials.py:15](../scripts/financials.py), [page_api_check.py:171](../scripts/page_api_check.py) |
| [Financial estimate date](api-catalog.md) | script-backed | `/api/v2/companies/{productCode}/financial/estimate/date` | [financials.py:16](../scripts/financials.py), [page_api_check.py:268](../scripts/page_api_check.py) |
| [Revenue estimate](api-catalog.md) | script-backed | `/api/v2/companies/{productCode}/financial/estimate/revenue` | [financials.py:17](../scripts/financials.py), [page_api_check.py:175](../scripts/page_api_check.py) |
| [EPS estimate](api-catalog.md) | script-backed | `/api/v2/companies/{productCode}/financial/estimate/eps` | [financials.py:18](../scripts/financials.py), [page_api_check.py:177](../scripts/page_api_check.py) |
| [Operating income estimate](api-catalog.md) | script-backed | `/api/v2/companies/{productCode}/financial/estimate/operating-income` | [financials.py:19](../scripts/financials.py), [page_api_check.py:180](../scripts/page_api_check.py) |
| [Valuation](api-catalog.md) | script-backed | `/api/v2/stock-infos/evaluation/{productCode}` | [financials.py:20](../scripts/financials.py), [page_api_check.py:182](../scripts/page_api_check.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Valuation comparison](api-catalog.md) | script-backed | `/api/v2/stock-infos/evaluation-comparison/{productCode}` | [financials.py:21](../scripts/financials.py), [page_api_check.py:185](../scripts/page_api_check.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Stability](api-catalog.md) | script-backed | `/api/v2/stock-infos/stability/{productCode}` | [financials.py:22](../scripts/financials.py), [page_api_check.py:187](../scripts/page_api_check.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Revenue and net profit](api-catalog.md) | script-backed | `/api/v2/stock-infos/revenue-and-net-profit/{productCode}` | [financials.py:23](../scripts/financials.py), [page_api_check.py:190](../scripts/page_api_check.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [stock_summary.py:40](../scripts/stock_summary.py) |
| [Operating income](api-catalog.md) | script-backed | `/api/v2/stock-infos/operating-income/{productCode}` | [financials.py:24](../scripts/financials.py), [page_api_check.py:192](../scripts/page_api_check.py), [page_api_check.py:208](../scripts/page_api_check.py), [page_api_check.py:214](../scripts/page_api_check.py), [stock_summary.py:40](../scripts/stock_summary.py) |

## api-catalog.md — Filings And News APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Company filings list](api-catalog.md) | script-backed, observed | `/api/v1/stock-detail/companies/{companyCode}/filings` | [filings.py:14](../scripts/filings.py), [page_api_check.py:292](../scripts/page_api_check.py) |
| [Filing detail](api-catalog.md) | observed | `/api/v1/stock-infos/filings/companies/{companyCode}/report/{reportId}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Company news](api-catalog.md) | script-backed, observed | `/api/v2/news/companies/{companyCode}` | [news.py:23](../scripts/news.py), [page_api_check.py:284](../scripts/page_api_check.py) |
| [News detail](api-catalog.md) | script-backed | `/api/v2/news/{newsId}` | [news.py:43](../scripts/news.py) |
| [Exclude headline news](api-catalog.md) | observed | `/api/v2/forum/news/headline/exclude/{newsId}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |

## api-catalog.md — Transaction Status APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Broker trading ranking](api-catalog.md) | script-backed | `/api/v1/mds/broker/trading-ranking` | [page_api_check.py:305](../scripts/page_api_check.py), [trading_trend.py:111](../scripts/trading_trend.py) |
| [Investor trading trend](api-catalog.md) | script-backed | `/api/v1/stock-infos/trade/trend/trading-trend` | [page_api_check.py:312](../scripts/page_api_check.py), [trading_trend.py:88](../scripts/trading_trend.py), [trading_trend.py:100](../scripts/trading_trend.py), [trading_trend.py:107](../scripts/trading_trend.py) |
| [Program trading](api-catalog.md) | script-backed | `/api/v1/stock-infos/trade/trend/program-trading` | [page_api_check.py:321](../scripts/page_api_check.py), [trading_trend.py:88](../scripts/trading_trend.py), [trading_trend.py:100](../scripts/trading_trend.py), [trading_trend.py:107](../scripts/trading_trend.py) |
| [Fixed-date trading trend](api-catalog.md) | script-backed | `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | [page_api_check.py:330](../scripts/page_api_check.py), [pension_fund_trend.py:40](../scripts/pension_fund_trend.py), [trading_trend.py:88](../scripts/trading_trend.py), [trading_trend.py:100](../scripts/trading_trend.py), [trading_trend.py:107](../scripts/trading_trend.py) |
| [Accumulated fixed trading trend](api-catalog.md) | script-backed, observed | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | [page_api_check.py:339](../scripts/page_api_check.py), [trading_trend.py:88](../scripts/trading_trend.py), [trading_trend.py:100](../scripts/trading_trend.py), [trading_trend.py:107](../scripts/trading_trend.py) |
| [Accumulated fixed trend detail](api-catalog.md) | script-backed, observed | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | [page_api_check.py:348](../scripts/page_api_check.py), [trading_trend.py:88](../scripts/trading_trend.py) |
| [MDS info pages](api-catalog.md) | script-backed | `/api/v1/mds/info/{type}` | [trading_trend.py:117](../scripts/trading_trend.py), [trading_trend.py:136](../scripts/trading_trend.py) |
| [Program trading](api-catalog.md) | 원문 설명 참조 | `/api/v1/stock-infos/trade/trend/program-trading` | [page_api_check.py:321](../scripts/page_api_check.py), [trading_trend.py:88](../scripts/trading_trend.py), [trading_trend.py:100](../scripts/trading_trend.py), [trading_trend.py:107](../scripts/trading_trend.py) |
| [Credit](api-catalog.md) | 원문 설명 참조 | `/api/v1/mds/info/credit` | [trading_trend.py:117](../scripts/trading_trend.py), [trading_trend.py:136](../scripts/trading_trend.py) |
| [Lending trading](api-catalog.md) | 원문 설명 참조 | `/api/v1/mds/info/lending-trading` | [trading_trend.py:117](../scripts/trading_trend.py), [trading_trend.py:136](../scripts/trading_trend.py) |
| [Short selling](api-catalog.md) | 원문 설명 참조 | `/api/v1/mds/info/short-selling-trend` | [trading_trend.py:117](../scripts/trading_trend.py), [trading_trend.py:136](../scripts/trading_trend.py) |
| [CFD](api-catalog.md) | 원문 설명 참조 | `/api/v1/mds/info/cfd` | [trading_trend.py:117](../scripts/trading_trend.py), [trading_trend.py:136](../scripts/trading_trend.py) |

## api-catalog.md — Dashboard And Discovery APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Realtime stock ranking](api-catalog.md) | observed | `/api/v1/rankings/realtime/stock?size=10` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Dashboard intelligences](api-catalog.md) | observed | `/api/v1/dashboard/intelligences/all` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Observed legacy/detail AI signals](api-catalog.md) | observed | `/api/v1/dashboard/wts/overview/ai-signals` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Signal details](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/overview/ai-signals/detail?productCode={productCode}&productType=STOCKS` | [stock_page.py:24](../scripts/stock_page.py) |
| [Overview stock signals](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/overview/signals?codes={codes}` | [dashboard_ranking.py:104](../scripts/dashboard_ranking.py) |
| [Exchange rates](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/overview/exchange-rates` | [indices.py:201](../scripts/indices.py) |
| [Trading info](api-catalog.md) | observed | `/api/v1/dashboard/wts/overview/trading-info` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [WTS news feed](api-catalog.md) | observed | `/api/v1/dashboard/wts/news` | [feed.py:109](../scripts/feed.py) |
| [Public WTS search](api-catalog.md) | script-backed, observed | `/api/v3/search-all/wts-auto-complete` | [market_search.py:81](../scripts/market_search.py) |
| [Home live-chart top100 ranking](api-catalog.md) | script-backed, observed | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | [dashboard_ranking.py:127](../scripts/dashboard_ranking.py), [dashboard_ranking.py:153](../scripts/dashboard_ranking.py) |
| [Realtime investor rankings](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` | [dashboard_ranking.py:94](../scripts/dashboard_ranking.py) |
| [Economic calendar](api-catalog.md) | script-backed | `/api/v2/dashboard/wts/overview/calendar/economic-events` | [calendar.py:55](../scripts/calendar.py) |
| [Calendar AI key events](api-catalog.md) | script-backed | `/api/v1/calendar/ai-summary/key-events` | [calendar.py:47](../scripts/calendar.py) |
| [Current home industry ranking](api-catalog.md) | script-backed, observed | `/api/v2/dashboard/wts/overview/tics/ranking` | [sector.py:164](../scripts/sector.py), [theme.py:155](../scripts/theme.py) |
| [Current sector overview](api-catalog.md) | script-backed | `/api/v2/dashboard/wts/overview/tics/{ticsId}/overview` | [sector.py:86](../scripts/sector.py) |
| [Current sector compact header](api-catalog.md) | script-backed | `/api/v2/dashboard/wts/overview/tics/{ticsId}/simple` | [sector.py:93](../scripts/sector.py) |
| [Current sector comparison chart](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/overview/tics/{ticsId}/comparison-chart` | [sector.py:104](../scripts/sector.py) |
| [Current sector stocks](api-catalog.md) | script-backed, observed | `/api/v2/dashboard/wts/overview/tics/{ticsId}/stocks` | [sector.py:258](../scripts/sector.py), [theme.py:73](../scripts/theme.py) |
| [Current sector ETFs](api-catalog.md) | script-backed, observed | `/api/v2/dashboard/wts/overview/tics/{ticsId}/etfs` | [sector.py:263](../scripts/sector.py), [theme.py:77](../scripts/theme.py) |
| [Current sector news](api-catalog.md) | script-backed | `/api/v2/dashboard/wts/overview/tics/{ticsId}/news` | [sector.py:116](../scripts/sector.py) |
| [Current sector news](api-catalog.md) | script-backed | `/api/v2/news/{newsId}` | [news.py:43](../scripts/news.py) |
| [Auxiliary TICS ranking](api-catalog.md) | observed | `/api/v1/tics/rankings` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Theme list](api-catalog.md) | script-backed | `/api/v1/tics/all` | [theme.py:160](../scripts/theme.py) |
| [Theme ranking by tag](api-catalog.md) | script-backed | `/api/v1/rankings/contents/tics_margin_depth1/tags/{tag}` | [theme.py:37](../scripts/theme.py) |
| [Theme details](api-catalog.md) | script-backed | `/api/v1/tics/{ticsId}/details` | [theme.py:41](../scripts/theme.py) |
| [Theme company ranking](api-catalog.md) | script-backed | `/api/v1/companies/tics/rankings?ticsId={ticsId}&ticsRanking={ranking}` | [theme.py:52](../scripts/theme.py) |
| [Related themes](api-catalog.md) | script-backed | `/api/v1/tics/{ticsId}/related` | [theme.py:58](../scripts/theme.py) |
| [Theme news](api-catalog.md) | script-backed | `/api/v2/news/tics/{ticsId}` | [theme.py:45](../scripts/theme.py) |
| [Theme fluctuations](api-catalog.md) | script-backed | `/api/v2/tics/{ticsId}/fluctuations` | [theme.py:62](../scripts/theme.py) |

## api-catalog.md — Calendar APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Monthly market calendar](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}` | [calendar.py:34](../scripts/calendar.py) |
| [Index-page calendar subset](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}/index?countryType=kr&#124;us` | [calendar.py:41](../scripts/calendar.py) |
| [Economic indicator detail](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/calendar/economic-indicators/{ric}?announceDate={YYYY-MM-DD}` | [calendar.py:60](../scripts/calendar.py) |
| [Economic indicator AI analysis](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/analysis/indicators?announceDateTime={YYYY-MM-DDTHH:mm:ss}&ricId={ric}` | [calendar.py:67](../scripts/calendar.py) |
| [Calendar key events](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/calendar/ai-summary/key-events` | [calendar.py:47](../scripts/calendar.py) |
| [Weekly AI summary](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/summary/weekly` | [calendar.py:51](../scripts/calendar.py) |
| [Overview economic events](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/calendar/economic-events` | [calendar.py:55](../scripts/calendar.py) |

## api-catalog.md — Feed And News APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Historical recommended feed posts](api-catalog.md) | needs-recheck | `/api/v3/feed/recommend/posts` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Current recommended feed posts](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | [feed.py:17](../scripts/feed.py), [feed.py:18](../scripts/feed.py) |
| [Dashboard/news tab feed](api-catalog.md) | script-backed | `/api/v1/dashboard/wts/news` | [feed.py:109](../scripts/feed.py) |
| [News detail](api-catalog.md) | script-backed | `/api/v2/news/{newsId}` | [news.py:43](../scripts/news.py) |

## api-catalog.md — Screener APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Common screener presets](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/screener/presets/common?useCustom=true` | [screener_count.py:211](../scripts/screener_count.py) |
| [Screener search modal](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen/search/modal` | [screener_count.py:217](../scripts/screener_count.py) |
| [Screener base filters](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/base` | [screener_count.py:363](../scripts/screener_count.py) |
| [Screener range filters](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/range` | [screener_count.py:372](../scripts/screener_count.py) |
| [Screener result count](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count` | [screener_count.py:325](../scripts/screener_count.py) |
| [Screener results](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen` | [screener_count.py:346](../scripts/screener_count.py) |

## api-catalog.md — Cert And Status Helpers

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Stock red flags](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/stock-infos/{productCode}/red-flags` | [page_api_check.py:106](../scripts/page_api_check.py), [stock_page.py:30](../scripts/stock_page.py) |
| [Product trading status](api-catalog.md) | script-backed, observed | `https://wts-cert-api.tossinvest.com/api/v3/trading/order/{productCode}/trading-status` | [stock_page.py:34](../scripts/stock_page.py) |
| [Trading analysis metadata](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/trading/analysis/productCode/{productCode}` | [stock_page.py:38](../scripts/stock_page.py) |
| [Overview indicator](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/index?market=kr` | [indices.py:135](../scripts/indices.py) |
| [Overview indicator v3](api-catalog.md) | observed | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator?market=kr` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Overview indicator v4](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | [dashboard_ranking.py:205](../scripts/dashboard_ranking.py) |
| [Overview ranking](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | [dashboard_ranking.py:127](../scripts/dashboard_ranking.py), [dashboard_ranking.py:153](../scripts/dashboard_ranking.py) |
| [Live-chart top100 ranking](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | [dashboard_ranking.py:127](../scripts/dashboard_ranking.py), [dashboard_ranking.py:153](../scripts/dashboard_ranking.py) |
| [Monthly calendar](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}` | [calendar.py:34](../scripts/calendar.py) |
| [Index-page calendar subset](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}/index?countryType=kr&#124;us` | [calendar.py:41](../scripts/calendar.py) |
| [Economic indicator detail](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/calendar/economic-indicators/{ric}?announceDate={YYYY-MM-DD}` | [calendar.py:60](../scripts/calendar.py) |
| [Economic indicator AI analysis](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/analysis/indicators` | [calendar.py:67](../scripts/calendar.py) |
| [Calendar key events](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/calendar/ai-summary/key-events` | [calendar.py:47](../scripts/calendar.py) |
| [Calendar weekly summary](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/summary/weekly` | [calendar.py:51](../scripts/calendar.py) |
| [Economic calendar](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/calendar/economic-events` | [calendar.py:55](../scripts/calendar.py) |
| [Investor rankings](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` | [dashboard_ranking.py:94](../scripts/dashboard_ranking.py) |

## api-catalog.md — Public Community And Main-Page APIs

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Public stock comments](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v4/comments` | [community_comments.py:70](../scripts/community_comments.py) |
| [Public lounge comments](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v4/comments` | [community_comments.py:70](../scripts/community_comments.py) |
| [Public comment replies](api-catalog.md) | public-social-sensitive, script-backed, observed | `https://wts-cert-api.tossinvest.com/api/v2/comments/{commentId}/replies` | [community_comments.py:74](../scripts/community_comments.py) |
| [Public community post permalink and replies](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v1/comments/{postId}/replies` | [community_comments.py:81](../scripts/community_comments.py) |
| [Stock community related board](api-catalog.md) | public-social-sensitive | `https://wts-cert-api.tossinvest.com/api/v1/boards/STOCK/{productCode}/related` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Stock community recommended profiles](api-catalog.md) | public-social-sensitive | `https://wts-cert-api.tossinvest.com/api/v1/community/board/{productCode}/recommend-profiles` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Popular-follower feed support](api-catalog.md) | public-social-sensitive | `https://wts-cert-api.tossinvest.com/api/v1/boards/popular-follower` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [Community top rankings](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | [feed.py:124](../scripts/feed.py) |
| [Feed community ranking posts](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | [feed.py:17](../scripts/feed.py), [feed.py:18](../scripts/feed.py) |
| [https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator](api-catalog.md) | observed-drift | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator](api-catalog.md) | script-backed | `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | [dashboard_ranking.py:205](../scripts/dashboard_ranking.py) |
| [https://wts-info-api.tossinvest.com/api/v2/dashboard/wts/overview/signals](api-catalog.md) | observed-drift | `https://wts-info-api.tossinvest.com/api/v2/dashboard/wts/overview/signals` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-buy](api-catalog.md) | excluded, observed | `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-buy` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-sell](api-catalog.md) | excluded | `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-sell` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}](api-catalog.md) | public-social-sensitive | `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | [feed.py:124](../scripts/feed.py) |
| [https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts](api-catalog.md) | public-social-sensitive, script-backed | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | [feed.py:17](../scripts/feed.py), [feed.py:18](../scripts/feed.py) |

## api-catalog.md — Route-manifest scope review

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [/cheetah, /cheetah/[code]](api-catalog.md) | needs-recheck | `/api/v1/reasoning-news/count` | — (호출 코드 없음; 문서 관찰/재확인 대상) |

## websocket-api-reference.md — Available logged-out page channels

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [krStockTradeUpdates](websocket-api-reference.md) | confirmed-public, bounded-live | `/topic/v1/kr/stock/trade/{productCode}` | [websocket_prices.py:300](../scripts/websocket_prices.py) |
| [usStockTradeUpdates](websocket-api-reference.md) | confirmed-public, bounded-live | `/topic/v1/us/stock/trade/{productCode}` | [websocket_prices.py:304](../scripts/websocket_prices.py) |
| [krStockIndexUpdates](websocket-api-reference.md) | bounded-live | `/topic/v1/kr/stock/index/{productCode}` | [websocket_prices.py:309](../scripts/websocket_prices.py) |
| [usStockIndexUpdates](websocket-api-reference.md) | bounded-live | `/topic/v1/us/stock/index/{productCode}` | [websocket_prices.py:314](../scripts/websocket_prices.py) |
| [cryptoVwapUpdates](websocket-api-reference.md) | bounded-live | `/topic/v1/crypto/vwap/{productCode}` | [websocket_prices.py:319](../scripts/websocket_prices.py) |

## websocket-api-reference.md — Experimental or unverified destinations

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Stock bid/offer and pre-open estimates](websocket-api-reference.md) | observed-code | `/topic/v1/{market}/stock/bidoffer/{productCode}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |
| [KR stock status invalidation](websocket-api-reference.md) | observed-code | `/topic/v1/kr/stock/status/{productCode}` | — (호출 코드 없음; 문서 관찰/재확인 대상) |

## websocket-api-reference.md — HTTP Snapshot And Stream Semantics

| 목적 / 출처 | 상태 | endpoint | 코드 연결 후보 |
|---|---|---|---|
| [Stock trade ticks](websocket-api-reference.md) | observed | `/api/v2/stock-prices/{code}/ticks` | [page_api_check.py:136](../scripts/page_api_check.py), [quote.py:32](../scripts/quote.py) |
| [Stock quote/order-book snapshot](websocket-api-reference.md) | 원문 설명 참조 | `/api/v3/stock-prices/{code}/quotes` | [page_api_check.py:128](../scripts/page_api_check.py), [quote.py:21](../scripts/quote.py) |
| [Screener HTTP snapshot](websocket-api-reference.md#http-snapshot-and-stream-semantics) | 원문 설명 참조 | POST `/api/v2/screener/screen` | [screener_count.py](../scripts/screener_count.py) |
| [Home live-chart top100 HTTP snapshot](websocket-api-reference.md#http-snapshot-and-stream-semantics) | 원문 설명 참조 | POST `/api/v2/dashboard/wts/overview/ranking` | [dashboard_ranking.py](../scripts/dashboard_ranking.py) |
