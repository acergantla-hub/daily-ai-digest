#!/usr/bin/env python3
from pathlib import Path
import re

content = Path("posts/2026-06-18-daily-ai-digest.md").read_text()
story_titles = re.findall(r"###\s+(.+)", content)
story_titles = [t for t in story_titles if "Why This Matters" not in t][:12]
date_str = "June 18, 2026"

lines = []
lines.append("Daily AI Digest — " + date_str)
lines.append("")
lines.append("Today's top " + str(len(story_titles)) + " AI stories:")
lines.append("")
for i, t in enumerate(story_titles, 1):
    clean = re.sub(r"\*\*", "", t)
    lines.append(str(i) + ". " + clean)
lines.append("")
lines.append("Read the full digest: https://daily-ai-digest.freelancerloki.workers.dev")
lines.append("")
lines.append("#AI #ArtificialIntelligence #AIagents #ClaudeCode #ChatGPT #OpenAI #Anthropic #GoogleAI #tech #ainews #technews #machinelearning #dailydigest #airesearch")

caption = "\n".join(lines)
Path("instagram_posts/caption.txt").write_text(caption)
print(caption)
