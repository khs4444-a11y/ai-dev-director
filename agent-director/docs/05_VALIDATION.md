# 설계 패키지 검증 기록

검증일: 2026-11-11 (Asia/Seoul). Windows, Python 3.12 가상환경.

| 검사 | 결과 |
|---|---|
| `python -m pip install -e '.[dev]'` | editable 설치 성공 |
| `python -m pytest -q` | 계약 테스트 9개 통과 |
| `python scripts/export_schemas.py --check` | 모델과 5개 JSON Schema 일치 |
| `python -m ruff check src tests scripts` | 통과 |
| `python -m pip check` | 의존성 충돌 없음 |
| YAML / JSON / TOML 파싱 | 통과 |

검증 의존성: Pydantic 2.14.3, pytest 9.2.0, PyYAML 6.0.3, GitPython 3.2.1,
psutil 7.2.2, Ruff 0.17.4. 현재는 범위 기반 의존성 명세이며 재현용 lockfile은 로드맵 5단계다.

추상 클래스 비인스턴스화, 잘못된 TaskSpec 거부, JSON 왕복, 0 budget 보존, 스키마 drift를
검사했다. 실행 엔진·실제 공급자 CLI·프로세스 종료·OS sandbox·worktree 복구·기존 v3 런타임
전체 회귀는 이 패키지의 검증 대상이 아니며 이번 작업에서 실행하지 않았다.
