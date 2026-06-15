# Daily AI Digest — Cron Job Instructions

You are running the Daily AI Digest pipeline. Complete ALL steps below.

## Step 1: Search for today's top AI news

Search the web for today's biggest AI news stories. Use web_search with queries like:
- "AI news today"
- "artificial intelligence latest developments"
- "OpenAI Anthropic Google AI news"
- "AI agents news"
- "LLM large language model news"

Aim to find 8-12 high-quality stories. Skip stories that are purely marketing/announcements unless they are significant (new model releases, major partnerships, etc.).

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

CRITICAL: Each story section needs:
- A ### heading with the story title
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

## Step 7: Report results

Output a summary including:
1. ✅ Blog post URL on the live site
2. ✅ Number of Instagram slides generated
3. ✅ Caption preview
4. ✅ Notice that user needs to manually upload slides to Instagram
