# Daily AI Digest — Newsletter System

## Architecture

```
Visitor → Subscribe Form (index.html) → Cloudflare Worker API → Cloudflare D1 (SQLite)
                                                                        ↓
You write post → cron pipeline → send_newsletter.py → Worker /api/send → Resend → All subscribers
```

## What's in this folder

| File | Purpose |
|------|---------|
| `worker.js` | Cloudflare Worker — subscribe, unsubscribe, list, send |
| `schema.sql` | D1 database schema (subscribers + send log) |
| `wrangler.toml` | Worker config (DB binding, secrets) |
| `send_newsletter.py` | Python script to trigger newsletter send from cron |

## Setup Steps

### 1. Create D1 Database (Cloudflare Dashboard)

Since wrangler doesn't work on Termux (Android), do this in the dashboard:

1. Go to **Cloudflare Dashboard** → **D1** → **Create database**
2. Name it `newsletter-db`
3. Copy the **Database ID**
4. Run the schema:
   - Click on the database → **Console**
   - Paste and run the SQL from `schema.sql`

### 2. Deploy the Worker

**Option A — Dashboard (easiest):**
1. Go to **Workers & Pages** → **Create application** → **Create Worker**
2. Name it `daily-ai-digest-newsletter`
3. Paste the code from `worker.js`
4. Go to **Settings** → **Variables**:
   - Add `ADMIN_SECRET` = a random string (e.g., `openssl rand -hex 32`)
   - Add `RESEND_API_KEY` = your Resend API key (see step 3)
5. Go to **Settings** → **Bindings** → **D1 Database**:
   - Variable name: `DB`
   - Database: `newsletter-db`

**Option B — If you have access to a PC with wrangler:**
```bash
cd newsletter
wrangler d1 create newsletter-db
# Put the database_id in wrangler.toml
wrangler d1 execute newsletter-db --file=schema.sql
wrangler secret put ADMIN_SECRET
wrangler secret put RESEND_API_KEY
wrangler deploy
```

### 3. Set Up Resend (Free Email API)

1. Go to **resend.com** → sign up (free tier: 100 emails/day)
2. Verify your domain (`daily-ai-digest.freelancerloki.workers.dev`) or use the Resend test domain
3. Get your **API key**
4. Add it to the Worker as `RESEND_API_KEY` secret

### 4. Update the Website

1. In `app/index.html`, find the `WORKER_URL` in the `handleNL` function
2. Replace `https://daily-ai-digest-newsletter.YOUR_SUBDOMAIN.workers.dev` with your actual Worker URL
3. Rebuild: `python3 build.py`
4. Push: `git push`

### 5. Hook Into Cron Pipeline

In your `daily_run.py`, after the build+push step, add:

```python
import subprocess
# After new post is published:
subprocess.run([
    "python3", "newsletter/send_newsletter.py",
    "send",
    "--slug", post_slug,
    "--title", post_title,
    "--url", f"/posts/{post_slug}.html"
])
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/subscribe` | None | Subscribe an email |
| GET | `/api/unsubscribe?token=xxx` | Token | Unsubscribe |
| GET | `/api/subscribers?secret=xxx` | Admin | List all subscribers |
| POST | `/api/send` | Admin | Send newsletter to all |
| GET | `/api/health` | None | Health check |

## Admin Commands

```bash
# Count subscribers
python3 newsletter/send_newsletter.py count

# List all subscribers
python3 newsletter/send_newsletter.py list

# Manually send a newsletter
python3 newsletter/send_newsletter.py send \
    --slug 2026-06-18 \
    --title "Daily AI Digest — June 18, 2026" \
    --url "/posts/2026-06-18.html"
```
