<!-- {{...}}를 채워 저장소 루트의 README.md로 사용합니다. DOC_ROOT는 루트 적용 시 빈 문자열입니다. 작성 기준과 적용 예시는 README_RESEARCH.md를 참고하세요. -->
# {{PROJECT_TITLE}}

[![CI](https://github.com/{{REPOSITORY}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{REPOSITORY}}/actions/workflows/ci.yml) [![최신 릴리스](https://img.shields.io/github/v/release/{{REPOSITORY}}?sort=semver)](https://github.com/{{REPOSITORY}}/releases/latest)

`{{PUBLIC_SOURCE}}`의 공개 주식·시장 데이터를 **에이전트와 Python CLI에서 읽기 전용으로 조회**하는 스킬입니다.
비공식 프로젝트이며 로그인·계좌·주문이나 투자 조언은 지원하지 않습니다.

[설치](#설치) · [빠른 시작](#빠른-시작) · [지원 범위](#지원-범위) · [문서 안내](#문서-안내) · [변경 이력]({{DOC_ROOT}}CHANGELOG.md)

---

## 설치

Codex에서는 다음과 같이 요청하세요.

```text
https://github.com/{{REPOSITORY}} 에서 스킬을 설치해줘.
```

설치 후 스킬 목록에서 `{{SKILL_NAME}}`을 확인하세요. 설치 폴더명도 이 이름을 사용합니다.

<details>
<summary>직접 설치하거나 다른 에이전트에서 사용하기</summary>

Codex 개인 스킬 경로에 직접 설치하는 예시입니다. 셸 명령은 Bash 기준입니다.

```bash
mkdir -p ~/.agents/skills
git clone --depth 1 https://github.com/{{REPOSITORY}}.git ~/.agents/skills/{{SKILL_NAME}}
```

호스트에 따라 설치 위치 또는 명령을 바꾸세요.

| 호스트 | 설치 위치 또는 명령 | 안내 |
| --- | --- | --- |
{{INSTALLATION_ROWS}}

위 clone 명령은 `main`을 설치합니다. 버전을 고정하려면 `--branch <태그>`를 추가하고 [릴리스 목록](https://github.com/{{REPOSITORY}}/releases)의 실제 태그를 사용하세요.
설치 안내와 실제 호스트 실행 검증은 구분합니다. 각 환경에서 스킬 발견과 첫 조회를 확인하세요.

</details>

---

## 빠른 시작

설치 후 새 대화에서 자연어로 요청하세요.

```text
{{EXAMPLE_PROMPT}}
```

직접 CLI를 실행할 때는 **{{PYTHON_SUPPORT}}**를 사용합니다. HTTP 조회는 표준 라이브러리로 실행합니다.
저장소 루트에서 다음 명령을 실행하면 JSON 결과가 출력됩니다.

```bash
{{EXAMPLE_COMMAND}}
```

`python3`가 지원 버전인지 `python3 --version`으로 확인하세요. Windows에서는 설치 환경에 맞게 `py -3.14` 등으로 바꿉니다.
다른 작업 폴더에서는 설치된 스크립트의 절대경로를 사용하세요. 상대 입력·출력 경로는 실행한 작업 폴더 기준입니다.
전체 옵션은 `--help`, 다른 조회 방법은 [실행 예제]({{DOC_ROOT}}references/script-cookbook.md)를 참고하세요.

{{OPTIONAL_RUNTIME_NOTE}}

---

## 지원 범위

| 하고 싶은 일 | 제공 기능 |
| --- | --- |
{{CAPABILITY_ROWS}}

---

## 문서 안내

| 찾는 내용 | 문서 |
| --- | --- |
| 실행 명령과 옵션 조합 | [실행 예제]({{DOC_ROOT}}references/script-cookbook.md) |
{{REFERENCE_ROWS}}
| 응답 필드와 페이징 | [응답 설명]({{DOC_ROOT}}references/response-notes.md) |
| 허용 범위와 중단 조건 | [안전 규칙]({{DOC_ROOT}}references/safety-rules.md) |

---

## 한계와 안전 범위

- 공개 데이터만 조회합니다. 로그인·계좌·보유종목·주문·개인화·쓰기 작업은 지원하지 않습니다.
- 대량 수집과 접근 제어 우회를 하지 않습니다. HTTP 403·429, 챌린지 또는 로그인 전환이 발생하면 중단합니다.
- 비공식 API의 경로·응답·데이터 가용성은 예고 없이 바뀔 수 있습니다. CI 통과가 현재 API의 성공이나 모든 호스트의 실행을 보장하지는 않습니다.

{{PROJECT_BOUNDARY_NOTE}}

---

## 개발 및 문의

에이전트 작업 규칙은 [SKILL.md]({{DOC_ROOT}}SKILL.md)에 있습니다.
수정 후 저장소 루트에서 테스트하고, [유지보수 안내]({{DOC_ROOT}}{{MAINTENANCE_PATH}})의 검증 절차를 따르세요.

```bash
{{TEST_COMMANDS}}
```

이 README는 `main` 기준이며, 릴리스 배지는 가장 최근에 발행한 버전을 가리킵니다.
특정 릴리스의 지원 환경은 해당 태그의 README를, 미출시 변경과 호환성 안내는 [변경 이력]({{DOC_ROOT}}CHANGELOG.md)을 확인하세요.

오류나 문서 개선은 [Issues](https://github.com/{{REPOSITORY}}/issues)로 알려주세요. 쿠키·토큰·원본 HAR·계좌 정보는 공개 이슈에 올리지 마세요.
{{SECURITY_NOTE}}

---

## 라이선스

[MIT]({{DOC_ROOT}}LICENSE)
