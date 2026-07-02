#!/bin/bash
set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Generate markdown file for today
TODAY=$(date +%Y-%m-%d)
FILE=posts/${TODAY}-ai-digest.md

cat > "$FILE" <<EOF
---
title: "$TODAY"
date: $TODAY
---

# AI News Digest – $TODAY

*This is an automatically generated digest.*

- **Note**: This is a placeholder entry.
EOF

# Run the build script
python build.py

# Commit and push changes
git add "$FILE"
git commit -m "Auto-daily digest $TODAY" || echo "No changes to commit"
git push origin main