#!/usr/bin/env python3
"""Generate per-story SVG hero images for the blog post."""
import hashlib
import base64
from pathlib import Path

OUTPUT_DIR = Path("assets/story_images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Story data: (title, category_icon, accent_color, accent2)
stories = [
    ("Anthropic joins Frontier carbon removal coalition", "🌍", "#34d399", "#00d4f0"),
    ("World leaders want American AI", "🌐", "#7c6cf0", "#b46eff"),
    ("US government Anthropic models ban", "⚖️", "#f472b6", "#7c6cf0"),
    ("ChatGPT image generator safety failure", "🛡️", "#ff6b6b", "#ffd166"),
    ("AI layoff wave powder keg", "💥", "#ff6b6b", "#f472b6"),
    ("Meta AI unit gulag report", "🏭", "#ffd166", "#ff6b6b"),
    ("Meta Facebook AI Mode", "📱", "#00d4f0", "#34d399"),
    ("Turn off AI in Google Docs", "📄", "#7c6cf0", "#00d4f0"),
    ("GLM-5.2 open weights LLM", "🧠", "#b46eff", "#7c6cf0"),
    ("LLM battle royale Claude vs Grok", "🤖", "#00d4f0", "#34d399"),
    ("x86 ACE AI compute spec", "💻", "#34d399", "#00d4f0"),
    ("NEA enterprise AI ROI", "📊", "#f472b6", "#ffd166"),
]

def hexval(h, offset, length=2):
    start = offset % 32
    end = (offset + length) % 32
    if end <= start:
        end = 32
    val = h[start:end]
    return int(val, 16) if val else 0

def make_svg(title, icon, accent, accent2):
    h = hashlib.md5(title.encode()).hexdigest()
    nodes = []
    for i in range(18):
        x = 8 + (hexval(h, i * 2) % 84)
        y = 8 + (hexval(h, i * 2 + 16) % 84)
        r = 1.5 + (hexval(h, i) % 5)
        nodes.append((x, y, r))

    connections = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 30:
                connections.append((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1], max(0.08, 0.35 - dist / 100)))

    parts = []
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" preserveAspectRatio="xMidYMid slice">')
    parts.append('<defs>')
    parts.append('<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">')
    parts.append('<stop offset="0%" style="stop-color:#0a0a1a"/>')
    parts.append('<stop offset="50%" style="stop-color:#0f0a2a"/>')
    parts.append('<stop offset="100%" style="stop-color:#0a1a30"/>')
    parts.append('</linearGradient>')
    parts.append('<radialGradient id="glow1" cx="30%" cy="50%" r="60%">')
    parts.append('<stop offset="0%" style="stop-color:' + accent + ';stop-opacity:0.3"/>')
    parts.append('<stop offset="100%" style="stop-color:' + accent + ';stop-opacity:0"/>')
    parts.append('</radialGradient>')
    parts.append('<radialGradient id="glow2" cx="70%" cy="50%" r="50%">')
    parts.append('<stop offset="0%" style="stop-color:' + accent2 + ';stop-opacity:0.2"/>')
    parts.append('<stop offset="100%" style="stop-color:' + accent2 + ';stop-opacity:0"/>')
    parts.append('</radialGradient>')
    parts.append('<filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    parts.append('<filter id="softglow"><feGaussianBlur stdDeviation="8"/></filter>')
    parts.append('</defs>')
    parts.append('<rect width="1200" height="400" fill="url(#bg)"/>')
    parts.append('<rect width="1200" height="400" fill="url(#glow1)"/>')
    parts.append('<rect width="1200" height="400" fill="url(#glow2)"/>')

    for x1, y1, x2, y2, op in connections:
        parts.append('<line x1="' + str(x1*10) + '" y1="' + str(y1*3.33) + '" x2="' + str(x2*10) + '" y2="' + str(y2*3.33) + '" stroke="' + accent + '" stroke-width="1" opacity="' + str(round(op, 2)) + '"/>')

    for x, y, r in nodes:
        nx, ny = x * 10, y * 3.33
        parts.append('<circle cx="' + str(nx) + '" cy="' + str(ny) + '" r="' + str(r*6) + '" fill="' + accent + '" opacity="0.06" filter="url(#softglow)"/>')
        parts.append('<circle cx="' + str(nx) + '" cy="' + str(ny) + '" r="' + str(r*3) + '" fill="' + accent + '" opacity="0.15"/>')
        parts.append('<circle cx="' + str(nx) + '" cy="' + str(ny) + '" r="' + str(r*1.2) + '" fill="' + accent + '" opacity="0.7" filter="url(#glow)"/>')

    for i in range(10):
        px = 50 + (hexval(h, i * 2) % 1100)
        py = 30 + (hexval(h, i * 2 + 8) % 340)
        pr = 1 + (hexval(h, i) % 3)
        p_op = 0.1 + (hexval(h, i + 4) % 20) / 100
        parts.append('<circle cx="' + str(px) + '" cy="' + str(py) + '" r="' + str(pr) + '" fill="white" opacity="' + str(round(p_op, 2)) + '"/>')

    parts.append('<text x="600" y="210" text-anchor="middle" font-size="72" opacity="0.9" filter="url(#glow)">' + icon + '</text>')
    parts.append('</svg>')

    svg = "\n".join(parts)
    encoded = base64.b64encode(svg.encode()).decode()
    return "data:image/svg+xml;base64," + encoded

for i, (title, icon, accent, accent2) in enumerate(stories):
    data_uri = make_svg(title, icon, accent, accent2)
    fname = "story_" + str(i + 1) + ".txt"
    (OUTPUT_DIR / fname).write_text(data_uri)
    print("  Generated: " + fname + " (" + title[:40] + ")")

print("\nDone. " + str(len(stories)) + " story images generated.")
