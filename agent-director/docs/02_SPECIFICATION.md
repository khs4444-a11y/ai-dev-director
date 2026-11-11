# 02. 입출력 계약 및 상태 머신

규범 소스는 `src/core/schema.py`와 `src/pipeline/states.py`이다. Pydantic v2
`model_json_schema()` 출력은 `schemas/*.schema.json`으로 버전 관리한다. 모델 변경 시 함께 재생성한다.
모든 메시지는 UTF-8 단일 JSON 객체, schema_version=1.0, 추가 필드 금지이다.
스트리밍 공급자 출력은 adapter가 최종 객체로 조립한다. 최대 바이트 초과/유효하지 않은 JSON은 실패한다.
stdout은 프로토콜, stderr는 제한·비밀 제거된 진단용이다. markdown fence를 묵시적으로 수용하지 않는다.

| 모델 | 방향 | 의미 |
|---|---|---|
| TaskSpec | 사용자/Planner → 감독 | 기준 커밋, 경로 allowlist, 수용 기준, 테스트 argv, 변경 예산 |
| AgentRequest | 감독 → adapter | UUID, 역할, gate, attempt, worktree, 후보 커밋, prompt |
| AgentResponse | adapter → 감독 | request 상관관계, 공급자, 종료 상태, 제한된 artifact 참조 |
| GateResult | 감독 → 상태 저장소 | 작업/요청/시도/후보에 귀속한 판정과 최소 1개 증거 |
| GuardDecision | guard → 감독 | 허용 여부, 위반, 파일/라인 변경량 |

```json
{"schema_version":"1.0","task_id":"11111111-1111-4111-8111-111111111111","objective":"빈 입력의 오류 계약 추가","repository":"/workspace/repo","base_commit":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","allowed_paths":["src/**","tests/**"],"acceptance_criteria":["빈 입력은 ValueError"],"test_commands":[{"argv":["python","-m","pytest","-q"],"timeout_seconds":120}],"max_changed_files":10,"max_changed_lines":500,"max_attempts":3}
```

구조 검증과 실행 권한 검증은 별개이다. 경로는 repo-relative POSIX 패턴으로 정의하며 `/`,
`..`, Windows drive/UNC, NUL, symlink/reparse 경유를 거부한다. 대소문자는 실제 파일시스템에 맞춰
정규화한다. 보호 규칙 > 작업 allowlist, 유효 예산은 전역·작업 제한의 최솟값이다. 0은 수정 금지이다.
삭제/추가/rename 양쪽 경로와 untracked 파일도 계산하고 변경 라인은 additions+deletions이다.
binary/submodule은 기본 거부한다. 정책 파일은 작업 시작 시 trusted supervisor가 읽고 해시로 고정한다.
테스트 명령은 argv 단위 승인 후 실행하며 AI가 명령 allowlist나 정책을 확대할 수 없다.

| 현재 | 다음 | 요구 gate/outcome |
|---|---|---|
| created | planned | plan/pass |
| planned | red | red/pass (예상 assertion 실패를 확인했다는 의미) |
| red | green | green/pass |
| green | refactored | refactor/pass |
| refactored | verified | verify/pass |
| verified | awaiting_approval | 최종 후보와 verify 증거 동일, 감독 이벤트 |
| awaiting_approval | completed | 사람 승인 + 통합 성공 이벤트 |
| 모든 비종료 | failed | 예산 소진/안전 위반/복구 불가, 감독 이벤트 |
| 모든 비종료 | cancelled | 명시적 취소 + 프로세스 종료 확인, 감독 이벤트 |

failed/cancelled/completed는 종료 상태이다. gate fail/blocked는 진전하지 않으며 동일 상태에서
해당 gate만 예산 내 재시도한다. GateResult 기반 transition 인터페이스는 첫 5개 전이용이다.
승인/취소/통합 이벤트의 별도 인터페이스와 모델은 로드맵 1단계에서 정의한다.
후보가 VERIFIED 뒤 변경되거나 base branch가 이동하면 증거·승인을 무효화하고 새 작업으로 검증한다.

검증 순서: schema → request/task 매칭 → 허용 role/provider → gate/state 매칭 → attempt 범위와
중복 확인 → candidate HEAD 일치 → artifact 경로/실제 해시 확인 → 독립 테스트 판정 → CAS 저장.
AI는 GateResult를 권위 있게 발급할 수 없다. GuardDecision.allowed와 violations의 일관성도 감독이 검증한다.
오류·로그는 secret을 제거하고, artifact 경로는 증거 루트 아래 일반 파일만 허용한다.
