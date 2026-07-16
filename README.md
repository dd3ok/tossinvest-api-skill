# 비공식 토스증권 API / TossInvest API Skill

[![TossInvest API Skill CI](https://github.com/dd3ok/tossinvest-api-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/dd3ok/tossinvest-api-skill/actions/workflows/ci.yml)
[![최신 릴리스](https://img.shields.io/github/v/release/dd3ok/tossinvest-api-skill?sort=semver)](https://github.com/dd3ok/tossinvest-api-skill/releases/latest)

> 토스증권 웹에 공개된 API를 바탕으로 만든 경량 에이전트 스킬입니다.  
> 로그인이나 계좌 인증 없이 공개 주식·시장 데이터를 Codex, Claude Code 같은 에이전트가 안전하게 다시 조회하도록 돕습니다.  
> 공식 Open API, 증권사 거래 API, 투자 조언 도구가 아닙니다.

## 공식 Open API와의 구분

이 스킬은 `developers.tossinvest.com/docs`에서 제공하는 토스증권 공식 Open API 클라이언트가 아닙니다.  
토스증권 공개 웹 페이지에 이미 표시되는 주식·시장 데이터를 조회하도록 돕는 경량 에이전트 스킬입니다.  
공식 Open API 앱 설정, OAuth 토큰, 계좌 헤더, IP 등록 절차는 필요하지 않습니다.  
계좌·자산·주문 업무가 필요하다면 공식 Open API 문서를 기준으로 별도 클라이언트를 구현하세요.

## 지원 범위

### 공개 HTTP 기반 조회

- 종목 요약과 현재가·호가 스냅샷·장중 체결 틱 조회
- 재무제표, 실적 추정, 밸류에이션, 배당, 안정성 지표
- 공시, 뉴스, 피드 탐색, 시장 통합 검색, 테마/TICS와 관련 테마·섹터 종목/ETF
- KOSPI 같은 지수와 일별 시세표, 환율 차트와 위젯, 채권·원자재 지표
- 증시 캘린더, 경제지표·실적 발표 일정, 국내·해외 캘린더 탭
- 국내·미국 실시간 차트 top100와 `투자위험 주식 숨기기`, 투자자 매매 동향, 브로커 순위, 스크리너 조건 검색
- 공개 주식 메인 페이지의 AI·상태 보조 정보와 정제된 주식·라운지 댓글·답글·커뮤니티 랭킹

### 차트 및 로컬 계산

- 일봉·주봉·월봉·분봉 차트
- RSI, SMA, EMA, MACD, Bollinger Bands 계산

### WebSocket API

- `scripts/websocket_prices.py`로 공개 국내·미국 주식 체결, 지수, 가상자산형 지수 이벤트를 제한된 시간·건수만큼 JSONL로 수신
- 서버·STOMP 연결·destination·`MESSAGE`·payload 필드는 [비공식 WebSocket API 레퍼런스](references/websocket-api-reference.md)에 정리
- 임시 게스트 연결값은 실행 중 메모리에서만 사용하며 CLI 인자·환경 파일·로그·출력·저장 파일에 남기지 않음
- 공개 지수(`KGG01P`, `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, `SOX.NAI`)만 허용하고 로그인 전환 지수에서는 즉시 중단함
- 호가·예상체결·종목상태 채널은 공개 시장 데이터만 실험적으로 다루며 로그인·주문·계좌 작업과 연결하지 않음
- 국내·미국 top100은 단일 WebSocket 랭킹 채널이 아니라 10초 주기 HTTP 랭킹 snapshot과 최대 100개 종목별 체결 구독을 결합함
- 검색·산업·투자자 동향·조건검색·뉴스 목록과 `scripts/quote.py`의 현재가·호가·체결 틱은 HTTP로 조회
- 구독·메모리·출력 제한은 [WebSocket 클라이언트 운영 제한](#websocket-클라이언트-운영-제한) 참고

설치 후 TossInvest 또는 토스증권을 언급해 자연어로 요청하면 종목 요약, 시세, 차트, 재무, 뉴스, 공시, 테마, 지수, 캘린더, 랭킹, 스크리너를 조회하고 공개 WebSocket 실시간 체결을 제한적으로 수신할 수 있습니다.

## 안정성 및 버전 정책

`v1.0.0`부터 다음 저장소 표면을 안정된 공개 계약으로 취급합니다.

- 스킬 이름 `tossinvest-web-api`와 `.agents/skills/tossinvest-web-api` 설치 경로
- `SKILL.md`, `scripts/`, `references/`, `agents/`를 포함한 설치 레이아웃
- 문서화된 CLI 명령과 옵션, 로그인·계좌·주문을 제외하는 안전 경계
- Python 3.10과 3.12 CI 호환성, HTTP 표준 라이브러리 실행, WebSocket 선택 의존성 잠금 파일

이 버전 정책은 이 저장소가 제공하는 인터페이스에 적용됩니다. 토스증권 웹 API와 WebSocket 채널은 여전히 비공식·미문서화 인터페이스이며 예고 없이 경로, 응답 필드, 접근 가능 여부가 바뀔 수 있습니다. 외부 응답 필드와 데이터 가용성은 하위 호환성 계약에 포함하지 않으며, 관찰된 변경은 API 카탈로그의 상태 표기와 릴리스 노트에 기록합니다.

## 설치

### Codex

Codex에서는 공개 GitHub URL로 설치를 요청할 수 있습니다.

```text
https://github.com/dd3ok/tossinvest-api-skill 에서 스킬을 설치해줘.
```

설치가 끝나면 Codex를 재시작해 스킬 목록을 다시 로드하세요. 이후 TossInvest 또는 토스증권을 언급한 주식 데이터 요청이 이 스킬로 연결됩니다.

수동으로 설치하려면 다음처럼 스킬 디렉터리에 클론합니다.

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills"
mkdir -p "$CODEX_SKILLS_DIR"
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skill.git "$CODEX_SKILLS_DIR/tossinvest-web-api"
```

이미 클론한 작업 디렉터리를 쓰고 싶다면 심볼릭 링크로 노출할 수 있습니다.

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills"
mkdir -p "$CODEX_SKILLS_DIR"
ln -sfn /path/to/tossinvest-api-skill "$CODEX_SKILLS_DIR/tossinvest-web-api"
```

특정 저장소에서만 쓰고 싶다면 이 저장소를 아래 위치에 클론하거나 복사하세요.

```text
.agents/skills/tossinvest-web-api/
```

스킬 루트 디렉터리명은 `SKILL.md`의 `name: tossinvest-web-api`와 맞추세요. 일부 validator는 스킬 이름과 부모 디렉터리명 일치를 검사하므로, 저장소 루트를 그대로 쓰더라도 최종 로컬 스킬 경로는 `.agents/skills/tossinvest-web-api`로 유지하세요.

### Claude Code

Claude Code는 개인 스킬 폴더와 프로젝트 스킬 폴더에서 사용자 정의 스킬을 탐색합니다.

개인 설치:

```bash
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skill.git ~/.claude/skills/tossinvest-web-api
```

프로젝트 설치:

```bash
mkdir -p .claude/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skill.git .claude/skills/tossinvest-web-api
```

지원 범위에 맞는 TossInvest/토스증권 공개 주식·시장 데이터 요청이라면 Claude가 이 스킬을 사용할 수 있습니다.

### Antigravity CLI

Antigravity CLI는 프로젝트의 `.agents/skills/<skill-name>/SKILL.md` 레이아웃에서 로컬 Agent Skill을 탐색합니다. 이 저장소는 `SKILL.md`, `scripts/`, `references/`를 포함한 스킬 루트이므로 프로젝트별 스킬 디렉터리에 클론하거나 복사해 사용하세요.

프로젝트 설치:

```bash
mkdir -p .agents/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skill.git .agents/skills/tossinvest-web-api
```

개발 중인 로컬 체크아웃을 바로 반영하려면 심볼릭 링크로 노출합니다.

```bash
mkdir -p .agents/skills
ln -sfn /path/to/tossinvest-api-skill .agents/skills/tossinvest-web-api
```

최종 파일 위치는 `.agents/skills/tossinvest-web-api/SKILL.md`가 되어야 합니다. Antigravity CLI를 `agy`로 실행한 뒤 `/skills`에서 `tossinvest-web-api`가 보이는지 확인하세요.

### 로컬 스크립트만 실행

에이전트 스킬로 설치하지 않고 Python 스크립트만 실행할 수도 있습니다. HTTP 스크립트는 Python 표준 라이브러리만 사용합니다. WebSocket 스크립트만 선택 의존성 하나가 필요합니다.

```bash
git clone https://github.com/dd3ok/tossinvest-api-skill.git
cd tossinvest-api-skill
python3 scripts/stock_summary.py --code A005930 --no-overview
```

WebSocket 수신을 사용할 때만 다음 의존성을 설치합니다.

```bash
python3 -m pip install -r requirements-websocket.txt
```

스크립트별 옵션은 `--help`로 확인합니다.

```bash
python3 scripts/stock_chart.py --help
```

## 스크립트 빠른 실행

자주 쓰는 실행 예시는 다음과 같습니다.

```bash
python3 scripts/stock_summary.py --code A005930 --no-overview
python3 scripts/stock_page.py --code SOXL --comment-limit 5
python3 scripts/market_search.py --query 삼성전자 --section product --section news --limit 5
python3 scripts/community_comments.py --code NVDA --sort popular --limit 5
python3 scripts/community_comments.py --lounge-id LOUNGE_193394 --sort popular --limit 5
python3 scripts/quote.py --code A005930 --ticks 5
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart biggest_total_amount --market us --duration realtime --hide-investment-risk
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart biggest_market_amount --market us --duration 20d
python3 scripts/dashboard_ranking.py --kind indicator
python3 scripts/indices.py --code KGG01P --include-daily-quotes --daily-quote-count 20
python3 scripts/theme.py --tag us --tics-id 925 --include-sector-stocks --include-sector-etfs --sector-nation us
python3 scripts/feed.py --kind community-ranking --community-ranking profit --community-limit 10
python3 scripts/websocket_prices.py --kr-stock A005930 --duration 10 --max-events 5
python3 scripts/websocket_prices.py --us-stock US20100311002 --duration 10 --max-events 5
python3 scripts/websocket_prices.py --crypto VWAP.KRW-BTC --duration 10 --max-events 5
python3 scripts/stock_chart.py --code A005930 --range day:1 --count 61 --rsi-period 14 --macd --bollinger-period 20
python3 scripts/stock_chart.py --code US20100311002 --securities-type us-s --range day:1 --count 20
python3 scripts/financials.py --code A005930 --kind comprehensive
python3 scripts/calendar.py --year-month 2026-05 --kind economic --country us
python3 scripts/calendar.py --kind economic-detail --ric USPMI=ECI --date 2026-06-01 --include-analysis
python3 scripts/calendar.py --year-month 2026-06 --kind index-events --index-country us
python3 scripts/screener_count.py --nation kr --rsi oversold --include-results --size 5
```

더 많은 실행 예시는 [references/script-cookbook.md](references/script-cookbook.md)를, 엔드포인트 목록은 [references/api-catalog.md](references/api-catalog.md)를 참고하세요.

미국 주식 차트는 TossInvest 상품/소스 코드가 필요합니다. `SPY`, `NVDA` 같은 표시 티커를 `c-chart` 상품 코드로 바로 넣으면 HTTP 400이 날 수 있습니다.

실시간 값은 계속 바뀝니다. 아래 예시는 고정된 시장 데이터가 아니라 출력 형태를 보여주기 위한 예시입니다.

### WebSocket 클라이언트 운영 제한

HTTP 조회 스크립트는 요청할 때 실행되고 응답을 받으면 종료하므로 별도의 상주 클라이언트나 추가 패키지가 필요하지 않습니다. 지속적으로 이벤트를 받는 `websocket_prices.py`만 `requirements-websocket.txt`의 선택 의존성을 사용합니다.

| 항목 | 현재 동작 |
| --- | --- |
| 지원 스트림 | 국내·미국 주식 체결, 공개 지수, `VWAP.*` 가상자산형 지수 |
| 공개 지수 allowlist | KR `KGG01P`; US `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, `SOX.NAI` |
| 즉시 차단 | 로그인 전환이 확인된 `DJI.DJI`, `RFU.NQc1`, `RFU.GCv1`, 임의 destination·서버 URL·인증값 입력 |
| 실행 상한 | 로컬 클라이언트 1개, 중복 제거된 구독 최대 100개, 실행 300초, 출력 1,000건 |
| 부하 제한 | 구독 20개 / 400ms, STOMP 프레임 256KiB, WebSocket 수신 메시지 1MiB |
| 메모리·출력 | 게스트 연결값은 메모리에서만 사용하고 제거하며, allowlist 필드만 JSONL로 출력; 첫 이벤트 즉시 flush 후 20건 또는 500ms 단위 flush |
| 장애·종료 | 자동 재연결 없이 오류에서 중단; 정상 종료 시 `UNSUBSCRIBE` 후 `DISCONNECT` 영수증을 최대 1초 대기 |

top100 전용 WebSocket 채널은 확인되지 않았습니다. top100은 10초 주기 HTTP 랭킹 snapshot으로 종목 목록을 얻고, 한 화면의 종목 코드만 최대 100개 체결 destination으로 구독하는 혼합 구조입니다. 현재 최소 클라이언트는 랭킹 자동 갱신을 하지 않으므로 `dashboard_ranking.py`로 snapshot을 조회한 뒤 필요한 종목만 명시적으로 구독해야 합니다.

유지보수자는 다음 명령으로 WebSocket 방어 로직과 전체 회귀 테스트를 재현할 수 있습니다.

```bash
python3 -m unittest tests.test_websocket_prices -v
python3 -m unittest discover -s tests -v
python3 -m ruff check .
python3 -m ruff format --check .
python3 -m pip install --dry-run -r requirements-websocket.txt
python3 -m pip check
```

네트워크가 허용된 환경에서는 다음 명령으로 비로그인 공개 스트림을 짧게 확인할 수 있습니다. 이벤트 발생 여부와 값은 시장 상태에 따라 달라집니다.

```bash
python3 scripts/websocket_prices.py --crypto VWAP.KRW-BTC --duration 15 --max-events 1
```

주식 요약:

```bash
python3 scripts/stock_summary.py --code A005930 --no-overview
```

```json
{
  "code": "A005930",
  "info": {
    "code": "A005930",
    "name": "삼성전자",
    "market": "KOSPI",
    "companyCode": "005930"
  },
  "price": {
    "code": "A005930",
    "close": 70000,
    "changeType": "RISE",
    "volume": 12345678
  },
  "overview": null
}
```

차트와 로컬 보조지표:

```bash
python3 scripts/stock_chart.py --code A005930 --range day:1 --count 61 --rsi-period 14 --macd
```

```json
{
  "code": "A005930",
  "chart": {
    "code": "A005930",
    "candles": [
      {
        "dt": "2026-04-20T00:00:00+09:00",
        "close": 70000,
        "volume": 12345678
      }
    ]
  },
  "technicalIndicators": {
    "rsi": {
      "period": 14,
      "source": "local calculation from c-chart close prices"
    },
    "macd": {
      "fastPeriod": 12,
      "slowPeriod": 26,
      "signalPeriod": 9,
      "source": "local calculation from c-chart close prices"
    }
  }
}
```

## 프롬프트 예시

처음 써볼 때는 이런 요청이 유용합니다.

```text
토스증권 기준으로 A005930의 간단한 종목 요약과 현재 시세를 조회해줘.
토스증권 SOXL 메인에 보이는 왜 떨어졌을까 내용과 커뮤니티 댓글을 같이 조회해줘.
토스증권에서 A005930의 일봉 캔들을 조회하고 RSI 14와 MACD를 계산해줘.
TossInvest 스크리너에서 RSI 과매도 조건에 해당하는 한국 주식을 찾아줘.
토스증권에서 KGG01P의 KOSPI 지수 가격, 차트, 지수 관련 뉴스를 조회해줘.
토스증권에서 국내와 미국 거래대금 기준 실시간 차트 top100 랭킹을 조회해줘.
토스증권 비로그인 공개 페이지의 A005930 실시간 체결 WebSocket 채널과 수신 필드를 설명해줘.
문서화되지 않은 주식 페이지 엔드포인트를 찾기 위해 TossInvest 네트워크 호출을 조사해줘.
```

새로운 네트워크 호출을 조사하기 전에는 [references/capture-workflow.md](references/capture-workflow.md)와 [references/safety-rules.md](references/safety-rules.md)를 먼저 확인하세요.

## 저장소 구성

```text
tossinvest-api-skill/
├── SKILL.md
├── scripts/
├── references/
├── examples/
│   └── filters/
├── agents/
├── tests/
├── SECURITY.md
├── LICENSE
└── README.md
```

| 경로 | 용도 |
| --- | --- |
| `SKILL.md` | 에이전트가 읽는 라우팅 규칙, 안전 규칙, 작업 흐름 |
| `scripts/` | 시세, 차트, 재무, 랭킹, 스크리너, 뉴스, 공시, 테마, 지수, 투자자 동향 조회 스크립트 |
| `references/` | API 카탈로그, WebSocket API 레퍼런스, 네트워크 캡처 절차, 응답 노트, 안전 규칙, 스모크 테스트 프롬프트 |
| `examples/filters/` | 재사용 가능한 스크리너 필터 JSON 예시 |
| `agents/openai.yaml` | Codex/OpenAI 계열 도구에서 노출할 표시 메타데이터 |
| `tests/` | 스크립트 헬퍼와 엔드포인트 경로 생성 로직을 검증하는 유지보수자·CI용 테스트 |
| `SECURITY.md` | 민감한 엔드포인트, 개인정보, 자격 증명 처리 관련 제보 절차 |
| `LICENSE`, `LICENSE.txt` | MIT 라이선스 본문 |

유지보수자와 CI 검증에는 다음 명령을 사용합니다.

```bash
python3 -m unittest discover -s tests -v
```

릴리스 전에는 다음 검증도 함께 실행하는 것을 권장합니다.

```bash
for f in scripts/*.py; do python3 -m py_compile "$f" || exit 1; done
for f in scripts/*.py; do python3 "$f" --help >/dev/null || exit 1; done
for f in examples/filters/*.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
```

공개 릴리스 전에는 [.github/RELEASE_CHECKLIST.md](.github/RELEASE_CHECKLIST.md)를 함께 확인하세요.

## 안전 범위

이 프로젝트는 TossInvest 공식 API, 증권사 API, 거래 API, 투자 조언 도구가 아닙니다.

공개 주식·시장 페이지에서 확인할 수 있는 정보만 읽기 전용으로 조회하세요. 다음 용도로는 사용하지 않습니다.

- 로그인, 인증, 인증서, 쿠키, 인증 헤더, 세션 상태
- 계좌 잔고, 보유 종목, 이체, 주문, 주문 정정, 주문 취소
- 계좌 식별자, 개인 금융 데이터, 원본 HAR 저장, 접근 제어 우회
- 공개 TossInvest 웹 페이지에 보이지 않는 데이터 접근
- 크롤러, 배경 모니터, 대량 반복 조회처럼 동작하는 자동 수집
- 막힌 요청이나 비정상 응답을 우회하기 위한 자동 재시도

`wts-cert-api.tossinvest.com`은 민감한 호스트로 취급하세요. 공개 페이지에서 보이는 데이터나 메타데이터이고, 카탈로그에 있거나 스크립트로 검증된 엔드포인트군에 속하며, 쿠키·인증 헤더·계좌 식별자·개인 데이터가 필요 없을 때만 사용합니다.

요청이 막히거나 로그인/확인 화면으로 이어지면 자동 재시도를 멈추고, 현재 공개 웹 페이지에서 같은 데이터가 노출되는지 먼저 확인하세요. 이 프로젝트는 서비스 보호 장치나 접근 제어 흐름을 우회하지 않습니다.

민감한 엔드포인트, 개인정보, 자격 증명 처리 관련 제보는 [SECURITY.md](SECURITY.md)를 먼저 확인하세요. GitHub 이슈에는 쿠키, 토큰, 인증 헤더, 원본 HAR, 계좌·개인 금융 데이터를 올리지 마세요.

## 라이선스

MIT 라이선스입니다. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요.
