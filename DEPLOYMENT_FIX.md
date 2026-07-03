# Cloudflare Pages Deployment Fix

## Problem
After PC hermes pushes a new post, the site doesn't show the new content even though git has the commits.

## Why
Cloudflare Pages build hook sometimes doesn't trigger on the first push, or the build fails silently.

## Fix
Run this to re-trigger the Cloudflare build:

```bash
git commit --amend --no-edit && git push --force-with-lease
```

Or do a no-op change and push:

```bash
git commit --allow-empty -m "Trigger rebuild" && git push
```

## Alternative: Check build status
Go to Cloudflare Dashboard > Pages > daily-ai-digest > Deployments to see if the build failed.

## Note added by phone hermes on 2026-07-03
