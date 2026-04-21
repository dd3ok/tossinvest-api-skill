# TossInvest Web API Skill

[![TossInvest API Skills CI](https://github.com/dd3ok/tossinvest-api-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/dd3ok/tossinvest-api-skills/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/dd3ok/tossinvest-api-skills?sort=semver)](https://github.com/dd3ok/tossinvest-api-skills/releases/latest)

비공식 토스증권 API / TossInvest API read-only Agent Skill입니다. `tossinvest.com`의 공개 주식/시장 페이지에서 관찰되는 read-only 웹 내부 API를 안전하게 탐색하고 재조회합니다. 공식 API, 증권사 API, 거래 API가 아니라 공개 웹 페이지에 이미 보이는 주식/시장 데이터를 에이전트가 다시 확인하도록 돕는 도구입니다.

## 30초 요약

- 설치 후에는 TossInvest/토스증권을 언급한 자연어 요청으로 종목 요약, 시세, 차트, 재무, 뉴스, 공시, 테마, 지수, 랭킹, 스크리너를 조회할 수 있습니다.
- bundled Python scripts는 표준 라이브러리만 사용하며, API 호출 전에 host/path safety guard를 통과해야 합니다.
- 쿠키, 로그인, 계좌, 주문, raw HAR, 접근 제어 우회는 명시적으로 범위 밖입니다.
- undocumented internal API이므로 중요한 사용 전에는 현재 브라우저 트래픽으로 재확인하는 것을 전제로 합니다.

설치 후에는 이런 식으로 자연스럽게 요청할 수 있습니다.

```text
토스증권 기준으로 A005930의 간단한 종목 요약과 현재 시세를 조회해줘.
토스증권에서 A005930의 일봉 캔들을 조회하고 RSI 14와 MACD를 계산해줘.
TossInvest 스크리너에서 RSI 과매도 조건에 해당하는 한국 주식을 찾아줘.
```

## 지원 범위

- 종목 요약, 현재가, 호가, intraday ticks
- 일/주/월/min candle chart와 로컬 RSI, SMA, EMA, MACD, Bollinger Bands 계산
- 재무제표, 실적 추정, valuation, 배당, 안정성 지표
- 공시, 뉴스, feed discovery, theme/TICS, 관련 테마
- KOSPI 같은 지수, FX chart, 환율 widget, 채권/원자재 indicator
- 국내/미국 live-chart top100, 투자자 매매 동향, broker ranking, screener 조건 검색

## 구성

- `SKILL.md`: 에이전트가 읽는 라우팅 규칙, 안전 규칙, 작업 흐름
- `scripts/`: 시세, 차트, 재무, 랭킹, 스크리너, 뉴스, 공시, 테마, 지수, 투자자 동향을 조회하는 작은 Python 스크립트
- `references/`: API 카탈로그, 네트워크 캡처 절차, 응답 노트, 안전 규칙, 스모크 테스트 프롬프트
- `examples/`: 재사용 가능한 스크리너 필터 JSON 예시
- `tests/`: 스크립트 helper와 endpoint path builder를 검증하는 maintainer/CI용 테스트

## 안전 범위

이 프로젝트는 TossInvest 공식 API, 증권사 API, 거래 API, 투자 조언 도구가 아닙니다.

공개 페이지에서 확인 가능한 read-only 주식/시장 정보 조회에만 사용하세요. 다음 용도로는 사용하지 않습니다.

- 로그인, 인증, 인증서, 쿠키, authorization header, 세션 상태
- 계좌 잔고, 보유 종목, 이체, 주문, 주문 정정, 주문 취소
- 계좌 식별자, 개인 금융 데이터, raw HAR 저장, 접근 제어 우회
- 공개 TossInvest 웹 페이지에 보이지 않는 데이터 접근
- 크롤러, 배경 모니터, 대량 반복 조회처럼 동작하는 자동 수집
- 막힌 요청이나 비정상 응답을 우회하기 위한 자동 재시도

`wts-cert-api.tossinvest.com`은 현재 공개 페이지에서 public-looking metadata로 확인된 endpoint가 아니라면 민감한 host로 취급하세요. 이 API들은 문서화된 공개 API가 아니며 언제든 변경될 수 있으므로, 의존하기 전에 현재 브라우저 트래픽으로 다시 확인하는 것이 좋습니다.

요청이 막히거나 로그인/확인 화면으로 이어지면 자동 재시도를 멈추고, 현재 공개 웹 페이지에서 같은 데이터가 노출되는지 먼저 다시 확인하세요. 이 프로젝트는 서비스 보호 장치나 접근 제어 흐름을 우회하지 않습니다.

민감한 endpoint, privacy, credential-handling 관련 제보는 [SECURITY.md](SECURITY.md)를 먼저 확인하세요. GitHub issue에는 쿠키, token, authorization header, raw HAR, 계좌/개인 금융 데이터를 올리지 마세요.

## 스크립트 빠른 실행

번들 스크립트는 Python 표준 라이브러리만 사용하며, 네트워크 접근이 필요합니다.

```bash
python3 scripts/stock_summary.py --code A005930 --no-overview
python3 scripts/quote.py --code A005930 --ticks 5
python3 scripts/stock_chart.py --code A005930 --range day:1 --count 61 --rsi-period 14 --macd --bollinger-period 20
python3 scripts/financials.py --code A005930 --kind comprehensive
python3 scripts/screener_count.py --nation kr --rsi oversold --include-results --size 5
```

스크립트별 옵션은 `--help`로 확인합니다.

```bash
python3 scripts/stock_chart.py --help
```

더 많은 실행 예시는 [references/script-cookbook.md](references/script-cookbook.md)를, endpoint 목록은 [references/api-catalog.md](references/api-catalog.md)를 참고하세요.

## 출력 예시

실시간 값은 계속 바뀝니다. 아래 예시는 고정된 시장 데이터가 아니라 출력 구조를 보여주기 위한 sample shape입니다.

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

## Codex 설치

Codex에서 공개 GitHub URL로 설치를 요청할 수 있습니다.

```text
https://github.com/dd3ok/tossinvest-api-skills 에서 스킬을 설치해줘.
```

설치 후에는 Codex를 재시작해 skill 목록을 다시 로드하세요. 이후 TossInvest/토스증권을 언급한 주식 데이터 요청이 이 skill로 라우팅됩니다.

수동 설치:

```bash
CODEX_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$CODEX_SKILLS_DIR"
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skills.git "$CODEX_SKILLS_DIR/tossinvest-web-api"
```

이미 clone한 작업 디렉터리를 쓰고 싶다면 symlink로 노출할 수도 있습니다.

```bash
CODEX_SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$CODEX_SKILLS_DIR"
ln -sfn /path/to/tossinvest-api-skills "$CODEX_SKILLS_DIR/tossinvest-web-api"
```

특정 저장소 안에서만 쓰고 싶다면 이 저장소를 아래 위치에 복사하거나 vendor 형태로 포함하세요.

```text
.codex/skills/tossinvest-web-api/
```

## Claude Code 설치

Claude Code는 개인 skill 폴더와 프로젝트 skill 폴더에서 custom skill을 탐색합니다.

개인 설치:

```bash
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skills.git ~/.claude/skills/tossinvest-web-api
```

프로젝트 설치:

```bash
mkdir -p .claude/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skills.git .claude/skills/tossinvest-web-api
```

Claude는 TossInvest/토스증권 주식 데이터 요청이 skill 설명과 맞으면 이 skill을 자동으로 선택합니다.

## 프롬프트 예시

처음 써볼 때는 이런 요청이 유용합니다.

```text
토스증권에서 KGG01P의 KOSPI 지수 가격, 차트, 지수 관련 뉴스를 조회해줘.
TossInvest의 국내와 미국 거래대금 기준 live-chart top100 랭킹을 조회해줘.
문서화되지 않은 read-only 주식 페이지 endpoint를 찾기 위해 TossInvest 네트워크 호출을 조사해줘.
```

새로운 네트워크 호출을 조사하기 전에는 [references/capture-workflow.md](references/capture-workflow.md)와 [references/safety-rules.md](references/safety-rules.md)를 먼저 확인하세요.

## Maintainer Notes

`tests/`는 maintainer와 CI를 위한 검증 코드입니다. 일반적인 skill 사용에는 필요하지 않습니다.
공개 릴리스 전에는 [.github/RELEASE_CHECKLIST.md](.github/RELEASE_CHECKLIST.md)를 함께 확인하세요.

```bash
python3 -m unittest discover -s tests -v
```

릴리스 전에는 다음 검증도 같이 실행하는 것을 권장합니다.

```bash
for f in scripts/*.py; do python3 -m py_compile "$f" || exit 1; done
for f in scripts/*.py; do python3 "$f" --help >/dev/null || exit 1; done
for f in examples/filters/*.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
```

## 라이선스

MIT License입니다. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요.
