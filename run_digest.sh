#!/usr/bin/env bash
# Daily AI Digest - Automated Pipeline
# Runs the full workflow: scrape → write via Hermes → verify → build → instagram → push

set -e  # Exit on error

# Directory setup
BASE_DIR="/home/lancerloki/ai-digest-site"
SCRIPTS_DIR="/home/lancerloki/.hermes/scripts"
POSTS_DIR="$BASE_DIR/posts"
DIST_DIR="$BASE_DIR/dist"
IG_DIR="$BASE_DIR/instagram_posts"
TIMESTAMP=$(date +%Y%m%d_%H%M)
LOG_DIR="$HOME/.hermes/digests"
LOG_FILE="$LOG_DIR/cron_$TIMESTAMP.log"
DATE_STR=$(date +%Y-%m-%d)
DISPLAY_DATE=$(date +%B\ %d,\ %Y)

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$POSTS_DIR"
mkdir -p "$DIST_DIR/posts"
mkdir -p "$IG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "============================================================"
log "DAILY AI DIGEST PIPELINE - $DISPLAY_DATE"
log "============================================================"

cd "$BASE_DIR"

# Step 1: Scrape news
log "[1/7] Scraping news..."
if ! python3 "$SCRIPTS_DIR/daily-ai-digest.py" > "$BASE_DIR/today_news.txt" 2>>"$LOG_FILE"; then
    log "ERROR: News scraping failed"
    exit 1
fi
NUM_STORIES=$(grep -cE "^\s+[0-9]+\." "$BASE_DIR/today_news.txt" || echo 0)
log "  Scraped $NUM_STORIES stories"

# Step 2: Dedupe (already done in the scraper)
log "[2/7] Deduplicating news..."
DEDUPED="/tmp/today_news_deduped_$TIMESTAMP.txt"
DEDUP_BEFORE=$(grep -cE "^\s+[0-9]+\." "$BASE_DIR/today_news.txt" || echo 0)
awk '!seen[$0]++' "$BASE_DIR/today_news.txt" > "$DEDUPED"
DEDUP_AFTER=$(grep -cE "^\s+[0-9]+\." "$DEDUPED" || echo 0)
DUPES_REMOVED=$(( DEDUP_BEFORE - DEDUP_AFTER ))
if [ $DUPES_REMOVED -gt 0 ]; then
    log "  Removed $DUPES_REMOVED duplicate headline(s)"
    mv "$DEDUPED" "$BASE_DIR/today_news.txt"
else
    rm -f "$DEDUPED"
fi

# Step 3: Generate blog post via Hermes
log "[3/7] Generating blog post via Hermes..."
POST_PATH="$POSTS_DIR/$DATE_STR-daily-ai-digest.md"

# Check if post already exists (avoid overwriting)
if [ -f "$POST_PATH" ] && [ -s "$POST_PATH" ]; then
    log "  Post already exists ($(wc -l < "$POST_PATH") lines) - skipping LLM write"
else
    # Build prompt for Hermes
    PROMPT="You are the Daily AI Digest writer. Your job: read /home/lancerloki/ai-digest-site/today_news.txt (the freshly-scraped news for $DATE_STR) and write a markdown blog post for $DATE_STR.

OUTPUT FORMAT — strict:
Write exactly this file: /home/lancerloki/ai-digest-site/posts/$DATE_STR-daily-ai-digest.md

