#!/usr/bin/env python3
"""Generate Instagram caption for the latest Daily AI Digest post."""
from pathlib import Path
import re
from datetime import datetime

POSTS_DIR = Path("posts")
OUTPUT_DIR = Path("instagram_posts")

# Find the latest daily digest post
posts = sorted(POSTS_DIR.glob("*-daily-ai-digest.md"))
if not posts:
    print("ERROR: No daily digest posts found")
    exit(1)

latest = posts[-1]
content = latest.read_text()

# Extract date from frontmatter
date_match = re.search(r'date:\s*"?(\d{4}-\d{2}-\d{2})"?', content)
date_str = date_match.group(1) if date_match else latest.stem[:10]
try:
    display_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
except:
    display_date = date_str

# Extract story titles
story_titles = re.findall(r"###\s+(.+)", content)
story_titles = [t for t in story_titles if "Why This Matters" not in t][:12]

# Number emojis
num_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "1️⃣1️⃣", "1️⃣2️⃣"]

# Build caption
lines = []
lines.append(f"🚀 Daily AI Digest — {display_date}")
lines.append("")
lines.append(f"Today's biggest AI stories:")
for i, t in enumerate(story_titles):
    clean = re.sub(r"\*\*", "", t)
    emoji = num_emojis[i] if i < len(num_emojis) else f"{i+1}."
    lines.append(f"{emoji} {clean}")
lines.append(f"Read the full digest 👉 daily-ai-digest.freelancerloki.workers.dev")
lines.append(f"Follow for daily AI news → @lancerloki1")
lines.append("")
lines.append("#AI #ArtificialIntelligence #DailyAIDigest #OpenAI #Anthropic #SpaceX #Cursor #Nvidia #AIAgents #MachineLearning #TechNews #AIIndustry #BernieSanders #Trump #Amazon #AWS")

caption = "\n".join(lines)
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "caption.txt").write_text(caption)
print(caption)
