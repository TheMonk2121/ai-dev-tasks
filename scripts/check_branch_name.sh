#!/usr/bin/env bash
# Check if branch name matches policy: main or type/B-####-short-slug

current_branch=$(git rev-parse --abbrev-ref HEAD)

# Allow main branch
if [ "$current_branch" = "main" ]; then
    exit 0
fi

# Check feature branch format: type/B-####-short-slug
if echo "$current_branch" | grep -E "^(feature|fix|chore|docs|ci|test)/B-[0-9]+-" >/dev/null; then
    exit 0
fi

echo "❌ BRANCH NAME POLICY VIOLATION: Branch '$current_branch' does not match policy."
echo "Allowed formats: 'main' or 'type/B-####-short-slug' (e.g., feature/B-1001-my-feature)"
exit 1
