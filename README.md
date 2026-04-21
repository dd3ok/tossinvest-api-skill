# TossInvest Web API Skill

[![TossInvest Web API CI](https://github.com/dd3ok/tossinvest-api-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/dd3ok/tossinvest-api-skills/actions/workflows/ci.yml)

`tossinvest.com` 주식/시장 페이지에서 브라우저 네트워크 탭으로 관찰되는 공개 read-only TossInvest/토스증권 웹 내부 API를 탐색하고 호출하기 위한 비공식 Agent Skill입니다.

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
- 대량 스크래핑, rate limit 우회, 공개 TossInvest 웹 페이지에 보이지 않는 데이터 접근

`wts-cert-api.tossinvest.com`은 현재 공개 페이지에서 public-looking metadata로 확인된 endpoint가 아니라면 민감한 host로 취급하세요. 이 API들은 문서화된 공개 API가 아니며 언제든 변경될 수 있으므로, 의존하기 전에 현재 브라우저 트래픽으로 다시 확인하는 것이 좋습니다.

## 빠른 시작

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

## 출력 형태 예시

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
Install the skill from https://github.com/dd3ok/tossinvest-api-skills
```

설치 후에는 Codex를 재시작해 skill 목록을 다시 로드하세요.

수동 설치:

```bash
mkdir -p ~/.agents/skills
git clone --depth 1 https://github.com/dd3ok/tossinvest-api-skills.git ~/.agents/skills/tossinvest-web-api
```

이미 clone한 작업 디렉터리를 쓰고 싶다면 symlink로 노출할 수도 있습니다.

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/tossinvest-api-skills ~/.agents/skills/tossinvest-web-api
```

프롬프트에서 명시적으로 호출할 수 있습니다.

```text
Use $tossinvest-web-api to get a compact stock summary and current quote for A005930.
```

특정 저장소 안에서만 쓰고 싶다면 이 저장소를 아래 위치에 복사하거나 vendor 형태로 포함하세요.

```text
.agents/skills/tossinvest-web-api/
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

Claude는 요청이 `SKILL.md`의 `description`과 맞으면 skill을 자동으로 선택합니다. 직접 요청할 수도 있습니다.

```text
Use the tossinvest-web-api skill to fetch daily candles and calculate RSI 14 for A005930.
```

## 프롬프트 예시

처음 써볼 때는 이런 요청이 유용합니다.

```text
Use $tossinvest-web-api to fetch KOSPI index price, chart, and index-related news for KGG01P.
Use $tossinvest-web-api to fetch domestic and US top100 live-chart rankings by trading amount.
Use $tossinvest-web-api to inspect TossInvest network calls for undocumented read-only stock-page endpoints.
```

새로운 네트워크 호출을 조사하기 전에는 [references/capture-workflow.md](references/capture-workflow.md)와 [references/safety-rules.md](references/safety-rules.md)를 먼저 확인하세요.

## 테스트

`tests/`는 maintainer와 CI를 위한 검증 코드입니다. 일반적인 skill 사용에는 필요하지 않습니다.

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
