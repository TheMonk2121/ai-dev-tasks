#!/bin/bash
# Check if current branch is main, exit with error if not

current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "main" ]; then
    echo "❌ BRANCH CREATION BLOCKED: You are on branch $current_branch. Only main branch is allowed without explicit permission."
    exit 1
fi
