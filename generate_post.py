#!/usr/bin/env python3
"""
Daily AI Digest — Quality Post Generator
Filters noise, classifies signal, synthesizes themes.
"""

import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"


# ════════════════════════════════════════════════════════════════════════
# CATEGORIES — signal keywords only
# ════════════════════════════════════════════════════════════════════════

CATEGORIES = {
    "Agents": [
        "agent", "agentic", "orchestrat", "swarm", "sub-agent", "multi-agent",
        "cowork", "presence", "managed agent", "claude code", "devin", "openai agent",
        "slackbot", "robinhood", "autonomous agent", "agent platform", "takeoff",
        "sierra", "background task", "remote mcp", "voice mode", "chatgpt voice",
        "hugging face", "cyberattack", "fireside chat", "claude code team",
    ],
    "Models": [
        "nouscoder", "qwen", "kimi", "llama", "mistral", "gemma", "phi-",
        "open weight", "open-weight", "local model", "frontier model",
        "anthropic", "claude", "gpt-", "gemini", "opus", "sonnet", "haiku",
        "moonshot", "alibaba", "openai", "google", "deepmind",
        "guardrail", "cybersecurity", "health", "750 million", "voice mode",
    ],
    "Open Source": [
        "open source", "oss", "github.com/", "huggingface", "open weights",
        "apache 2.0", "mit license", "community model", "openclaw", "usb ai",
        "runway", "router", "model router", "generative media",
    ],
    "Security": [
        "vulnerability", "exploit", "injection", "phishing", "aegisai",
        "credential", "secret leak", "supply chain", "starlette", "badhost",
        "rogue agent", "smuggle", "memory poison", "guardrail", "red team",
        "prompt injection", "spear phishing", "onecli", "sunglasses",
    ],
    "Infrastructure": [
        "mcp", "context protocol", "model context protocol", "turo", "setoku",
        "mwe-mcp", "credential gateway", "token proxy", "router", "gateway",
        "rag", "retrieval", "vector db", "embedding", "memory layer",
    ],
    "Coding": [
        "coding agent", "copilot", "cursor", "codex", "windsurf", "aider",
        "vscode", "ide", "cli agent", "headroom", "token billing", "coding tool",
        "software engineer", "devin", "swe-agent",
    ],
    "Enterprise": [
        "salesforce", "slack", "workspace", "enterprise", "workplace",
        "microsoft copilot", "google workspace", "sierra", "adept",
        "robinhood trading", "presence platform", "yelp", "chatgpt health",
    ],
    "Research": [
        "arxiv", "paper", "benchmark", "eval", "scarfbench", "itbench",
        "agentx", "unslop", "conjecture", "jacobian", "mathematical",
        "methodology", "calibrated", "false positive", "detection",
    ],
    "Hardware": [
        "nvidia", "amd", "instinct", "h100", "h200", "blackwell", "gpu",
        "chip", "inference", "groq", "cerebras", "tpu", "tensor core",
        "mi455x", "cdna", "cowos", "rack-scale", "helios",
    ],
}

# URL patterns that are NEVER signal
NOISE_URL_PATTERNS = [
    r"techcrunch\.com/category/",
    r"techcrunch\.com/tag/",
    r"hacker-news\.firebaseio\.com",
    r"news\.ycombinator\.com/item\?id=",
    r"platform\.claude\.com/cookbook",
    r"\.pdf$",
    r"sliplane\.io/blog/hetzner",
    r"chipsandcheese\.com",
    r"nealstephenson\.substack\.com",
    r"houseofsaud\.com",
    r"timharek\.no",
    r"nesbitt\.io",
    r"airbus\.com",
    r"airport\.apunen\.com",
    r"axios\.com",
    r"haiku-os\.org",  # HaikuOS forum
    r"discuss\.haiku-os\.org",
    r"kaizen",
    r"homelab",
]

