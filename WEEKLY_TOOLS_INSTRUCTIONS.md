# Weekly AI Tools Digest — Cron Job Instructions

You are writing the Weekly AI Tools Digest for LancerLoki's Daily AI Digest blog.
This post discovers and showcases the BEST new AI tools, apps, repos, and products from the past week.

## Step 1: Hunt for the best new AI tools

Search broadly across the internet for new AI tools, apps, webapps, GitHub repos, and products.
Focus on tools that are FREE or have a generous free tier. Prioritize quality over quantity.

**For each tool you consider, also try to find a relevant image:**
- **GitHub Repos:** Use the repository owner's avatar (https://github.com/<username>.png) or look for a logo in the repo's README
- **Websites/Web Apps:** Try to fetch the favicon (`https://domain.com/favicon.ico`) or look for og:image meta tags
- **Official Sites:** Check the tool's official website for logos or screenshots
- **Product Hunt/Futurepedia:** These sites often have tool images you can use (credit the source)

**Image sources to prioritize (in order):**
1. Official tool logo from the company website
2. GitHub repository avatar/logo
3. Favicon from the tool's website
4. Screenshot of the tool interface (if demonstrating features)
5. Product Hunt/listing site image (only if clearly credited)

**How to fetch images with curl:**
- GitHub avatar: `curl -sL 'https://github.com/<username>.png' -o /tmp/logo.png` (then base64 encode or note the URL)
- Favicon: `curl -sL 'https://example.com/favicon.ico'`
- To check if an image URL is valid: `curl -sL -I <image-url> | grep -i "content-type: image"`

**Important:** Only use images you have the right to use (official sources, public domain, or properly credited). When in doubt, skip the image rather than risk copyright issues.

**GitHub (new trending AI repos):**
- `curl -sL 'https://github.com/trending?since=weekly&spoken_language_code=en'` — trending repos this week
- `curl -sL 'https://github.com/trending/python?since=weekly'` — Python AI repos
- `curl -sL 'https://github.com/trending/typescript?since=weekly'` — TS/JS AI repos
- Search GitHub for: "AI agent", "LLM", "AI tool", "AI app", "chatbot", "AI workflow"

**HN (filter for tools/products, not just news):**
- `curl -sL 'https://hacker-news.firebaseio.com/v0/topstories.json'` — get top story IDs
- Fetch top 30 story titles: `curl -sL 'https://hacker-news.firebaseio.com/v0/item/ID.json'`
- Filter for: new tool launches, GitHub repos, web apps, AI products, demos

**Product Hunt:**
- `curl -sL 'https://www.producthunt.com/'` — look for AI tool launches

**Reddit (AI tool discussions):**
- `curl -sL 'https://www.reddit.com/r/LocalLLaMA/hot.json?limit=25'` — LocalLLaMA community
- `curl -sL 'https://www.reddit.com/r/artificial/hot.json?limit=25'` — AI community
- `curl -sL 'https://www.reddit.com/r/SideProject/hot.json?limit=25'` — indie makers

**Twitter/X (via nitter or similar):**
- Search for "just launched", "open source", "free AI tool", "GitHub repo"

**Other sources:**
- `curl -sL 'https://www.futurepedia.io/'` — AI tools directory
- `curl -sL 'https://alternativeto.net/category/ai-tools/'` — alternative AI tools
- `curl -sL 'https://www.toolify.ai/'` — AI tools aggregator
- `curl -sL 'https://aitoptools.com/'` — AI tools directory

**What to look for:**
- New GitHub repos with 500+ stars that are AI-related
- New web apps / SaaS tools with free tiers
- Open-source AI tools (local LLMs, agents, automation)
- AI-powered developer tools
- AI creative tools (image, video, audio, music)
- AI productivity tools
- Browser extensions with AI features
- New model releases (open weights preferred)
- AI agent frameworks and MCP servers

**Filtering criteria:**
- Must be related to AI/ML/LLMs in some way
- Prefer free or freemium tools
- Prefer tools that are actually useful, not hype
- Skip: pure research papers without code, paid-only enterprise tools, crypto/blockchain AI
- Aim for 6-10 excellent tools (quality > quantity)

## Step 2: Write the blog post

Create a new markdown file in `/data/data/com.termux/files/home/daily-ai-digest/posts/`
Naming pattern: `YYYY-MM-DD-weekly-ai-tools.md`

The post MUST follow this format:

```
---
title: "Weekly AI Tools Digest — YYYY-MM-DD"
date: "YYYY-MM-DD"
category: Weekly Tools
excerpt: "Brief 1-sentence summary of the best new AI tools this week."
tags: ai-tools, weekly-digest, free-ai, open-source, github, [relevant tags]
---

## This Week's Best New AI Tools

Brief intro paragraph (2-3 sentences) about what you found this week and the overall trend.

---

### 🏆 Tool Name — One-line tagline

**Type:** Web App / GitHub Repo / Browser Extension / CLI Tool / etc.
**Pricing:** Free / Freemium / Open Source
**Link:** [tool-name](URL)

![Optional: Tool logo/screenshot](image-url-here)

2-3 paragraph description of what the tool does, why it's cool, and how to use it.
Include specific features, tech stack if known, and standout capabilities.
You can include additional images in the description if helpful (e.g., screenshots of the interface).

**Why it's great:**
- Specific reason 1
- Specific reason 2
- Specific reason 3

---

### 🥈 Next Tool Name — One-line tagline

[same format...]

---

[repeat for all tools]

---

## Honorable Mentions

Brief list (3-5) of other interesting tools that didn't make the main list but are worth watching:
- [Tool Name](URL) — one-line description
- [Tool Name](URL) — one-line description

---

## The Big Picture

2-3 paragraph analysis of the trends you're seeing in the AI tools landscape this week.
What patterns are emerging? What should people pay attention to?
```

WRITING STYLE:
- Enthusiastic but honest — don't oversell
- Include specific details: star counts, feature lists, tech stacks
- Write for a general tech audience (not too technical, not too dumbed down)
- Each tool section should be substantive — not just one line
- The "Big Picture" section should connect the tools into a narrative about where AI is heading

## Step 3: Build the site

Run: `cd /data/data/com.termux/files/home/daily-ai-digest && python3 build.py`

Verify that `dist/index.html` and `dist/posts/` were generated successfully.

## Step 4: Push to GitHub (triggers Cloudflare Pages auto-deploy)

```bash
cd /data/data/com.termux/files/home/daily-ai-digest
git config user.email "hermes@termux"
git config user.name "Hermes"
git add -A
git commit -m "Add Weekly AI Tools Digest for YYYY-MM-DD"
GIT_SSH_COMMAND="ssh -i /data/data/com.termux/files/home/.ssh/id_ed25519 -o StrictHostKeyChecking=no" git push origin main
```

## Step 5: Report results

Output a summary including:
1. ✅ Blog post URL on the live site
2. ✅ Number of tools featured
3. ✅ Top 3 tools with one-line descriptions
4. ✅ GitHub push confirmation
