# agent-director 설계 패키지

Codex, Claude, Gemini 및 capability 확인 후 Antigravity를 조합하는 개발 감독관의 사전 설계다.
기획·구현·독립 검토와 TDD 5 gate를 통해 작업 범위와 검증 증거를 관리한다.

**현재는 scaffolding이며 실행 엔진/CLI/원클릭 launcher는 구현하지 않았다.** 기존 저장소 루트의
v3 실행 코드와 독립적이다. 추후 개발은 아래 순서로 즉시 시작할 수 있다.

1. [아키텍처](docs/01_ARCHITECTURE.md), [계약](docs/02_SPECIFICATION.md),
   [장애 정책](docs/03_FAILOVER_POLICY.md), [Worktree](docs/04_WORKTREE_GUIDE.md)를 읽는다.
2. Python 3.11+로 개발 환경을 만든다. 아래 명령은 저장소 루트에서 시작한다.
3. [ROADMAP](ROADMAP.md) 1단계와 [실행 프롬프트](EXECUTION_PROMPTS.md)의 첫 블록부터 진행한다.

```powershell
cd agent-director
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/export_schemas.py --check
```

POSIX는 `.venv/bin/python`을 사용한다. CLI 구독/설치/인증은 별도이며 비용·사용량 제한은
공급자 조건을 따른다. 모델명과 CLI 옵션은 이 설계에서 확정하지 않는다.
`config.example.yaml`은 향후 설정 템플릿이다. 지금 실행되지 않으며 secret을 넣지 않는다.
전역 보호 규칙은 작업 중 완화할 수 없다. Worktree는 OS sandbox가 아니므로 docs/03의 실행 격리가 필요하다.

`src/`는 의도적으로 런타임 동작이 없는 추상 인터페이스와 Pydantic 계약만 담는다.
`schemas/`는 생성된 wire JSON Schema, `tests/`는 계약 검증이다. 패키지 import 경로는 `src.*`로 고정한다.
장기 공개 라이브러리로 배포할 경우 패키지명 변경은 별도 호환성 결정으로 다룬다.

이슈 템플릿 원본은 `.github/ISSUE_TEMPLATE/`, GitHub 활성 복사본은 저장소 루트의 같은 경로다.
각 단계에서 작업 범위·실패 테스트·통과 증거·복구 방법을 채운다.
