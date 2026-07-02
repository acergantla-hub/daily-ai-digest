#!/bin/bash
set -e

WORKDIR="/c/Users/MYPC/daily-ai-digest"
cd "$WORKDIR"

echo "=== Hermes verification start ==="
echo "Running fetch_news.sh ..."
bash fetch_news.sh

echo "Checking created markdown file..."
TODAY=$(date +%Y-%m-%d)
MARKDOWN="posts/${TODAY}-ai-digest.md"
if [ ! -f "$MARKDOWN" ]; then
  echo "FAIL: $MARKDOWN not found"
  exit 1
fi
echo "Found $MARKDOWN"

echo "Checking latest commit message..."
COMMIT_MSG=$(git log -1 --pretty=%B)
if [[ "$COMMIT_MSG" != *"Auto-daily digest 2026-07-02"* ]]; then
  echo "FAIL: Commit message does not contain expected text"
  echo "Got: $COMMIT_MSG"
  exit 1
fi
echo "SUCCESS: Verification completed"
echo "=== Hermes verification end ==="