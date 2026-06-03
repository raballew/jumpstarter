#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOW_FILE="$REPO_ROOT/.github/workflows/delete-stale-branches.yaml"
PASS=0
FAIL=0

assert() {
    local description="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        PASS=$((PASS + 1))
        echo "  PASS: $description"
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL: $description"
    fi
}

assert_grep() {
    local description="$1"
    local pattern="$2"
    if grep -q "$pattern" "$WORKFLOW_FILE" 2>/dev/null; then
        PASS=$((PASS + 1))
        echo "  PASS: $description"
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL: $description"
    fi
}

echo "=== Delete Stale Branches Workflow Tests ==="
echo ""

echo "--- File existence ---"
assert "Workflow file exists" test -f "$WORKFLOW_FILE"

echo ""
echo "--- YAML validity ---"
assert "File is valid YAML" python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_FILE'))"

echo ""
echo "--- Trigger configuration ---"
assert_grep "Has schedule trigger" "schedule:"
assert_grep "Has cron expression" "cron:"
assert_grep "Has workflow_dispatch trigger" "workflow_dispatch:"
assert_grep "Has dry_run input" "dry_run:"

echo ""
echo "--- Job structure ---"
assert_grep "Has jobs section" "jobs:"
assert_grep "Runs on ubuntu" "ubuntu-"

echo ""
echo "--- Permissions ---"
assert_grep "Has contents write permission" "contents: write"

echo ""
echo "--- Branch logic ---"
assert_grep "Uses gh api for branches" "gh api"
assert_grep "Checks protected branches" "protected"
assert_grep "Checks for open pull requests" "pulls"
assert_grep "Uses GITHUB_TOKEN" "GITHUB_TOKEN"
assert_grep "Has 30-day threshold" "30"

echo ""
echo "--- Dry-run support ---"
assert_grep "References dry_run in script" "dry_run"

echo ""
echo "--- Orphan branch handling ---"
assert "Orphan branches are treated as stale, not skipped" \
    python3 -c "
import yaml, sys
wf = yaml.safe_load(open('$WORKFLOW_FILE'))
script = wf['jobs']['delete-stale-branches']['steps'][0]['run']
# The script must NOT skip branches with no commit data.
# Instead, orphan branches (empty last_commit_date) should be treated as stale.
if 'SKIP (no commit data)' in script:
    sys.exit(1)
"

echo ""
echo "--- Delete error handling ---"
assert "Delete failures do not abort remaining branches" \
    python3 -c "
import yaml, sys
wf = yaml.safe_load(open('$WORKFLOW_FILE'))
script = wf['jobs']['delete-stale-branches']['steps'][0]['run']
# The gh api DELETE call must be wrapped in error handling so that
# a single branch delete failure does not abort the entire loop.
# Check that the delete line is guarded by 'if !' or '|| true' or similar.
lines = script.splitlines()
for line in lines:
    stripped = line.strip()
    if 'gh api -X DELETE' in stripped:
        # The raw delete call must NOT be on a bare line.
        # It should be wrapped in a conditional (if ! ... ; then) or have || to swallow errors.
        if stripped.startswith('gh api -X DELETE') or stripped.startswith('gh api  -X DELETE'):
            sys.exit(1)
sys.exit(0)
"

echo ""
echo "--- Branch name sanitization ---"
assert_grep "URL-encodes branch names" "@uri"
assert_grep "Validates branch names before processing" "invalid name"

echo ""
echo "--- Step summary ---"
assert_grep "Writes to GITHUB_STEP_SUMMARY" "GITHUB_STEP_SUMMARY"

echo ""
echo "--- No unnecessary checkout ---"
assert "Does not use actions/checkout" \
    bash -c "! grep -q 'actions/checkout' '$WORKFLOW_FILE'"

echo ""
echo "--- Delete operation ---"
assert_grep "Has branch delete command" "gh api.*DELETE\|git push.*--delete\|delete_ref\|DELETE"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
