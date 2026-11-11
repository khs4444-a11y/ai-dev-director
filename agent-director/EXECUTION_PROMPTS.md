# 단계별 실행 프롬프트

각 블록을 Codex 또는 Claude에 전달한다. 한 번에 한 단계만 구현하고 결과 diff와 테스트 증거를 검토한다.
공통 계약: 기존 root 실행 코드를 보존한다. 작업은 agent-director/에 제한한다(CI 연동은 사전 명시).
docs/01~04와 ROADMAP을 먼저 읽고 문서·schema·모델의 불일치는 숨기지 말고 수정안을 설명한다.
비밀 출력, 파괴적 Git 명령, sandbox 우회, 승인 없는 publish/push는 금지한다.
범위 확대가 필요하면 변경을 멈추고 이유를 보고한다. 테스트 결과는 실행한 환경과 명령으로 보고한다.

## 1. 계약과 guard
> ROADMAP 1단계를 구현하라. 먼저 계약 fixtures와 보호 경로/절대 경로/UNC/drive/../rename/
> symlink/reparse/untracked/0 budget 반례 테스트를 작성하고 실패를 확인하라. 설정 검증 모델,
> 승인/취소/통합 이벤트, ScopeGuard 구현을 추가하라. 구조 검증과 권한 판정을 분리하고 정책은
> 항상 fail-closed로 처리하라. JSON Schema 재생성 drift를 검사하라. 실제 공급자 호출은 하지 말라.
> 산출: 변경 파일 목록, 실패→통과 증거, 남은 플랫폼 제약, 1단계 체크리스트.

## 2. Supervisor와 adapter
> 1단계 완료를 확인하고 ROADMAP 2단계를 구현하라. fake CLI로 child hang/output flood/timeout/
> cancellation/잘못된 JSON 테스트를 먼저 작성하라. POSIX process group과 Windows Job Object로
> 전체 트리를 종료하고 reap을 확인하라. wall/idle/deadline/output cap을 독립 적용하라.
> 공급자 adapter 옵션은 실제 설치 --help와 공식 문서로 확인하라. probe 실패를 정상 성공으로
> 대체하지 말라. 실계정 CLI smoke는 사용자 opt-in일 때만 수행하라. Antigravity가 headless를
> 지원하지 않으면 disabled를 유지하라. 산출: capability matrix, 테스트 증거, secret 없는 진단.

## 3. Worktree와 5 gate
> 1~2단계 완료를 확인하고 ROADMAP 3단계를 구현하라. disposable Git fixture에서만 테스트하라.
> 사용자 dirty checkout 불변 테스트를 먼저 작성하라. RED assertion과 테스트 hash를 고정하고,
> GREEN 이후 삭제/skip/완화는 거부하라. 감독이 GateResult를 발급하고 commit/task/request/attempt/
> artifact hash를 검증하라. SQLite transaction/CAS와 single-writer lock을 구현하라.
> 승인 전 merge/push 금지. 산출: 5 gate E2E trace, rollback 증거, README 갱신.

## 4. Failover와 복구
> 3단계 완료를 확인하고 ROADMAP 4단계를 구현하라. 공급자 장애/JSON 오류/의미적 실패/정책 위반을
> 구별하라. 공유 시도 예산과 circuit breaker를 저장하고 재시작해도 유지하라. 이전 트리 종료가
> 확인되어야 다음 공급자를 시작하라. 독립 reviewer가 없으면 blocked. kill 지점 fault injection,
> PID 재사용, 중복 완료 이벤트, 동시 writer, stale commit 반례를 테스트하라.
> 산출: 실패 행렬, 복구 trace, docs/03 정책과 구현의 대응표.

## 5. 원클릭 진입점과 릴리스 준비
> 1~4단계 완료를 확인하고 ROADMAP 5단계를 구현하라. doctor/plan/run/status/cancel/approve,
> dry-run과 Windows/POSIX bootstrap을 추가하라. 의존성 lock과 공급자 사전진단을 수행하라.
> 깨끗한 fixture에서 한 명령 E2E를 검증하라. 최종 SHA 승인과 base 이동 거절을 테스트하라.
> 승인 없는 실제 대상 병합/push는 하지 말라. CI를 OS별로 실행하고 미검증 플랫폼을 명시하라.
> 산출: 실행 가능한 launcher, 설치·복구 안내, 검증 기록, 미해결 제한. 실행하지 않은 검증은
> 통과로 기록하지 말라. 출시 준비와 외부 배포는 분리하여 보고하라.