# Title/content patterns that are NEVER signal
NOISE_TEXT_PATTERNS = [
    r"^fundraising",
    r"^media & entertainment",
    r"^generative ai",
    r"^category/",
    r"^tag/",
    r"launch hn",
    r"airport simulator",
    r"my \d+ year old",
    r"constraint solving",
    r"brio",
    r"bloomy",
    r"mastery learning",
    r"k-12",
    r"writing by hand",
    r"homelab",
    r"maintainer interview",
    r"airbus",
    r"aircraft",
    r"irgc",
    r"data center",
    r"kaizen",
    r"cookbook",
    r"techcrunch\.com/category",
    r"techcrunch\.com/tag",
    r"meta launched.*ad",
    r"optimism ad",
    r"750 million.*gemini",
    r"gemini.*750 million",
    r"half-life 2",
    r"haikuos",
    r"haiku os",
    r"nvidia driver",
    r"turing gpu",
]


def is_noise_url(url: str) -> bool:
    for pat in NOISE_URL_PATTERNS:
        if re.search(pat, url, re.IGNORECASE):
            return True
    return False


def is_noise_text(text: str) -> bool:
    text_lower = text.lower()
    for pat in NOISE_TEXT_PATTERNS:
        if re.search(pat, text_lower):
            return True
    return False


def classify_story(title: str, content: str, url: str) -> str | None:
    """Return category name or None if noise."""
    if is_noise_url(url):
        return None

    text = f"{title} {content}".lower()
    if is_noise_text(text):
        return None

    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return cat
    return None


