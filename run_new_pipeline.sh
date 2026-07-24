#!/usr/bin/env bash
# Daily AI Digest - New Python Pipeline
# Runs: scrape → classify/filter → generate markdown → build → push

set -e

BASE_DIR="/home/lancerloki/ai-digest-site"
LOG_DIR="$HOME/.hermes/digests"
TIMESTAMP=$(date +%Y%m%d_%H%M)
LOG_FILE="$LOG_DIR/cron_new_$TIMESTAMP.log"
DATE_STR=$(date +%Y-%m-%d)
DISPLAY_DATE=$(date +"%B %d, %Y")

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "============================================================"
log "DAILY AI DIGEST (NEW PIPELINE) - $DISPLAY_DATE"
log "============================================================"

cd "$BASE_DIR"

# Step 1: Search & scrape AI news
log "[1/5] Searching & scraping AI news..."
if ! python3 daily_run.py >>"$LOG_FILE" 2>&1; then
    log "ERROR: daily_run.py failed"
    exit 1
fi

# Step 2: Generate markdown post
log "[2/5] Generating blog post..."
if ! python3 generate_post.py >>"$LOG_FILE" 2>&1; then
    log "ERROR: generate_post.py failed"
    exit 1
fi
POST_PATH="$BASE_DIR/posts/$DATE_STR-daily-ai-digest.md"
if [ -f "$POST_PATH" ] && [ -s "$POST_PATH" ]; then
    log "  Post written: $(wc -l < "$POST_PATH") lines"
else
    log "ERROR: Post file missing or empty"
    exit 1
fi

# Step 3: Build site
log "[3/5] Building site..."
if ! python3 build.py >>"$LOG_FILE" 2>&1; then
    log "ERROR: Site build failed"
    exit 1
fi
BUILT_COUNT=$(find "$BASE_DIR/dist/posts" -name '*.html' | wc -l)
log "  Site built: $BUILT_COUNT HTML pages"

# Step 4: Generate Instagram content (non-fatal)
log "[4/5] Generating Instagram content..."
python3 generate_images.py "$POST_PATH" >>"$LOG_FILE" 2>&1 || log "  Image gen failed (non-fatal)"
python3 gen_caption.py >>"$LOG_FILE" 2>&1 || log "  Caption gen failed (non-fatal)"

# Step 5: Git commit & push
log "[5/5] Git commit & push..."
git config user.email 'hermes@termux' 2>/dev/null || true
git config user.name 'Hermes' 2>/dev/null || true
git add -A

if ! git diff --quiet --cached; then
    git commit -m "Add Daily AI Digest for $DATE_STR" >>"$LOG_FILE" 2>&1
    if git push origin main >>"$LOG_FILE" 2>&1; then
        log "  ✓ Pushed to GitHub (Cloudflare Pages auto-deploy)"
    else
        log "ERROR: git push failed"
        exit 1
    fi
else
    log "  No changes to commit"
fi

log "============================================================"
log "DIGEST COMPLETE - $DISPLAY_DATE"
log "============================================================"

echo "Daily AI Digest for $DATE_STR is live."
echo "  https://daily-ai-digest.freelancerloki.workers.dev/"
echo "  Instagram: $BASE_DIR/instagram_posts/"

exit 0