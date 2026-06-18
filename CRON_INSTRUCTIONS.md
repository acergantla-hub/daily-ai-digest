# Daily AI Digest — Cron Job Instructions

You are running the Daily AI Digest pipeline. Complete ALL steps below.

## Step 1: Search for today's top AI news

Fetch today's AI news by curling these sources directly (web_search is not configured, use `curl -sL`):

**For each article you consider, also try to find a relevant image:**
- **News Articles:** Look for og:image or twitter:image meta tags in the article's HTML
- **Company Announcements:** Use the company logo or product screenshot from their official site
- **Research Papers:** Use diagrams or figures from the paper (if available and copyright allows)

**How to fetch article images with curl and grep:**
1. Fetch the article: `curl -sL '<article-url>'`
2. Extract og:image: `grep -i 'og:image' | grep -o 'content="[^"]*"' | cut -d'"' -f2`
3. Extract twitter:image: `grep -i 'twitter:image' | grep -o 'content="[^"]*"' | cut -d'"' -f2`
4. To verify an image URL: `curl -sL -I <image-url> | head -5`

**Image sources to prioritize:**
1. Official og:image/twitter:image from the news article
2. Company logo from the mentioned organization's site
3. Screenshot of the product/technology being discussed
4. Graph or chart from the original source (research paper, report)

**Important:** Only use images you have the right to use (official sources, public domain, or properly credited). When in doubt, skip the image rather than risk copyright issues.

**Primary sources (check all of these):**
- `https://techcrunch.com/category/artificial-intelligence/` — TechCrunch AI section
- `https://arstechnica.com/ai/` — Ars Technica AI section
- `https://www.theverge.com/ai-artificial-intelligence` — The Verge AI section
- `https://venturebeat.com/ai/` — VentureBeat AI section
- `https://news.ycombinator.com/` — Hacker News (filter for AI stories)
- `https://www.reuters.com/technology/artificial-intelligence/` — Reuters AI
- `https://www.bbc.com/news/topics/cywd23g0wzwt` — BBC AI stories

**Company blogs (check for recent posts):**
- `https://www.anthropic.com/news` — Anthropic announcements
- `https://openai.com/news` — OpenAI announcements
- `https://blog.google/technology/ai/` — Google AI blog
- `https://microsoft.com/en-us/research/blog` — Microsoft Research

**Secondary sources:**
- `https://www.404media.co/` — 404 Media (AI coverage)
- `https://simonwillison.net/` — Simon Willison's blog (daily AI notes)
- `https://www.economist.com/` — Economist tech/AI coverage

For each source, use: `curl -sL --max-time 15 '<URL>'` then extract article titles and URLs using Python regex. Deduplicate across sources. Aim for 8-12 high-quality stories. Prioritize stories about model releases, AI agents, policy/regulation, security, industry/funding, and research breakthroughs. Skip pure marketing fluff unless it is significant.

Prioritize stories about:
- New AI model releases/updates
- AI agents and agent frameworks
- Major company announcements (OpenAI, Anthropic, Google DeepMind, Microsoft, Meta, Mistral)
- AI policy, regulation, and legal
- AI security and safety
- AI industry news (funding, pricing, partnerships)
- AI research breakthroughs
- AI tools and products

## Step 2: Write the blog post

Create a new markdown file in `/data/data/com.termux/files/home/daily-ai-digest/posts/` with the naming pattern `YYYY-MM-DD-daily-ai-digest.md`

The post MUST follow this exact format (matching existing posts):

```
---
title: "Daily AI Digest — YYYY-MM-DD"
date: "YYYY-MM-DD"
category: Daily Digest
excerpt: "Brief 1-sentence summary of today's key stories."
tags: ai-agents, claude-code, daily-digest, google, anthropic, openai, [relevant tags]
---

### Story Title Here

![Optional: Relevant image from article](image-url-here)

**Category Name** | Date | Source Name

Story summary paragraph (2-4 sentences covering the key facts and why it matters).

More detail paragraph (2-3 sentences with technical details, numbers, quotes).

**Key Takeaways:**
- Key takeaway 1
- Key takeaway 2
- Key takeaway 3
- Key takeaway 4

[Read full story](URL)

---

### Next Story Title

[... repeat for all stories ...]

---

## Why This Matters Today

Today's digest reveals several converging themes...

[4-6 paragraph analysis section connecting all the stories and discussing broader implications]
```

**Adding Images (Optional but Recommended):**
For each story, you MAY include one relevant image right after the title. This could be:
- A screenshot from the article
- A logo of the company/product mentioned
- A relevant graphic or chart
- Use standard markdown syntax: `![Description](image-url)`

Only include images if they add value and are from legitimate sources (article itself, official company sites, etc.). Avoid random stock photos.

**CRITICAL: Each story section needs:**
- A ### heading with the story title
- An optional image line (markdown image syntax)
- A bold category line with source and date
- 2-4 well-written summary paragraphs (don't just copy from sources — synthesize and write in your own words)
- A "Key Takeaways" section with 4 bullet points
- A "Read full story" link to the source URL

WRITING STYLE:
- Professional but engaging
- Include specific numbers, names, and technical details when available
- Each story should be substantive — not just a one-line summary
- The "Why This Matters Today" section should connect all stories into a coherent narrative

## Step 3: Build the site

Run: `cd /data/data/com.termux/files/home/daily-ai-digest && python3 build.py`

Verify that `dist/index.html` and `dist/posts/` were generated successfully.

## Step 4: Push to GitHub (triggers Cloudflare Pages auto-deploy)

```bash
cd /data/data/com.termux/files/home/daily-ai-digest
git config user.email "hermes@termux"
git config user.name "Hermes"
git add -A
git commit -m "Add Daily AI Digest for YYYY-MM-DD"
GIT_SSH_COMMAND="ssh -i /data/data/com.termux/files/home/.ssh/id_ed25519 -o StrictHostKeyChecking=no" git push origin main
```

## Step 5: Generate Instagram carousel images

Run: `cd /data/data/com.termux/files/home/daily-ai-digest && python3 generate_images.py posts/YYYY-MM-DD-daily-ai-digest.md`

This will create slides in `/data/data/com.termux/files/home/daily-ai-digest/instagram_posts/`

## Step 6: Generate Instagram caption

Create an Instagram caption file at `/data/data/com.termux/files/home/daily-ai-digest/instagram_posts/caption.txt` with:
- A hook line
- Numbered list of stories
- Link to the website
- Relevant hashtags

## Step 7: Send newsletter to subscribers

Run the newsletter sender to email all active subscribers about the new post:

```bash
cd /data/data/com.termux/files/home/daily-ai-digest
python3 newsletter/send_newsletter.py send \
    --slug YYYY-MM-DD-daily-ai-digest \
    --title "Daily AI Digest — YYYY-MM-DD" \
    --url "/posts/YYYY-MM-DD-daily-ai-digest.html"
```

This sends the newsletter via the Cloudflare Worker to all D1 subscribers using Resend.

## Step 8: Report results

Output a summary including:
1. ✅ Blog post URL on the live site
2. ✅ Number of Instagram slides generated
3. ✅ Caption preview
4. ✅ Newsletter sent to N subscribers (or "No subscribers yet" if 0)
5. ✅ Notice that user needs to manually upload slides to Instagram
