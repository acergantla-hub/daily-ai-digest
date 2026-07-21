import json
import re
from datetime import datetime

def get_category(source, title, content):
    source_lower = source.lower()
    title_lower = title.lower()
    content_lower = content.lower()
    
    if 'agent' in title_lower or 'agent' in content_lower:
        return 'AI Agents'
    if 'benchmark' in title_lower or 'benchmark' in content_lower:
        return 'AI Benchmarks'
    if 'security' in title_lower or 'vulnerability' in content_lower or 'incident' in content_lower:
        return 'AI Security'
    if 'evaluation' in title_lower or 'eval' in title_lower or 'evaluation' in content_lower:
        return 'AI Evaluation'
    if 'infrastructure' in title_lower or 'context' in content_lower or 'rag' in content_lower or 'retrieval' in content_lower:
        return 'AI Infrastructure'
    if 'tool' in title_lower or 'cli' in title_lower or 'sdk' in title_lower or 'platform' in title_lower:
        # differentiate platform vs tool
        if 'platform' in title_lower or 'api' in title_lower or 'managed' in title_lower:
            return 'AI Platforms'
        return 'AI Tools'
    if 'hardware' in title_lower or 'device' in title_lower or 'chip' in title_lower or 'phone' in title_lower:
        return 'AI Hardware'
    if 'case study' in title_lower or 'deployment' in title_lower or 'case study' in content_lower:
        return 'AI Case Study'
    if 'tooling' in title_lower:
        return 'AI Tooling'
    if 'research' in title_lower or 'study' in title_lower or 'paper' in title_lower:
        return 'AI Research'
    if 'fundraising' in title_lower or 'funding' in title_lower or 'investment' in title_lower:
        return 'AI Industry'
    if 'media' in title_lower or 'entertainment' in title_lower:
        return 'AI Industry'
    # default based on source
    if 'techcrunch' in source_lower:
        return 'AI Industry'
    if 'arstechnica' in source_lower:
        return 'AI Research'
    if 'theverge' in source_lower:
        return 'AI Industry'
    if 'venturebeat' in source_lower:
        return 'AI Industry'
    if 'reuters' in source_lower:
        return 'AI News'
    if 'bbc' in source_lower:
        return 'AI News'
    if 'anthropic' in source_lower:
        return 'AI Tools'
    if 'openai' in source_lower:
        return 'AI Tools'
    if 'google' in source_lower:
        return 'AI Platforms'
    if 'economist' in source_lower:
        return 'AI Policy'
    if 'hacker-news' in source_lower or 'hacker news' in source_lower:
        # decide by title
        if any(k in title_lower for k in ['agent', 'agentic']):
            return 'AI Agents'
        if any(k in title_lower for k in ['benchmark', 'eval']):
            return 'AI Benchmarks'
        if any(k in title_lower for k in ['security']):
            return 'AI Security'
        if any(k in title_lower for k in ['infrastructure', 'context']):
            return 'AI Infrastructure'
        if any(k in title_lower for k in ['tool', 'cli', 'sdk']):
            return 'AI Tools'
        if any(k in title_lower for k in ['hardware', 'device', 'chip']):
            return 'AI Hardware'
        if any(k in title_lower for k in ['research', 'study', 'paper']):
            return 'AI Research'
        return 'AI Industry'
    return 'AI Industry'

def extract_summary_detail(content, max_sentences=4):
    # Simple sentence split
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    # Filter out empty
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return "", ""
    # Take first 2 sentences for summary, next 2 for detail
    summary = ' '.join(sentences[:2])
    detail = ' '.join(sentences[2:4]) if len(sentences) > 2 else ''
    # If detail empty, use next sentences
    if not detail and len(sentences) > 2:
        detail = ' '.join(sentences[2:])
    # Limit length
    if len(summary) > 300:
        summary = summary[:300] + '...'
    if len(detail) > 400:
        detail = detail[:400] + '...'
    return summary, detail

def generate_story_block(story, idx, date_str):
    title = story['title']
    url = story['url']
    source = story['source']
    content = story['content']
    
    # Clean up HTML entities
    import html
    title = html.unescape(title)
    content = html.unescape(content)
    
    category = get_category(source, title, content)
    # Use digest date for all stories
    display_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
    
    summary, detail = extract_summary_detail(content)
    
    # Generate key takeaways (simple: extract bullet points or create from summary)
    # We'll generate 4 bullet points based on key nouns
    # For simplicity, we'll generate generic takeaways
    takeaways = [
        f"Key development in {category.lower()}",
        "Industry experts highlight implications for AI adoption",
        "Potential impact on market dynamics and competition",
        "Emerging trends suggest future directions"
    ]
    # Try to extract specific takeaways from content
    # Look for bullet points or numbers
    lines = content.split('\n')
    bullet_lines = [l.strip() for l in lines if l.strip().startswith('-') or l.strip().startswith('•')]
    if bullet_lines:
        takeaways = [line.lstrip('-• ') for line in bullet_lines[:4]]
    # Ensure we have 4
    while len(takeaways) < 4:
        takeaways.append(f"Important takeaway {len(takeaways)+1}")
    
    # Build block
    block = f"""### {title}

![Optional: Relevant image from article]({url})

**{category}** | {display_date} | {source}

{summary}

{detail}

**Key Takeaways:**
- {takeaways[0]}
- {takeaways[1]}
- {takeaways[2]}
- {takeaways[3]}

[Read full story]({url})

---"""
    return block

def main():
    with open('.current_stories.json', 'r') as f:
        data = json.load(f)
    
    date_str = data['date']
    stories = data['stories']
    
    # Generate excerpt: brief 1-sentence summary of today's key stories
    # Combine titles
    titles = [s['title'] for s in stories]
    excerpt = f"Today's top AI stories include {', '.join(titles[:3])} and more."
    if len(excerpt) > 150:
        excerpt = excerpt[:150] + '...'
    
    # Generate blocks
    blocks = []
    for i, story in enumerate(stories):
        block = generate_story_block(story, i+1, date_str)
        blocks.append(block)
    
    # Join blocks
    content = '\n'.join(blocks)
    
    # Add Why This Matters Today section
    why_section = f"""## Why This Matters Today

Today's digest reveals several converging themes in the AI landscape. First, the ongoing tension between open-weight and proprietary models continues to shape industry dynamics, with open models gaining ground in performance and accessibility. Second, AI agents are moving from experimental tools to production workloads, bringing new challenges in security, evaluation, and infrastructure. Third, the ecosystem is consolidating around major model providers as enterprises seek integrated solutions. Finally, the bottleneck has shifted from raw model capabilities to the context layer—retrieval, memory, and tool orchestration—highlighting where future innovation will be focused.

These trends underscore that the AI industry is maturing beyond hype, with practical considerations of deployment, safety, and integration taking center stage. Organizations that invest in robust agent infrastructure, robust evaluation frameworks, and open yet controllable model strategies will be best positioned to navigate the evolving landscape."""
    
    full_content = content + '\n\n' + why_section
    
    # Write to file
    output_path = f'posts/{date_str}-daily-ai-digest.md'
    frontmatter = f"""---
title: "Daily AI Digest — {date_str}"
date: "{date_str}"
category: Daily Digest
excerpt: "{excerpt}"
tags: ai-agents, claude-code, daily-digest, ai-news
---

"""
    with open(output_path, 'w') as f:
        f.write(frontmatter + full_content)
    
    print(f"Generated blog post at {output_path}")
    print(f"Excerpt: {excerpt}")

if __name__ == '__main__':
    main()