The file must look like an existing post in /home/lancerloki/ai-digest-site/posts/ — read 2026-07-1103-daily-ai-digest.md first to match the exact format (frontmatter, ### headings, key takeaways, link format, source pattern, why-it-matters section at the end).

REQUIREMENTS:
- Cover 12-15 of the most relevant stories from today_news.txt
- Each story: 3-5 sentence summary with concrete facts, not generic commentary
- Real URLs from today_news.txt for each link
- Real source names from today_news.txt for each source citation
- Each story gets 3-5 bullet 'Key Takeaways'
- Group stories roughly by theme (agents / models / business / research / hardware / policy)
- End with a 'Why This Matters Today' section synthesizing 3-4 themes
- Pick a topic set that is genuinely interesting and parses the world — do NOT just summarize headlines
- 12-15 stories; do not pad with weak items
- frontmatter tags should be concrete — list distinct topics covered
- Use the Write tool (write_file). That's it. No git, no build — another step handles that.
- DO NOT add anything to today_news.txt; only write the markdown file."

    if hermes chat -q "$PROMPT" >>"$LOG_FILE" 2>&1; then
        if [ -f "$POST_PATH" ] && [ -s "$POST_PATH" ]; then
            log "  Blog post written: $(wc -l < "$POST_PATH") lines, $(wc -c < "$POST_PATH") bytes"
        else
            log "ERROR: Blog post file missing or empty after LLM run"
            exit 1
        fi
    else
        log "ERROR: LLM invocation failed"
        exit 1
    fi
fi

# Step 4: Verify the post (basic checks)
log "[4/7] Verifying blog post..."
if [ ! -f "$POST_PATH" ] || [ ! -s "$POST_PATH" ]; then
    log "ERROR: Post file missing or empty"
    exit 1
fi

# Check for frontmatter
if ! grep -q "^---\s*$" "$POST_PATH"; then
    log "WARNING: Missing or malformed frontmatter"
fi

# Check for story sections (### headings, excluding Why This Matters)
STORY_COUNT=$(grep -E "^### .+" "$POST_PATH" | grep -v "Why This Matters" | wc -l)
if [ "$STORY_COUNT" -lt 10 ]; then
    log "WARNING: Only $STORY_COUNT story sections found (expected 12-15)"
elif [ "$STORY_COUNT" -gt 20 ]; then
    log "WARNING: $STORY_COUNT story sections found (seems too many)"
else
    log "  Found $STORY_COUNT story sections"
fi

# Check for Key Takeaways sections
KT_COUNT=$(grep -c -i "Key Takeaways" "$POST_PATH")
if [ "$KT_COUNT" -lt 10 ]; then
    log "WARNING: Only $KT_COUNT Key Takeaways sections found"
else
    log "  Found $KT_COUNT Key Takeaways sections"
fi

# Step 5: Build site
log "[5/7] Building site..."
if ! python3 "$BASE_DIR/build.py" >>"$LOG_FILE" 2>&1; then
    log "ERROR: Site build failed"
    exit 1
fi
BUILT_COUNT=$(find "$DIST_DIR/posts" -name '*.html' | wc -l)
log "  Site built - $BUILT_COUNT HTML pages in dist/posts/"

# Step 6: Generate Instagram images and caption
log "[6/7] Generating Instagram content..."
if python3 "$BASE_DIR/generate_images.py" "$POST_PATH" >>"$LOG_FILE" 2>&1; then
    IMG_COUNT=$(ls -1 "$BASE_DIR/instagram_posts"/*.png 2>/dev/null | wc -l)
    log "  Generated $IMG_COUNT Instagram images"
else
    log "WARNING: Image generation failed (non-fatal)"
fi

if python3 "$BASE_DIR/gen_caption.py" >>"$LOG_FILE" 2>&1; then
    log "  Caption generated"
else
    log "WARNING: Caption generation failed (non-fatal)"
fi

# Step 7: Git commit and push
log "[7/7] Git commit and push..."
# Configure git (if not already)
git config user.email 'hermes@termux' 2>/dev/null || true
git config user.name 'Hermes' 2>/dev/null || true

git add -A

# Check if there are changes to commit
if ! git diff --quiet --cached; then
    git commit -m "Add Daily AI Digest for $DATE_STR" >>"$LOG_FILE" 2>&1
    if git push origin main >>"$LOG_FILE" 2>&1; then
        log "  ✓ Pushed to GitHub (Cloudflare Pages will auto-deploy)"
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

# Output summary for cron delivery
echo "Daily AI Digest for $DATE_STR is live."
echo "  https://daily-ai-digest-10e.pages.dev"
echo "  $NUM_STORIES stories scraped."
echo "  Instagram: $BASE_DIR/instagram_posts/"

exit 0