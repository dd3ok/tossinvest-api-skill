# 토스증권 API Skill

<a id="비공식-토스증권-api-tossinvest-api-skill"></a>

[![CI](https://github.com/dd3ok/tossinvest-api-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/dd3ok/tossinvest-api-skill/actions/workflows/ci.yml) [![최신 릴리스](https://img.shields.io/github/v/release/dd3ok/tossinvest-api-skill?sort=semver)](https://github.com/dd3ok/tossinvest-api-skill/releases/latest)

`tossinvest.com`의 공개 주식·시장 데이터를 **에이전트와 Python CLI에서 읽기 전용으로 조회**하는 스킬입니다.
비공식 프로젝트이며 로그인·계좌·주문이나 투자 조언은 지원하지 않습니다.

[설치](#설치) · [빠른 시작](#빠른-시작) · [지원 범위](#지원-범위) · [문서 안내](#문서-안내) · [변경 이력](CHANGELOG.md)

---

## 설치

Codex에서는 다음과 같이 요청하세요.

```text
https://github.com/dd3ok/tossinvest-api-skill 에서 스킬을 설치해줘.
```

설치 후 스킬 목록에서 `tossinvest-web-api`가 보이는지 확인하세요. 설치 폴더명도 이 이름을 사용합니다.

<details>
<summary>직접 설치하거나 다른 에이전트에서 사용하기</summary>

Codex 개인 스킬 경로에 직접 설치하는 예시입니다. 셸 명령은 Bash 기준입니다.

```bash
mkdir -p ~/.agents/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skill.git ~/.agents/skills/tossinvest-web-api
```

위 `git clone` 명령의 설치 경로를 아래 표에 맞게 바꾸세요.

| 호스트 | 설치 위치 | 안내 |
| --- | --- | --- |
| <a id="codex"></a>Codex | 개인 `~/.agents/skills/tossinvest-web-api` · 프로젝트 `.agents/skills/tossinvest-web-api` | [공식 안내](https://learn.chatgpt.com/docs/build-skills) |
| <a id="claude-code"></a>Claude Code | 개인 `~/.claude/skills/tossinvest-web-api` · 프로젝트 `.claude/skills/tossinvest-web-api` | [공식 안내](https://code.claude.com/docs/en/skills) |
| <a id="antigravity-cli"></a>Antigravity CLI | 프로젝트 `.agents/skills/tossinvest-web-api` | [공식 안내](https://antigravity.google/docs/skills) |
| <a id="hermes-agent"></a>Hermes Agent | 개인 `~/.hermes/skills/tossinvest-web-api` | [공식 안내](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/) |
| <a id="openclaw"></a>OpenClaw | 설정한 에이전트 workspace의 `skills/tossinvest-web-api` | [공식 안내](https://docs.openclaw.ai/tools/skills) |

위 clone 명령은 `main`을 설치합니다. 버전을 고정하려면 `--branch <태그>`를 추가하고 [릴리스 목록](https://github.com/dd3ok/tossinvest-api-skill/releases)의 실제 태그를 사용하세요.
최종 파일 위치는 `.agents/skills/tossinvest-web-api/SKILL.md`처럼 스킬 이름과 폴더명이 일치해야 합니다.
Antigravity CLI는 `agy` 실행 후 `/skills`에서 설치 여부를 확인하세요.
Hermes의 프로젝트 `.hermes/skills` 또는 `.agents/skills`를 사용하려면 해당 프로젝트가 신뢰된 상태여야 합니다.
OpenClaw에서는 `openclaw skills list --eligible`과 `openclaw skills info tossinvest-web-api`로 발견 여부를 확인하세요. Python은 실제 실행 호스트나 샌드박스에도 필요합니다.

`SKILL.md`, `scripts/`, `references/`는 호스트가 함께 사용하는 본체입니다.
`agents/openai.yaml`은 Codex용 표시 정보와 자동 호출 정책이며 다른 호스트의 권한·호출 설정을 대신하지 않습니다.
각 환경에서 [수동 점검 절차](references/eval-prompts.md#running-a-small-evaluation)에 따라 스킬 발견과 첫 조회를 확인하세요.

</details>

---

<a id="스크립트-빠른-실행"></a>
<a id="로컬-스크립트만-실행"></a>

## 빠른 시작

설치 후 새 대화에서 자연어로 요청하세요.

```text
토스증권 기준으로 A005930의 종목 요약과 현재 시세를 조회해줘.
```

직접 CLI를 실행할 때는 **Python 3.14.7**을 사용합니다. HTTP 조회는 표준 라이브러리로 실행합니다.
스킬이 설치된 폴더(저장소 루트)에서 다음 명령을 실행하면 JSON 결과가 출력됩니다.

```bash
python3 scripts/stock_summary.py --code A005930 --no-overview
```

`python3 --version`이 `Python 3.14.7`인지 확인하세요. Windows에서는 `py -3.14`로 바꿀 수 있지만, `3.14` 명령 이름만으로 패치 버전이 고정되지는 않습니다.
다른 작업 폴더에서는 로드된 `SKILL.md`가 있는 디렉터리를 기준으로 스크립트와 번들 파일의 절대경로를 사용하세요. 상대 입력·출력 경로는 실행한 작업 폴더 기준입니다.
전체 옵션은 `--help`, 다른 조회 방법은 [실행 예제](references/script-cookbook.md)를 참고하세요.

<details>
<summary>WebSocket 수신 설정</summary>

WebSocket 수신에만 잠금된 선택 의존성이 필요합니다. 프로젝트 전용 가상환경에 설치하세요.

```bash
python3.14 --version  # Python 3.14.7인지 확인
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-websocket.txt
.venv/bin/python scripts/websocket_prices.py --kr-stock A005930 --duration 10 --max-events 5
```

Windows에서는 `py -3.14 -m venv .venv`로 생성하고 `.venv/bin/python`을 `.venv/Scripts/python.exe`로 바꿉니다.
다른 채널은 [수신 예제](references/script-cookbook.md#real-time-websocket-streams)와 [WebSocket 클라이언트 운영 제한](#websocket-클라이언트-운영-제한)을 확인하세요.

</details>

미국 주식 차트에는 `US20100311002` 같은 TossInvest 상품/소스 코드가 필요합니다. `SPY`, `NVDA` 같은 표시 티커를 그대로 넣으면 HTTP 400이 날 수 있습니다. [코드 선택 안내](references/script-cookbook.md#charts-and-local-indicators)를 참고하세요.

<a id="프롬프트-예시"></a>

<details>
<summary>추가 요청과 랭킹 조회 예시</summary>

```text
토스증권에서 A005930의 일봉 캔들을 조회하고 RSI 14와 MACD를 계산해줘.
토스증권 비로그인 공개 페이지의 A005930 실시간 체결 WebSocket 채널과 수신 필드를 설명해줘.
```

```bash
python3 scripts/dashboard_ranking.py --kind live-chart --live-chart biggest_market_amount --market us --duration 20d
```

<a id="주식-요약-출력-예시"></a>
<a id="차트와-로컬-보조지표-출력-예시"></a>

전체 명령과 출력 해석은 [실행 예제](references/script-cookbook.md)와 [응답 설명](references/response-notes.md)을 참고하세요.

</details>

---

## 지원 범위

| 하고 싶은 일 | 제공 기능 |
| --- | --- |
| 종목 살펴보기 | 국내·미국 종목 요약, 현재가·호가, 재무·배당, 투자자 동향 |
| 차트 분석하기 | 캔들 조회와 RSI·SMA·EMA·MACD·Bollinger Bands의 로컬 계산 |
| 시장 탐색하기 | 검색, 랭킹, 섹터·ETF, 지수·환율·채권·원자재, 캘린더, 스크리너 |
| 공개 콘텐츠 읽기 | 뉴스·공시, 정제된 피드·종목/라운지 댓글·답글 |
| 실시간 데이터 받기 | 공개 주식 체결과 검증된 지수·가상자산형 지수의 제한된 WebSocket 수신 |

<details>
<summary>HTTP·차트·WebSocket 상세 기능과 운영 제한</summary>

### 공개 HTTP 기반 조회

- 종목 요약과 현재가·호가 스냅샷·장중 체결 틱 조회
- 재무제표, 실적 추정, 밸류에이션, 배당, 안정성 지표
- 공시, 뉴스, 피드 탐색, 시장 통합 검색, 테마/TICS와 관련 테마·섹터 종목/ETF
- KOSPI 같은 지수와 일별 시세표, 환율 차트와 위젯, 채권·원자재 지표
- 증시 캘린더, 경제지표·실적 발표 일정, 국내·해외 캘린더 탭
- 국내·미국 실시간 차트 top100와 `투자위험 주식 숨기기`, 투자자 매매 동향, 브로커 순위, 스크리너 조건 검색
- 공개 주식 메인 페이지의 AI·상태 보조 정보와 정제된 추천 피드·주식/라운지 댓글·답글·커뮤니티 게시물 퍼머링크·랭킹

### 차트 및 로컬 계산

- 일봉·주봉·월봉·분봉 차트
- RSI, SMA, EMA, MACD, Bollinger Bands 계산

### WebSocket API

- `scripts/websocket_prices.py`로 공개 국내·미국 주식 체결, 지수, 가상자산형 지수 이벤트를 제한된 시간·건수만큼 JSONL로 수신
- 서버·STOMP 연결·destination·`MESSAGE`·payload 필드는 [비공식 WebSocket API 레퍼런스](references/websocket-api-reference.md)에 정리
- 임시 게스트 연결값은 실행 중 메모리에서만 사용하며 CLI 인자·환경 파일·로그·출력·저장 파일에 남기지 않음
- 실수신이 확인된 공개 국내 지수(`KGG01P`, `QGG01P`)와 미국 지수(`COMP.NAI`, `SPX.CBI`, `RGI..VIX`, `SOX.NAI`)만 허용하고, 로그인 전환 또는 allowlist 밖 지수에서는 즉시 중단함
- 호가·예상체결·종목상태 채널은 공개 시장 데이터만 실험적으로 다루며 로그인·주문·계좌 작업과 연결하지 않음
- 국내·미국 top100은 단일 WebSocket 랭킹 채널이 아니라 10초 주기 HTTP 랭킹 snapshot과 최대 100개 종목별 체결 구독을 결합함
- 검색·산업·투자자 동향·조건검색·뉴스의 핵심 목록은 HTTP로 조회하며, 화면에 보이는 종목 가격은 공용 체결 이벤트가 덧씌워질 수 있음; `scripts/quote.py`의 현재가·호가·체결 틱은 HTTP 조회
- 구독·메모리·출력 제한은 [WebSocket 클라이언트 운영 제한](#websocket-클라이언트-운영-제한) 참고

### WebSocket 클라이언트 운영 제한

HTTP 조회 스크립트는 요청할 때 실행되고 응답을 받으면 종료하므로 별도의 상주 클라이언트나 추가 패키지가 필요하지 않습니다. 지속적으로 이벤트를 받는 `websocket_prices.py`만 `requirements-websocket.txt`의 선택 의존성을 사용합니다.

| 항목 | 현재 동작 |
| --- | --- |
| 지원 스트림 | 국내·미국 주식 체결, 공개 KR·US 지수, 검증된 `VWAP.KRW-*` 가상자산형 지수 |
| 공개 지수 allowlist | KR `KGG01P`, `QGG01P`; US `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, `SOX.NAI` |
| 가상자산형 지수 allowlist | `VWAP.KRW-BTC`, `VWAP.KRW-ETH`, `VWAP.KRW-XRP`, `VWAP.KRW-SOL` |
| 즉시 차단 | 로그인 전환 지수, allowlist 밖 지수, 임의 destination·서버 URL·인증값 입력 |
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

네트워크가 허용된 환경에서는 다음 명령으로 비로그인 공개 스트림을 짧게 확인할 수 있습니다. 이벤트 발생 여부와 값은 시장 상태에 따라 달라지며, 정상 종료했더라도 이벤트가 0건이면 해당 채널이나 필드를 확인한 것으로 보지 않습니다.

```bash
.venv/bin/python scripts/websocket_prices.py --crypto VWAP.KRW-BTC --duration 15 --max-events 1
```

</details>

---

## 문서 안내

| 찾는 내용 | 문서 |
| --- | --- |
| 실행 명령과 옵션 조합 | [실행 예제](references/script-cookbook.md) |
| API 목록과 확인 상태 | [API 카탈로그](references/api-catalog.md) |
| 종목 시세·차트·재무·공시 | [종목 API](references/api-stock.md) |
| 지수·환율·검색·랭킹·섹터·캘린더 | [시장 API](references/api-market.md) |
| 뉴스 탐색·피드·공개 댓글 | [피드·커뮤니티 API](references/api-community.md) |
| 실시간 채널·수신 필드·운영 제한 | [WebSocket 문서](references/websocket-api-reference.md) |
| 실제 스킬 선택·실행 비교 | [Codex 평가 기록](references/skill-evaluation-2026-09-21.md) |
| 응답 필드와 페이징 | [응답 설명](references/response-notes.md) |
| 허용 범위와 중단 조건 | [안전 규칙](references/safety-rules.md) |

---

## 한계와 안전 범위

- 공개 데이터만 조회합니다. 로그인·계좌·보유종목·주문·개인화·쓰기 작업은 지원하지 않습니다.
- 대량 수집과 접근 제어 우회를 하지 않습니다. HTTP 403·429, 챌린지 또는 로그인 전환이 발생하면 중단합니다.
- 비공식 API의 경로·응답·데이터 가용성은 예고 없이 바뀔 수 있습니다. CI 통과가 현재 API의 성공이나 모든 호스트의 실행을 보장하지는 않습니다.

<a id="안전-범위"></a>
<a id="공식-open-api와의-구분"></a>

이 스킬은 토스증권의 공식 Open API 클라이언트가 아니며, 공식 API 앱 설정·OAuth 토큰·계좌 헤더·IP 등록이 필요하지 않습니다. [공식 API와의 구분](references/official-openapi-boundary.md)을 참고하세요.
WebSocket의 임시 게스트 연결값은 실행 중 메모리에만 유지하고 출력·로그·파일에 남기지 않습니다.
`wts-cert-api.tossinvest.com`은 공개 페이지에서 확인되고 카탈로그에 있거나 스크립트로 검증된 엔드포인트군만 사용합니다. 쿠키·인증 헤더·계좌 식별자·개인 데이터가 필요한 요청은 제외합니다.
새 API를 조사할 때는 [캡처 절차](references/capture-workflow.md)와 [안전 규칙](references/safety-rules.md)을 먼저 확인하세요.

---

## 안정성 및 버전 정책

`v1.0.0`부터 다음 저장소 표면을 안정된 공개 계약으로 취급합니다.

- 스킬 이름 `tossinvest-web-api`와 `.agents/skills/tossinvest-web-api` 설치 경로
- `SKILL.md`, `scripts/`, `references/`, `agents/`를 포함한 설치 레이아웃
- 문서화된 CLI 명령과 옵션, 로그인·계좌·주문을 제외하는 안전 경계
- Python 3.14.7 CI 호환성, HTTP 표준 라이브러리 실행, WebSocket 선택 의존성 잠금 파일

이 버전 정책은 이 저장소가 제공하는 인터페이스에 적용됩니다. 토스증권 웹 API와 WebSocket 채널은 여전히 비공식·미문서화 인터페이스이며 예고 없이 경로, 응답 필드, 접근 가능 여부가 바뀔 수 있습니다. 외부 응답 필드와 데이터 가용성은 하위 호환성 계약에 포함하지 않으며, 관찰된 변경은 API 카탈로그의 상태 표기와 릴리스 노트에 기록합니다.

2026-09-07부터 Python 3.14.7만 지원·검증하며 기존 Python 3.12 지원은 종료했습니다.

---

## 개발 및 문의

<details>
<summary>저장소 구성</summary>

### 저장소 구성

| 경로 | 용도 |
| --- | --- |
| `SKILL.md` · `agents/openai.yaml` | 에이전트 작업 규칙과 Codex 표시·호출 설정 |
| `scripts/` · `examples/filters/` | 공개 조회 CLI와 스크리너 필터 예시 |
| `references/` | API 카탈로그, WebSocket API 레퍼런스, 실행 예제와 안전 규칙 |
| `tests/` · `.github/workflows/ci.yml` | 회귀 검사와 설치 검증 |
| `SECURITY.md` · `LICENSE` | 비공개 보안 제보와 MIT 라이선스 |

</details>

에이전트 작업 규칙은 [SKILL.md](SKILL.md)에 있습니다.
수정 후 저장소 루트에서 테스트하고, [유지보수 안내](.github/RELEASE_CHECKLIST.md)의 검증 절차를 따르세요.

```bash
python3 -m pip install -r requirements-websocket.txt
python3 -B -m unittest discover -s tests
```

이 README는 `main` 기준이며, 릴리스 배지는 가장 최근에 발행한 버전을 가리킵니다.
특정 릴리스의 지원 환경은 해당 태그의 README를, 미출시 변경과 호환성 안내는 [변경 이력](CHANGELOG.md)을 확인하세요.

오류나 문서 개선은 [Issues](https://github.com/dd3ok/tossinvest-api-skill/issues)로 알려주세요. 쿠키·토큰·원본 HAR·계좌 정보는 공개 이슈에 올리지 마세요.
민감한 보안 제보는 [SECURITY.md](SECURITY.md)의 비공개 제보 절차를 따르세요.

---

## 라이선스

[MIT](LICENSE)