def clean_content(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    import html
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    cut_markers = ["subscribe", "sign in", "log in", "paywall", "continue reading", "cookie", "accept all", "enable cookies", "attention required", "cloudflare"]
    for m in cut_markers:
        idx = text.lower().find(m)
        if idx > 200 and idx != -1:
            text = text[:idx]
            break
    return text[:2500]


def extract_summary(content: str, title: str, max_sentences: int = 2) -> str:
    if not content or len(content) < 50:
        return title
    sentences = re.split(r"(?<=[.!?])\s+", content)
    summary = []
    for s in sentences:
        s = s.strip()
        if len(s) < 30:
            continue
        if any(skip in s.lower() for skip in ["skip to", "click here", "read more", "advertisement", "subscribe", "try cursor", "50% off"]):
            continue
        summary.append(s)
        if len(summary) >= max_sentences:
            break
    return " ".join(summary) if summary else title


# ════════════════════════════════════════════════════════════════════════
# MAIN GENERATION
# ════════════════════════════════════════════════════════════════════════

def generate_post(data: dict) -> str:
    date_str = data["date"]
    display_date = data["display_date"]
    stories = data["stories"]

    by_category = {}
    quick_hits = []

    for s in stories:
        title = s["title"]
        content = clean_content(s.get("content", ""))
        url = s.get("url", "")
        cat = classify_story(title, content, url)
        summary = extract_summary(content, title)

        story_obj = {"title": title, "url": url, "source": s["source"], "summary": summary}

        if cat:
            by_category.setdefault(cat, []).append(story_obj)
        else:
            quick_hits.append(story_obj)

    cat_order = ["Agents", "Models", "Open Source", "Security", "Infrastructure", "Coding", "Enterprise", "Research", "Hardware"]
    ordered_cats = [c for c in cat_order if c in by_category] + [c for c in by_category if c not in cat_order]

    dt = datetime.strptime(date_str, "%Y-%m-%d")
    day_name = dt.strftime("%A")
    signal_count = sum(len(v) for v in by_category.values())

    md = f"""---
title: "Daily AI Digest — {display_date}"
date: "{date_str}"
category: Daily Digest
excerpt: "{signal_count} signal stories across {len(by_category)} categories. {len(quick_hits)} filtered."
tags: {", ".join([c.lower().replace(" ", "-") for c in ordered_cats[:5]])}, daily-digest
---

# Daily AI Digest — {display_date} ({day_name})

**{signal_count} stories from the last 24 hours.** Here's what matters today.

---

"""

    # Top Stories by category
    for cat in ordered_cats:
        items = by_category[cat]
        if not items:
            continue
        md += f"## {cat}\n\n"
        for i, s in enumerate(items, 1):
            md += f"**{i}. {s['title']}**\n"
            md += f"{s['summary']}\n"
            md += f"[Read more]({s['url']})\n\n"
        md += "---\n\n"

    # Quick Hits
    if quick_hits:
        md += "## Quick Hits\n\n"
        for s in quick_hits[:12]:
            md += f"- **{s['title']}** — {s['summary'][:120]}... [Read]({s['url']})\n"
        md += "\n---\n\n"

    # Why This Matters — synthesize from ACTUAL stories in this post
    md += "## Why This Matters\n\n"
    themes = []

    agents_stories = by_category.get("Agents", [])
    models_stories = by_category.get("Models", [])
    open_source_stories = by_category.get("Open Source", [])
    security_stories = by_category.get("Security", [])
    enterprise_stories = by_category.get("Enterprise", [])
    hardware_stories = by_category.get("Hardware", [])

    if agents_stories:
        agent_titles = [s['title'] for s in agents_stories[:3]]
        themes.append(f"**Voice & agent interfaces hit the desktop** — {', '.join(agent_titles)}. The battleground shifts from chat to ambient voice control of agents on your machine.")

    if security_stories:
        sec_titles = [s['title'] for s in security_stories[:2]]
        themes.append(f"**AI security funding accelerates** — {', '.join(sec_titles)}. Attack surface expanding (voice agents, automated phishing) and capital follows.")

    if models_stories:
        mod_titles = [s['title'] for s in models_stories[:2]]
        themes.append(f"**Guardrails vs. utility tension** — {', '.join(mod_titles)}. Safety controls blocking legitimate security research; health features launching amid liability suits.")

    if enterprise_stories:
        ent_titles = [s['title'] for s in enterprise_stories[:2]]
        themes.append(f"**Enterprise AI goes agentic** — {', '.join(ent_titles)}. Yelp/ChatGPT partnership, ChatGPT Health rollout show B2B distribution winning.")

    if open_source_stories:
        os_titles = [s['title'] for s in open_source_stories[:2]]
        themes.append(f"**Model routing becomes infrastructure** — {', '.join(os_titles)}. Runway's router signals generative media fragmentation; you need a gateway, not a model.")

    if hardware_stories:
        hw_titles = [s['title'] for s in hardware_stories[:2]]
        themes.append(f"**AI hardware race intensifies** — {', '.join(hw_titles)}. Rack-scale systems (Helios) targeting Nvidia's moat; inference economics shifting.")

    if not themes:
        themes.append("**Signal concentrating in agent infra.** Models are commodities; orchestration, memory, tooling, and evals are the moat.")

    for i, t in enumerate(themes[:4], 1):
        md += f"{i}. {t}\n\n"

    md += "---\n\n*Stay ahead. Check back tomorrow.*\n"
    return md


def main():
    stories_path = BASE_DIR / ".current_stories.json"
    if not stories_path.exists():
        print("❌ No .current_stories.json found. Run daily_run.py first.")
        return

    with open(stories_path) as f:
        data = json.load(f)

    md = generate_post(data)

    date_str = data["date"]
    output_path = POSTS_DIR / f"{date_str}-daily-ai-digest.md"
    output_path.write_text(md, encoding="utf-8")

    signal_count = sum(1 for s in data["stories"] if classify_story(s["title"], clean_content(s.get("content", "")), s.get("url", "")))
    print(f"✅ Generated: {output_path}")
    print(f"   {len(data['stories'])} stories → {signal_count} signal, {len(data['stories']) - signal_count} filtered")


if __name__ == "__main__":
    main()