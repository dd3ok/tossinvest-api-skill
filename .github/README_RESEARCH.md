# 단일 API 스킬 저장소의 README 구성 조사

확인일: 2026-09-21. 대상: `dd3ok/tossinvest-api-skill`, `dd3ok/naverstock-api-skill`.

[공통 템플릿](README_TEMPLATE.md) · [토스 적용 미리보기](readme-examples/tossinvest.md) · [네이버 적용 미리보기](readme-examples/naverstock.md)

이 문서는 사람을 위한 README 템플릿의 편집 근거다. 아래 권고는 Agent Skills의 `SKILL.md` 형식 요건이나 모든 에이전트의 실행 호환성을 뜻하지 않는다. Anthropic도 자체 구현과 Agent Skills 표준을 구분한다. [Anthropic 원본 README](https://github.com/anthropics/skills#readme)

## 확인한 원본과 채택할 요소

| 원본 | 관찰 | 두 저장소에 적용할 요소 |
| --- | --- | --- |
| [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) | 용도·유용성·시작 방법·도움받을 곳을 안내하고, 긴 문서는 분리하도록 권장한다. | 처음 방문한 사람이 첫 조회까지 진행할 수 있는 순서. |
| [Matt Pocock: skills](https://github.com/mattpocock/skills#readme) | 소개 뒤에 설치를 두고, 설치 선택지를 접으며, 이후 문제별 설명과 참조 목록을 제공한다. | 앞부분의 설치 동선, 대안 설치법의 접기. 긴 철학 설명·뉴스레터·다중 스킬 목록은 가져오지 않는다. |
| [Anthropic: skills](https://github.com/anthropics/skills#readme) | 스킬의 목적을 설명하고 문서로 연결하며, Claude Code·Claude.ai·API의 이용 경로를 나눈다. | 환경별 설치·실행 조건을 명시하고 실제 요청 예시를 제공한다. |
| [Vercel: agent-skills](https://github.com/vercel-labs/agent-skills#readme) | 기능별 사용 상황, 설치 명령, 자연어 사용 예시, `SKILL.md`·스크립트·참조 문서 역할을 제시한다. | 사용자 요청 중심의 예시와 간결한 문서 안내. 전체 스킬 카탈로그 구조는 생략한다. |
| [RichardLitt: Standard Readme](https://github.com/RichardLitt/standard-readme), [자체 명세](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) | 설명→설치→사용을 구조화하고, 배너·배지는 선택 사항으로 정한다. | 재사용 가능한 섹션 순서와 예시 블록. 자체 명세의 모든 요건을 채택한 것은 아니므로 준수 배지를 붙이지 않는다. |
| [OpenAI: skills](https://github.com/openai/skills#readme) | 현재 README 맨 위에 폐기 안내가 있고 `openai/plugins`를 후속 예제로 안내한다. | 과거 README의 설치 안내를 최신 Codex 설치법의 근거로 사용하지 않는다. |

## 공통 템플릿을 위한 여섯 가지 결정

1. **첫 화면에서 목적과 범위를 설명한다.** 제목, 한두 문장 소개, 공개 데이터·읽기 전용·비공식이라는 범위를 먼저 둔다. 짧은 소개 다음에는 설치와 첫 사용이 이어지게 한다. 이 순서는 두 저장소에 맞춘 편집 선택이며, GitHub가 정한 필수 순서는 아니다. [GitHub 안내](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), [Standard Readme 명세](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)

2. **설치는 주 경로 하나를 먼저 보여준다.** 검증된 설치법과 필요한 실행 환경을 노출하고, 추가 호스트·프로젝트 전용 경로·개발용 링크는 접기 또는 설치 문서로 보낸다. 설치 후 인식할 스킬 이름과 확인 방법을 적는다. `npx skills`나 플러그인 명령은 우리 저장소에서 탐색·설치가 확인된 경우에만 채택한다. [Matt의 설치 구성](https://github.com/mattpocock/skills#installation-30-second-setup), [Anthropic의 환경별 이용 경로](https://github.com/anthropics/skills#try-in-claude-code-claudeai-and-the-api)

3. **첫 사용은 요청 하나와 CLI 하나로 끝낸다.** 서비스명을 포함한 자연어 요청과 대표 조회 명령을 제공한다. CLI 명령의 작업 디렉터리·Python 실행 파일·예상 출력 형식을 짧게 밝히고, 수십 개 명령은 쿡북으로 연결한다. 자연어 호출 방식은 호스트에 맞춰 검증한다. [Vercel의 사용 예시](https://github.com/vercel-labs/agent-skills#usage), [Standard Readme의 Usage](https://github.com/RichardLitt/standard-readme/blob/main/spec.md#usage)

4. **기능은 사용 목적별로 묶고 문서는 찾는 내용별로 연결한다.** 예를 들어 종목 조회·시장 조회·콘텐츠 조회처럼 3~5개 묶음을 쓰고, API 카탈로그·쿡북·제약·변경 이력으로 안내한다. 파일 목록을 그대로 늘어놓는 것보다 독자가 찾는 질문을 링크 이름에 담는다. 저장소 안의 링크는 상대 경로를 쓴다. [Vercel의 기능 설명](https://github.com/vercel-labs/agent-skills#available-skills), [GitHub의 상대 링크 안내](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes#relative-links-and-image-paths-in-markdown-files)

5. **배지는 사실 확인에 도움이 되는 항목만 남긴다.** 기존 CI·릴리스 등 2~3개 이내를 편집 기준으로 삼고 실제 대상에 연결한다. 이 개수는 자체 권고다. 릴리스 배지가 `main`의 검증 상태를 뜻하지 않도록 구분하고, 미검증 호스트 지원·마켓플레이스 등록 배지를 만들지 않는다. [Standard Readme의 선택적 배지와 과밀 방지 권고](https://github.com/RichardLitt/standard-readme#badge)

6. **운영·내부 설명은 연결 문서에서 읽게 한다.** 전체 파일 트리, 전체 CLI 옵션, 응답 스키마, 테스트 명령 모음, 감사 이력, 상세 안전 규칙의 중복은 본문에서 줄인다. 중요한 사용 경계와 문의·보안 제보·라이선스 링크는 남긴다. 짧은 README의 목차는 GitHub Outline 또는 간단한 바로가기로 충분하다. [GitHub의 문서 범위·자동 목차](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)

## 두 저장소에 적용할 때의 주의점

- 공통 순서는 **소개 → 설치 → 첫 사용 → 기능 → 문서 → 문의·라이선스**로 제안한다. 섹션과 정보의 역할을 공유하고, 서비스별 기능·조건·링크는 각각 채운다.
- 다중 스킬 컬렉션의 선택 UI, `/setup-matt-pocock-skills`, 플러그인 마켓플레이스 등록 절차는 해당 저장소의 배포 구성에 속한다. 단일 `SKILL.md` 저장소에 같은 명령이 제공된다고 추정하지 않는다. [Matt 원본](https://github.com/mattpocock/skills#installation-30-second-setup), [Anthropic 원본](https://github.com/anthropics/skills#claude-code)
- 로컬 `SKILL.md` 확인 기준, 설치 폴더명은 각각 `tossinvest-web-api`, `naverstock-web-api`다. 저장소 이름과 혼동하지 않게 템플릿 변수를 나눈다. [TossInvest 스킬 원문](../SKILL.md), [NaverStock 스킬 원문](https://github.com/dd3ok/naverstock-api-skill/blob/main/SKILL.md)
- 확인 시점의 실행 조건도 다르다. TossInvest는 Python 3.14.7을 지정하고 WebSocket 선택 의존성이 있으며, NaverStock은 Python 3.14 최신 패치를 지정한다. 공통 템플릿이 버전 정책이나 실시간 기능을 같게 만들어서는 안 된다. [TossInvest 현재 안내](../README.md), [NaverStock 현재 안내](https://github.com/dd3ok/naverstock-api-skill#readme)
- 설치 가능 여부, 스킬 검색 여부, Python·네트워크를 통한 실제 실행 가능 여부는 별도로 확인한다. 특정 저장소의 여러 호스트 지원 문구를 두 API 스킬의 전체 호스트 실행 보장으로 확대하지 않는다. [Anthropic의 환경별 안내·자체 환경 테스트 권고](https://github.com/anthropics/skills#readme)
- README 분량·접기 사용·배지 개수·위 순서는 이 조사에서 제안하는 편집 기준이다. `standard-readme`는 자체 명세이며 GitHub 또는 Agent Skills가 모든 README에 부과하는 형식은 아니다. [Standard Readme 명세](https://github.com/RichardLitt/standard-readme/blob/main/spec.md), [GitHub 안내](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)

## 템플릿 사용법

완성한 공통 순서는 **소개 → 설치 → 빠른 시작 → 지원 범위 → 문서 안내 → 한계와 안전 범위 → 개발 및 문의 → 라이선스**다.
소개에는 별도 제목을 붙이지 않고, CI·릴리스 배지 두 개와 한 번의 설치 요청을 노출한다. 추가 설치법만 `<details>`로 접는다.

두 미리보기는 각각 115줄이다. 이는 길이 제한이 아니라 현재 내용을 채운 결과다.
기준 파일은 TossInvest `652398a`, NaverStock `5aa856b`의 README·SKILL·CI다. 실제 두 저장소의 README 본문은 아직 교체하지 않았다.

| 채울 항목 | 템플릿 변수 | 토스 / 네이버의 차이 |
| --- | --- | --- |
| 이름과 출처 | `PROJECT_TITLE`, `REPOSITORY`, `PUBLIC_SOURCE`, `SKILL_NAME` | 브랜드·저장소 URL·공개 사이트·스킬 이름을 각각 기입 |
| 실행 환경 | `PYTHON_SUPPORT`, `OPTIONAL_RUNTIME_NOTE` | 토스 `3.14.7`과 WebSocket 선택 의존성 / 네이버 `3.14` 최신 패치 |
| 첫 조회 | `EXAMPLE_PROMPT`, `EXAMPLE_COMMAND` | 토스 `A005930 --no-overview` / 네이버 `005930 --include-industry` |
| 설치 경로 | `INSTALLATION_ROWS` | 현재 각 저장소에 안내된 호스트와 공식 문서만 유지 |
| 기능과 문서 | `CAPABILITY_ROWS`, `REFERENCE_ROWS` | 같은 표 형식에 각 프로젝트의 실제 기능·문서 링크를 기입 |
| 고유한 사용 경계 | `PROJECT_BOUNDARY_NOTE` | 토스 공식 OAuth API·메모리 내 게스트 값 / 네이버 REST polling·토론 정제 |
| 개발과 보안 | `MAINTENANCE_PATH`, `TEST_COMMANDS`, `SECURITY_NOTE` | 기존 유지보수 문서·필요 의존성·보안 제보 경로를 기입 |
| 문서 링크 기준 | `DOC_ROOT` | 실제 루트 README에 적용할 때 **빈 문자열**로 설정 |

`*_ROWS`에는 표의 헤더를 제외한 행을 넣는다. 선택 항목이 없으면 빈 문자열로 바꾸고 남는 빈 줄을 정리한다.
이 저장소 안에서 링크를 열 수 있도록 토스 미리보기는 `../../`, 네이버 미리보기는 해당 GitHub `blob/main/` 주소를 사용했다. 실제 적용 때는 템플릿의 `DOC_ROOT`를 비워 상대 링크로 만든다.

## 실제 README를 교체할 때

- 기존 README의 고유 기능·운영 제한·공개 인터페이스와 버전 정책을 해당 상세 문서에 먼저 옮기거나 기존 설명이 충분한지 확인한다. 예를 들어 토스 WebSocket 운영 수치와 top100 설명, 네이버 주요 버전 변경 기준을 단순 삭제하지 않는다.
- 기존 제목 앵커를 참조하는 링크를 확인한다. 토스의 `#스크립트-빠른-실행`, `#websocket-클라이언트-운영-제한` 등을 바꾸면 링크를 새 문서로 수정하거나 호환 앵커를 둔다.
- 복사한 README에서 `{{...}}`가 남지 않았는지, 상대 문서 링크·제목 앵커와 접기 영역이 열리는지 확인한다. 루트 적용본으로 GitHub 미리보기를 확인한다.
- `tests/test_docs.py` 등 기존 문서 검사에서 상세 설명을 README에 고정해 둔 항목은 설명이 이동한 실제 문서를 검사하도록 조정한다. 안전 경계와 링크 검증은 유지한다.
- 첫 CLI 예시의 옵션은 해당 저장소의 `--help`로 확인한다. 템플릿 적용 자체가 호스트 추가 지원이나 새로운 API 검증을 뜻하지 않는다.
