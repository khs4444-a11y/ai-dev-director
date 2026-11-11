# 구현 로드맵

모든 단계는 먼저 실패 테스트 → 최소 구현 → 회귀 → 독립 검토 순서로 완료한다.
현재 완료 범위는 문서·추상 계약·스키마이다. 아래 런타임 체크박스는 아직 완료되지 않았다.

## 1단계: 계약과 정책 기반 (의존 없음)
- [ ] TaskSpec/요청/응답/GateResult 계약을 고정하고 fixtures와 schema 호환 테스트 추가
- [ ] 설정 모델과 설정 파일 검증기 구현; 알 수 없는 옵션·0 budget·경로 탈출 거부
- [ ] 승인/취소/통합 이벤트 모델과 terminal 상태 인터페이스 추가
- [ ] Safety guard 구현: rename 양끝, deletion, untracked, binary, Windows 경로/reparse 테스트
- [ ] JSON Schema 재생성과 drift 검사를 CI로 연결

완료 기준: 악성 경로/정책 완화/버전 불일치가 모두 fail-closed. 기존 root 테스트 영향 없음.

## 2단계: 감독 실행기와 CLI adapter (1 의존)
- [ ] async supervisor, wall/idle/output cap, cancellation, OS process-tree termination 구현
- [ ] Windows Job Object/POSIX process group, sandbox capability와 인증 broker 구현
- [ ] fake CLI로 hang/자식 생성/flood/비정상 JSON/실행 불가 테스트
- [ ] Codex·Claude·Gemini의 실제 설치 버전과 공식 옵션 확인 후 adapter 구현
- [ ] Antigravity headless capability 없으면 명시적 unavailable 유지

완료 기준: timeout 뒤 자손 0개, 버퍼 상한 준수, secret 미출력, 실제 CLI smoke는 opt-in.

## 3단계: Worktree·증거·TDD gate (1, 2 의존)
- [ ] 작업별 worktree/branch/lock/checkpoint와 artifact hash 저장 구현
- [ ] RED expected assertion 및 테스트 무결성 manifest 구현
- [ ] 5 gate FSM + SQLite 이벤트/상태 원자 저장 + 단일 supervisor lock 구현
- [ ] dirty 사용자 checkout 보존, 충돌/target 이동/허위 증거 테스트

완료 기준: 작은 fixture 저장소에서 RED→GREEN→REFACTOR→VERIFY, 원본 바이트 불변.

## 4단계: Failover와 재시작 복구 (3 의존)
- [ ] gate 공유 재시도 예산, deadline, backoff/circuit breaker 구현
- [ ] 독립 reviewer 제한과 checkpoint 기반 새 worktree 이관 구현
- [ ] kill 확인 불가 시 writer 차단, crash 후 PID 재사용/중복 이벤트 복구 테스트
- [ ] kill 지점별 fault injection과 재시도 시 증거/승인 무효화 테스트

완료 기준: 재시작해도 시도 예산 유지, 중복 전이 없음, 동시 writer 없음.

## 5단계: 진입점·통합·원클릭 개발환경 (4 의존)
- [ ] `agent-director doctor/plan/run/status/cancel/approve` CLI와 dry-run 구현
- [ ] Windows/POSIX bootstrap launcher와 lockfile, 의존성/CLI 사전진단 구현
- [ ] 사람 승인에 묶인 최종 SHA 통합, 이동한 base 거절, 명시적 push 옵션 구현
- [ ] CI: 계약/단위/fixture E2E 및 Windows/Linux 실행; macOS는 실기 검증 전 미검증 표시
- [ ] 설치/복구/로그 보존/플랫폼 지원표와 opt-in 실제 3공급자 E2E 기록

완료 기준: 깨끗한 환경에서 한 명령으로 bootstrap→doctor→fixture E2E. 실계정 smoke 결과와
지원 플랫폼을 기록한 후에만 원클릭 실행 가능으로 표시한다. 현재는 런처와 실행 명령이 없다.
