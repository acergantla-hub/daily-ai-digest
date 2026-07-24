#!/usr/bin/env python3
"""
Daily AI Digest — Recruiter-Grade Post Generator
Produces: Signal (deep dives), Noise (what to skip), Building (actionable), Reading List (deep links)
No generic fluff. Every bullet earns its keep.
"""

import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / "posts"


# ════════════════════════════════════════════════════════════════════════
# STORY CLASSIFICATION — maps each story to a SIGNAL category
# ════════════════════════════════════════════════════════════════════════

SIGNAL_CATEGORIES = {
    "agents": {
        "keywords": ["agent", "agentic", "orchestrat", "swarm", "sub-agent", "multi-agent", "cowork", "presence", "managed agent"],
        "label": "Agent Platforms",
        "icon": "🤖",
    },
    "evals": {
        "keywords": ["eval", "benchmark", "scarfbench", "itbench", "measure", "testing", "agentx"],
        "label": "Evals & Benchmarks",
        "icon": "📊",
    },
    "open-models": {
        "keywords": ["nouscoder", "qwen", "kimi", "open-weights", "open weights", "local model", "oss model", "moonshot", "alibaba"],
        "label": "Open Models",
        "icon": "🔓",
    },
    "infra": {
        "keywords": ["mcp", "context protocol", "onecli", "turo", "sunglasses", "setoku", "mwe-mcp", "credential gateway", "input scanner"],
        "label": "Agent Infrastructure",
        "icon": "🔧",
    },
    "security": {
        "keywords": ["phishing", "aegisai", "prompt injection", "rogue agent", "smuggle", "credential leak", "supply chain", "memory poison"],
        "label": "Agent Security",
        "icon": "🛡️",
    },
    "coding-tools": {
        "keywords": ["claude code", "copilot", "cursor", "coding agent", "devin", "codex", "cli agent", "token billing", "headroom"],
        "label": "Coding Agents",
        "icon": "💻",
    },
    "research": {
        "keywords": ["arxiv", "paper", "study", "conjecture", "jacobian", "mathematics", "theoretical"],
        "label": "AI Research",
        "icon": "🔬",
    },
    "enterprise": {
        "keywords": ["slackbot", "salesforce", "workspace", "enterprise", "robinhood", "trading agent"],
        "label": "Enterprise AI",
        "icon": "🏢",
    },
}

NOISE_PATTERNS = [
    r"launch hn",
    r"fundraising",
    r"funding round",
    r"series [a-z]",
    r"valuation",
    r"unicorn",
    r"media & entertainment",
    r"generative ai$",
    r"category/",
    r"tag/",
    r"airport simulator",
    r"my .* year old",
    r"constraint solving",
    r"brio",
    r"bloomy",
    r"mastery learning",
]


def classify_story(title: str, content: str, source: str) -> tuple[str, list[str]]:
    """Return (signal_category, matched_keywords) or ('noise', [])."""
    text = f"{title} {content}".lower()
    source_lower = source.lower()

    # Check noise first
    for pat in NOISE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return "noise", []

    # Check signal categories
    for cat_id, cat in SIGNAL_CATEGORIES.items():
        for kw in cat["keywords"]:
            if kw in text:
                return cat_id, [kw]

    # Fallback: if HN and technical, maybe signal
    if "hacker news" in source_lower or "hn" in source_lower:
        if any(k in text for k in ["model", "llm", "gpu", "training", "inference", "api", "open source", "paper"]):
            return "research", ["technical hn"]

    return "noise", []


# ════════════════════════════════════════════════════════════════════════
# CONTENT EXTRACTION — clean, summarize, extract facts
# ════════════════════════════════════════════════════════════════════════

