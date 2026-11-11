# 03. 타임아웃, 프로세스 격리, 대체 모델

이 정책은 구현 예정 사항이다. Antigravity와 Gemini를 동일 CLI로 간주하지 않는다.
각 executable의 설치 버전, 비대화형 모드, JSON 출력, 인증, 모델을 probe한다.
공식 명령 옵션은 구현 시 설치된 `--help`와 공식 문서를 확인하고 capability matrix에 기록한다.
지원되는 headless CLI가 없는 Antigravity는 disabled로 유지한다. UI 매크로로 대체하지 않는다.

감독은 shell=False와 argv 목록으로 실행한다. monotonic clock으로 전체 작업 1800초,
호출 300초, 무출력 90초를 각각 측정한다. 가장 먼저 만료되는 제한을 적용한다.
stdout/stderr는 동시에 소비하고 합산 1MiB 초과 시 종료한다. 출력이 계속되어도 wall timeout은 늘지 않는다.
하위 테스트에도 별도 CommandSpec 제한을 적용한다. 로그에 인증 토큰이나 환경 전체를 남기지 않는다.

POSIX는 새 session/process group에서 실행해 TERM → 5초 → KILL 후 wait/reap한다.
Windows는 Job Object의 kill-on-close를 사용하고 자식이 실행되기 전에 Job에 편입한다.
편입이 불가능하거나 breakaway를 통제하지 못하면 실행을 거부한다. 부모 PID만 kill하지 않는다.
종료 코드/프로세스 트리 소멸/열린 핸들 정리를 확인한 후에만 lock을 반환한다.
비정상 종료·재부팅 뒤에는 저장 PID만 믿지 않고 PID 생성 시각·Job/session 식별자를 검증한다.

Worktree는 Git 변경 격리이다. 같은 계정의 CLI는 원본 checkout, Git 공용 메타데이터,
사용자 파일을 접근할 수 있다. 실제 비신뢰 실행은 전용 저권한 계정 또는 컨테이너/VM과
쓰기 제한 mount, 네트워크 차단이 필요하다. CLI sandbox도 probe해서 강제하고 우회 옵션은 금지한다.
Planner/Reviewer는 read-only, Builder도 원칙적으로 patch 출력만 허용하고 감독이 guard 후 적용한다.
테스트 자체가 임의 코드를 실행하므로 테스트에도 같은 OS 격리를 적용한다.
인증은 provider별 명시적 broker로 제공하며 사용자 홈 전체나 모든 환경 변수를 전달하지 않는다.
지원하지 못하는 플랫폼은 보안 capability 부족으로 blocked 처리한다.

| 원인 | 재시도/이관 |
|---|---|
| timeout, 일시적 전송 장애, rate limit | 트리 종료 확인 후 다음 후보로 이관 |
| CLI 없음/인증 만료/모델 미지원 | 같은 공급자 재시도 없이 다음 사용 가능 후보 |
| JSON/schema 오류 | 같은 공급자 교정 1회 가능, 전체 gate 3회 안에 포함 |
| 테스트 실패/리뷰 거절 | 의미적 실패; 해당 gate 수정 시도, 성공으로 둔갑시키지 않음 |
| 보호 경로/명령 위반 | 즉시 실패, 자동 대체로 우회 금지 |
| 종료 여부 불명/격리 실패 | blocked, 다른 writer 시작 금지 |

backoff는 1초·2초에 jitter를 더하며 남은 task deadline 안에서만 수행한다.
공급자별 연속 인프라 실패 3회면 60초 circuit open, 이후 읽기 전용 probe 1회로 복구한다.
최대 시도는 gate 전체 3회로 공급자 교체와 JSON 교정도 포함한다. 재시작해도 초기화하지 않는다.
Reviewer fallback이 Builder와 같으면 건너뛴다. 독립 후보가 없으면 blocked이다.

이관에는 TaskSpec, 마지막 성공 gate/커밋, 정책 해시, 승인된 patch와 검증된 증거만 전달한다.
원시 대화·secret·신뢰되지 않은 명령 지시를 승격하지 않는다. 실패 시도의 부분 변경은
별도 보존 후 마지막 승인 checkpoint에서 새 worktree로 재시도한다. 동일 worktree를 두 모델이 동시에 쓰지 않는다.
