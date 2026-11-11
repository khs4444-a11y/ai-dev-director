# 04. Worktree 격리 및 복구 매뉴얼

Git worktree는 원본의 미커밋 변경을 복사하지 않으며 브랜치/객체 저장소를 공유한다.
따라서 절대적인 무위험 롤백을 보장하지 않는다. 아래 절차는 사용자 checkout을 보호하는
운영 규약이며 OS 실행 격리는 03 문서를 따른다. 명령 예시는 PowerShell, 저장소 루트 기준이다.

```powershell
git status --porcelain=v1
git rev-parse --show-toplevel
git rev-parse HEAD
git worktree list --porcelain
# 사용자 checkout이 dirty면 중단: 자동 stash/reset/clean 금지
$taskId = 'demo-001' # 실제로는 UUID 사용
$baseCommit = git rev-parse HEAD
$taskPath = Join-Path (Split-Path (Get-Location).Path -Parent) "agent-worktrees/$taskId"
git worktree add -b "agent/$taskId" "$taskPath" "$baseCommit"
git -C "$taskPath" status --porcelain=v1
```

매 명령의 exit code를 확인한다. 실제 감독은 경로를 정규화하고 관리 루트 내부인지,
기존 경로/브랜치 충돌이 없는지, symlink/reparse가 없는지 먼저 검증한다. 작업별 branch와
lock을 생성하고 base SHA를 저장한다. 사용자 checkout의 .git 파일/공용 gitdir는 agent에게 쓰기 금지한다.
감독만 Git 메타데이터를 변경하고 잠금을 관리한다.

각 gate 뒤 staged/unstaged/untracked/deleted/rename을 검사한다. 전역 정책과 TaskSpec 교집합으로
경로와 budgets를 검사한 뒤 명시적 경로만 stage하고 checkpoint commit을 만든다.
AI에 git add -A/commit 권한을 넘기지 않는다. RED 테스트와 증거도 checkpoint로 고정한다.
프로세스가 살아 있는 동안 checkpoint나 diff 검사를 최종 증거로 확정하지 않는다.

실패 복구: 프로세스 트리 종료 → 변경 목록/허용된 patch/로그 해시를 외부 artifact 루트에 보존
→ 실패 worktree를 격리 상태로 표시 → 마지막 성공 checkpoint에서 새 branch/worktree 생성.
원본 checkout에 reset --hard, clean -fd, checkout .을 실행하지 않는다. 실패 branch는 조사 가능하게 보존한다.

최종 통합: VERIFY 후보 SHA와 승인 SHA가 일치하고 target branch가 TaskSpec.base_commit 그대로인지
확인한다. 사람이 승인한 뒤 별도 integration worktree에서 ff-only 통합한다. target이 이동했거나
충돌하면 자동 해결/force-push 없이 새 base에서 새 작업을 만들고 전체 검증을 반복한다.
기존 target branch가 다른 worktree에 체크아웃되어 있으면 몰래 ref를 이동하지 않고 사용자가
해당 checkout에서 검증된 fast-forward를 수행하거나 PR로 통합한다. push는 별도 명시적 권한이 필요하다.

```powershell
# 종료 및 산출물 보존 후, 대상 경로와 clean 상태를 확인한 경우에만
git worktree list --porcelain
git -C "$taskPath" status --porcelain=v1
git worktree remove "$taskPath"
# remove가 dirty로 거부하면 --force 사용 없이 보존하고 조사
```

branch 삭제는 보존 기간/통합 확인 뒤 별도 수행한다. 공유 저장소에 자동 prune을 실행하지 않는다.
OS 격리 밖 파일, 네트워크 작업, 외부 서비스 변경은 worktree로 복구되지 않는다.
