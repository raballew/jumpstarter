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
assert_grep "Uses actions/checkout" "actions/checkout@"

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
echo "--- Delete operation ---"
assert_grep "Has branch delete command" "gh api.*DELETE\|git push.*--delete\|delete_ref\|DELETE"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
