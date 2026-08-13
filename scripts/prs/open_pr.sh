#!/usr/bin/env bash
# Push a story branch and open a PR against the pinned base branch.
# Prints the PR URL on stdout on success (gh's default behavior).
#
# Usage: open_pr.sh <target-repo-path> <branch> <base-branch> <title> <body-file>
set -euo pipefail

TARGET="${1:?usage: open_pr.sh <target-repo-path> <branch> <base-branch> <title> <body-file>}"
BRANCH="${2:?branch required}"
BASE="${3:?base branch required}"
TITLE="${4:?title required}"
BODY_FILE="${5:?body file required}"

if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI not found. Install with 'brew install gh' then 'gh auth login'." >&2
    exit 1
fi

git -C "$TARGET" push -u origin "$BRANCH"

(cd "$TARGET" && gh pr create \
    --base "$BASE" \
    --head "$BRANCH" \
    --title "$TITLE" \
    --body-file "$BODY_FILE")