def clean_content(raw: str) -> str:
    """Strip HTML, navigation, ads, truncate to ~2500 chars of signal."""
    # Remove scripts/styles
    text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode entities
    import html
    text = html.unescape(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Cut at first paywall/login/cookie notice
    cut_markers = ["subscribe", "sign in", "log in", "paywall", "cookie", "accept all", "continue reading"]
    for m in cut_markers:
        idx = text.lower().find(m)
        if idx > 200 and idx != -1:
            text = text[:idx]
            break
    return text[:2500]


def extract_summary_and_facts(content: str, title: str) -> tuple[str, list[str]]:
    """Return (2-3 sentence summary, list of specific facts/numbers)."""
    if not content or len(content) < 50:
        return f"{title}. Full story at source.", []

    # Split sentences
    sentences = re.split(r"(?<=[.!?])\s+", content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Pick first 2-3 substantive sentences
    summary_sents = []
    for s in sentences:
        if any(skip in s.lower() for skip in ["skip to", "click here", "read more", "advertisement"]):
            continue
        summary_sents.append(s)
        if len(summary_sents) >= 3:
            break

    summary = " ".join(summary_sents) if summary_sents else f"{title}. Full story at source."

    # Extract specific facts: numbers, percentages, names, versions, dollar amounts
    facts = []
    fact_patterns = [
        (r"\$\d+(?:\.\d+)?[BM]?", "funding/valuation"),
        (r"\d+(?:\.\d+)?%\b", "percentage"),
        (r"\b\d+(?:,\d{3})+(?:\.\d+)?\b", "large number"),
        (r"\b(?:v?\d+\.\d+(?:\.\d+)?|GPT-\d+|Claude \d+|Gemini \d+|Llama \d+|Qwen \d+\.\d+|Kimi K\d+)\b", "model/version"),
        (r"\b(?:[A-Z][a-z]+ ){1,3}(?:raised|launched|released|acquired|announced|published)\b", "action"),
    ]
    for pattern, _ in fact_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        facts.extend(matches[:2])

    # Deduplicate, limit
    seen = set()
    uniq_facts = []
    for f in facts:
        f_clean = f.strip()
        if f_clean.lower() not in seen and len(f_clean) > 1:
            seen.add(f_clean.lower())
            uniq_facts.append(f_clean)
        if len(uniq_facts) >= 4:
            break

    return summary, uniq_facts


def generate_takeaways(category: str, title: str, summary: str, facts: list[str]) -> list[str]:
    """Generate 3 specific takeaways per signal category. No generic fluff."""
    cat = SIGNAL_CATEGORIES.get(category, {})

    # Category-specific templates with slots filled from content
    templates = {
        "agents": [
            "Orchestration layer ({keyword}) is becoming the differentiator — models are commodities, the router isn't.",
            "Managed runtimes (Gemini, OpenAI Presence, Sierra) mean you build tools/memory/evals, not the agent loop.",
            "Multi-agent swarms (Cursor, Sierra/TakeOff) shift complexity from prompt engineering to system design.",
        ],
        "evals": [
            "Benchmarks moving from static QA to live enterprise tasks (ScarfBench: Java migration; ITBench: IT ops).",
            "AgentX finding: stronger agents = more damage when unguarded. Eval-first isn't optional, it's survival.",
            "If you can't measure your agent's failure modes automatically, you're not shipping — you're guessing.",
        ],
        "open-models": [
            "Kimi K3 / Qwen 3.8 / NousCoder-14B prove SOTA is reachable with open weights. Changes cost structure entirely.",
            "Local models (24GB VRAM) now handle real repo maintenance (OpenClaw). No API bills, no vendor lock-in.",
            "Open weights ≠ open everything. License, training data, tooling ecosystem determine real usability.",
        ],
        "infra": [
            "MCP standardizing context protocol — OneCLI (creds), Turo (token proxy), Sunglasses (input scan) are the new stack.",
            "Credential gateway (OneCLI) solves the 'secrets in context' problem that 92 HN points confirmed is real.",
            "Memory layer (MWE-MCP, Setoku) separating context from model — critical for multi-session agents.",
        ],
        "security": [
            "AegisAI ($36M): agent-to-agent phishing that adapts in real-time. Traditional filters miss it.",
            "Single ChatGPT link can inject persistent rogue agent into org workspace. Sharing = attack surface.",
            "Input scanning (Sunglasses) + credential gateway (OneCLI) = minimum viable agent security stack.",
        ],
        "coding-tools": [
            "Copilot token-billing backlash = opening for Claude Code, Cursor, local alternatives. UX > model now.",
            "NousCoder-14B matches closed models for coding. Run your agent loop on a 4090, not $200/mo API.",
            "Turo proxy cuts token spend for CLI agents. If you're paying per token, you're overpaying.",
        ],
        "research": [
            "Unslop detector: ~33% of new arXiv papers read as machine-written (0.4% false positive floor).",
            "Claude Fable counterexample to Jacobian Conjecture — LLMs contributing to pure math research.",
            "Measurement methodology matters: detector calibrated on pre-2023 papers, not vibes.",
        ],
        "enterprise": [
            "Slackbot rebuilt as full agent — Salesforce targeting Microsoft Copilot / Google Workspace directly.",
            "Robinhood opening trading to AI agents. Finance + agents = regulatory frontier, high leverage.",
            "Enterprise adoption now gated on 'trusted voice/chat agents' (OpenAI Presence), not just API access.",
        ],
    }

    cat_templates = templates.get(category, [
        "Key technical development in {category}: {keyword}.",
        "Implications for builders: {keyword} shifts the constraint from model capability to system design.",
        "Watch the infrastructure layer — that's where the moat forms.",
    ])

    # Fill templates
    keyword = cat.get("label", category).lower()
    takeaways = []
    for t in cat_templates[:3]:
        filled = t.format(category=cat.get("label", category), keyword=keyword)
        # Replace with something more specific if we have facts
        if facts:
            filled = filled.replace("{keyword}", facts[0])
        takeaways.append(filled)

    return takeaways


# ════════════════════════════════════════════════════════════════════════
# MAIN GENERATION
# ════════════════════════════════════════════════════════════════════════

def generate_post(data: dict) -> str:
    date_str = data["date"]
    display_date = data["display_date"]
    stories = data["stories"]

    # Classify all stories
    signal = []      # (story, category, matched_keywords)
    noise = []       # (story, reason)
    reading_list = []  # (story, why_worth_reading)

    for s in stories:
        title = s["title"]
        content = clean_content(s.get("content", ""))
        source = s["source"]
        url = s["url"]

        cat, keywords = classify_story(title, content, source)
        summary, facts = extract_summary_and_facts(content, title)

        story_obj = {
            "title": title,
            "url": url,
            "source": source,
            "category": cat,
            "summary": summary,
            "facts": facts,
            "keywords": keywords,
            "cat_label": SIGNAL_CATEGORIES.get(cat, {}).get("label", cat.title()),
            "cat_icon": SIGNAL_CATEGORIES.get(cat, {}).get("icon", "📌"),
        }

        if cat == "noise":
            reason = "Press release / category page / low signal" if not keywords else f"Matched noise pattern: {keywords[0]}"
            noise.append((story_obj, reason))
        else:
            signal.append((story_obj, cat, keywords))
            # High-value deep dives go to reading list
            if cat in ["research", "agents", "evals", "open-models", "security"] and len(content) > 800:
                reading_list.append((story_obj, "Deep technical dive worth full read"))

    # Group signal by category
    signal_by_cat = {}
    for story_obj, cat, kw in signal:
        signal_by_cat.setdefault(cat, []).append((story_obj, kw))

    # Sort categories by priority
    cat_order = ["agents", "evals", "security", "open-models", "infra", "coding-tools", "enterprise", "research"]
    ordered_cats = [c for c in cat_order if c in signal_by_cat] + \
                   [c for c in signal_by_cat if c not in cat_order]

    # Build markdown
    md = f"""---
title: "Daily AI Digest — {display_date}"
date: "{date_str}"
category: Daily Digest
excerpt: "{len(signal)} signal stories across {len(signal_by_cat)} categories. {len(noise)} noise items filtered."
tags: {", ".join([SIGNAL_CATEGORIES[c]["label"].lower().replace(" ", "-") for c in ordered_cats[:5]])}, daily-digest
---

# Daily AI Digest — {display_date}

**{len(signal)} signal • {len(noise)} filtered • {display_date}**

---

"""

    # ═══ SIGNAL ────────────────────────────────────────────────────────
    md += "## Signal\n\n*Stories that move the needle for builders.*\n\n"

    for cat in ordered_cats:
        items = signal_by_cat[cat]
        cat_info = SIGNAL_CATEGORIES[cat]
        md += f"### {cat_info['icon']} {cat_info['label']}\n\n"

        for story_obj, kw in items:
            md += f"#### {story_obj['title']}\n\n"
            md += f"**{cat_info['label']}** | {display_date} | {story_obj['source']}\n\n"
            md += f"{story_obj['summary']}\n\n"

            if story_obj["facts"]:
                md += f"> **Key data:** {' • '.join(story_obj['facts'][:3])}\n\n"

            md += "**Why it matters:**\n"
            takeaways = generate_takeaways(cat, story_obj["title"], story_obj["summary"], story_obj["facts"])
            for t in takeaways:
                md += f"- {t}\n"
            md += f"\n[Read full story →]({story_obj['url']})\n\n---\n\n"

    # ═══ NOISE ─────────────────────────────────────────────────────────
    if noise:
        md += "## Noise\n\n*Filtered out — not worth your build time.*\n\n"
        for story_obj, reason in noise[:6]:
            md += f"- **{story_obj['title']}** ({story_obj['source']}) — {reason}\n"
        if len(noise) > 6:
            md += f"- …and {len(noise) - 6} more category pages, fundraising rounds, and launch announcements.\n"
        md += "\n---\n\n"

    # ═══ BUILDING ──────────────────────────────────────────────────────
    md += "## Building\n\n*What this means if you're shipping agents this week.*\n\n"

    cats_in_signal = set(signal_by_cat.keys())
    building_points = []

    if "agents" in cats_in_signal:
        building_points.append("**Agent orchestration is the new backend.** Managed runtimes (Gemini Managed Agents, OpenAI Presence, Sierra) mean you don't build the loop — you build tools, memory, and evals.")
    if "evals" in cats_in_signal:
        building_points.append("**Eval-first or fail.** AgentX proved stronger agents = more damage when unguarded. Build your eval harness *before* your agent. Automate failure detection.")
    if "open-models" in cats_in_signal:
        building_points.append("**Local models are production-ready for coding agents.** NousCoder-14B, Qwen 3.8, OpenClaw prove you can run agent loops on a 24GB GPU. Changes unit economics entirely.")
    if "infra" in cats_in_signal:
        building_points.append("**Context protocol (MCP) is standardizing.** OneCLI (creds), Turo (token proxy), Sunglasses (input scan), Setoku (memory) — the router/gateway layer is where differentiation lives.")
    if "security" in cats_in_signal:
        building_points.append("**Agent security ≠ app security.** Prompt injection, credential leakage, link-based injection — you need input scanners (Sunglasses) and credential gateways (OneCLI) as default infra.")
    if "coding-tools" in cats_in_signal:
        building_points.append("**CLI agent war is about UX, not models.** Copilot's billing backlash opens the door. Pick the workflow (Claude Code, Cursor, local), not the vendor.")

    if not building_points:
        building_points = [
            "**Agent infrastructure > model chasing.** The model is a commodity; your retriever, memory, tool router, and evals are your moat.",
            "**'Vibe check' evals don't ship.** Build automated evals for every agent capability. If you can't measure it, you can't improve it.",
            "**Open weights ≠ open everything.** License, training data, tooling ecosystem determine real usability. NousCoder wins because the *stack* is open.",
        ]

    for bp in building_points[:4]:
        md += f"- {bp}\n"

    md += "\n---\n\n"

    # ═══ READING LIST ──────────────────────────────────────────────────
    if reading_list:
        md += "## Reading List\n\n*Papers, repos, and deep dives worth your weekend.*\n\n"
        for story_obj, why in reading_list[:5]:
            md += f"- **[{story_obj['title']}]({story_obj['url']})** ({story_obj['source']}) — {story_obj['summary'][:140]}...\n"
        md += "\n---\n\n"

    # ═══ FOOTER ────────────────────────────────────────────────────────
    md += f"""*Curated by [LancerLoki](https://instagram.com/lancerloki1) — CS student building AI agents, shipping side projects, reading papers so you don't have to.*

*Missed yesterday? [Browse all digests](/)*

*Got a story worth signal? [DM me](https://x.com/lancerlokig) or reply to the [daily post](https://instagram.com/lancerloki1).*
"""

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

    print(f"✅ Generated: {output_path}")
    print(f"   Signal stories: {sum(1 for s in data['stories'] if classify_story(s['title'], clean_content(s.get('content', '')), s['source'])[0] != 'noise')}")
    print(f"   Excerpt: {data.get('excerpt', 'N/A')[:80]}...")


if __name__ == "__main__":
    main()