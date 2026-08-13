#!/usr/bin/env bash
# Idempotent OpenSpec check/install/init for a target repo. Fails soft:
# always exits 0, since KB generation must succeed even if this doesn't.
#
# Usage: openspec_setup.sh <target-repo-path>
set -u

TARGET="${1:?usage: openspec_setup.sh <target-repo-path>}"

if [ -d "$TARGET/openspec" ]; then
    echo "openspec already initialized in $TARGET" >&2
    exit 0
fi

if ! command -v openspec >/dev/null 2>&1; then
    echo "openspec CLI not found — installing @fission-ai/openspec" >&2
    if ! command -v npm >/dev/null 2>&1; then
        echo "WARN: npm not available — skipping OpenSpec setup (fail-soft)" >&2
        exit 0
    fi
    if ! npm install -g @fission-ai/openspec@latest; then
        echo "WARN: openspec install failed — skipping OpenSpec setup (fail-soft)" >&2
        exit 0
    fi
fi

if ! openspec init "$TARGET" --tools claude --no-animation; then
    echo "WARN: openspec init failed — skipping OpenSpec setup (fail-soft)" >&2
    exit 0
fi

echo "openspec initialized in $TARGET" >&2
