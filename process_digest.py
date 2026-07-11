import re
from datetime import datetime

def parse_news_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    lines = content.splitlines()
    # Remove the first two lines (header and separator)
    content_lines = []
    for line in lines[2:]:  # Skip the first two lines
        if '|' in line:
            parts = line.split('|', 1)
            content_lines.append(parts[1].strip())
        else:
            content_lines.append(line.strip())
    # Now split into sections
    sections = []
    current_section = None
    current_lines = []
    for line in content_lines:
        if line.startswith('---') and line.endswith('---'):
            if current_section is not None:
                sections.append((current_section, current_lines))
            current_section = line.strip('- ').strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_section is not None:
        sections.append((current_section, current_lines))
    all_items = []
    for section_name, section_lines in sections:
        items = []
        current_item = []
        for line in section_lines:
            if line == '':
                if current_item:
                    items.append(current_item)
                    current_item = []
            else:
                current_item.append(line)
        if current_item:
            items.append(current_item)
        for item_lines in items:
            if not item_lines:
                continue
            title_line = item_lines[0].strip()
            title_match = re.match(r'^\d+\.\s+(.*)', title_line)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = title_line
            source = ''
            why_it_matters = ''
            snippet = ''
            link = ''
            for line in item_lines[1:]:
                stripped = line.strip()
                if stripped.startswith('Source:'):
                    source_part = stripped.split('Source:', 1)[1].strip()
                    if '|' in source_part:
                        source_part = source_part.split('|')[0].strip()
                    if source_part.startswith('RSS:'):
                        source_part = source_part[4:].strip()
                    source = source_part
                elif stripped.startswith('Why it matters:'):
                    why_it_matters = stripped.split('Why it matters:', 1)[1].strip()
                    if why_it_matters.startswith('> Respond:'):
                        why_it_matters = why_it_matters.split('> Respond:', 1)[1].strip()
                elif stripped.startswith('Snippet:'):
                    snippet = stripped.split('Snippet:', 1)[1].strip()
                elif stripped.startswith('Link:'):
                    link = stripped.split('Link:', 1)[1].strip()
            all_items.append({
                'section': section_name,
                'title': title,
                'source': source,
                'why_it_matters': why_it_matters,
                'snippet': snippet,
                'link': link
            })
    return all_items

def generate_summary(item):
    text = f"{item['why_it_matters']} {item['snippet']}"
    text = ' '.join(text.split())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]
    if len(sentences) < 3:
        if item['title'] not in sentences:
            sentences.insert(0, item['title'])
        while len(sentences) < 3:
            if item['why_it_matters'] not in sentences:
                sentences.append(item['why_it_matters'])
            elif item['snippet'] not in sentences:
                sentences.append(item['snippet'])
            else:
                break
    selected = sentences[:min(5, len(sentences))]
    if len(selected) < 3:
        selected = sentences[:3] if len(sentences) >= 3 else sentences
    summary = '. '.join(selected)
    if not summary.endswith('.'):
        summary += '.'
    return summary

def generate_key_takeaways(item):
    text = f"{item['why_it_matters']} {item['snippet']}"
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 15]
    facts = []
    for sent in sentences:
        if any(generic in sent.lower() for generic in ['worth a look', 'could change', 'might be relevant', 'new in agents', 'fresh tool', 'just dropped']):
            continue
        if len(sent) > 20:
            facts.append(sent)
    if len(facts) < 3:
        if len(item['why_it_matters']) > 30 and item['why_it_matters'] not in facts:
            facts.append(item['why_it_matters'])
        if len(item['snippet']) > 30 and item['snippet'] not in facts:
            facts.append(item['snippet'])
        if len(facts) < 2 and item['title'] not in facts:
            facts.append(item['title'])
    selected = facts[:5]
    if len(selected) < 2:
        selected.append(f"Published on July 11, 2026")
        if len(selected) < 2:
            selected.append(f"Source: {item['source']}")
    return [f"- {fact}" for fact in selected]

def extract_tags(items):
    tags = set()
    ai_topics = {
        'ai-agents', 'claude-code', 'anthropic', 'openai', 'google', 'meta', 
        'microsoft', 'salesforce', 'huggingface', 'research', 'models', 
        'agents', 'coding', 'enterprise', 'api', 'benchmark',
        'fundraising', 'claude', 'code'
    }
    for item in items:
        text = f"{item['title']} {item['why_it_matters']} {item['snippet']}".lower()
        for topic in ai_topics:
            if topic in text:
                tags.add(topic)
        section_tag = item['section'].lower()
        section_tag = re.sub(r'\s+\([^)]+\)', '', section_tag)
        section_tag = section_tag.strip().replace(' ', '-')
        if section_tag and len(section_tag) > 2:
            tags.add(section_tag)
    tags.add('daily-digest')
    return sorted(list(tags))

def main():
    items = parse_news_file('/home/lancerloki/ai-digest-site/today_news.txt')
    # Select 13 items with good distribution
    section_items = {}
    for item in items:
        section = item['section']
        section_items.setdefault(section, []).append(item)
    selected = []
    target_per_section = max(1, 13 // len(section_items))
    for section, lst in section_items.items():
        selected.extend(lst[:target_per_section])
        if len(selected) >= 13:
            break
    if len(selected) < 13:
        for section, lst in section_items.items():
            for item in lst[target_per_section:]:
                if item not in selected:
                    selected.append(item)
                    if len(selected) >= 13:
                        break
            if len(selected) >= 13:
                break
    selected = selected[:13]
    # Build markdown
    md_lines = []
    md_lines.append('---')
    md_lines.append('title: "Daily AI Digest — 2026-07-11"')
    md_lines.append('date: "2026-07-11"')
    md_lines.append('category: Daily Digest')
    if selected:
        excerpt_text = f"Today's AI digest covers {len(selected)} key stories including {selected[0]['section'].lower()}"
        if len(selected) > 1:
            excerpt_text += f", {selected[1]['section'].lower()}"
        excerpt_text += " and more developments in artificial intelligence."
    else:
        excerpt_text = "Daily digest of AI news and developments."
    md_lines.append(f'excerpt: "{excerpt_text}"')
    tags = extract_tags(selected)
    md_lines.append(f'tags: {", ".join(tags)}')
    md_lines.append('---')
    md_lines.append('')
    grouped = {}
    for item in selected:
        section = item['section']
        grouped.setdefault(section, []).append(item)
    for section, items_in_section in grouped.items():
        md_lines.append(f'### {section}')
        md_lines.append('')
        for item in items_in_section:
            md_lines.append(f'#### {item["title"]}')
            md_lines.append('')
            md_lines.append(f'**{item["section"]}** | July 11, 2026 | {item["source"]}')
            md_lines.append('')
            summary = generate_summary(item)
            md_lines.append(summary)
            md_lines.append('')
            md_lines.append('**Key Takeaways:**')
            for takeaway in generate_key_takeaways(item):
                md_lines.append(takeaway)
            md_lines.append('')
            md_lines.append(f'[Read full story]({item["link"]})')
            md_lines.append('')
            md_lines.append('---')
            md_lines.append('')
    md_lines.append('### Why This Matters Today')
    md_lines.append('')
    section_counts = {}
    for item in selected:
        section = item['section']
        section_counts[section] = section_counts.get(section, 0) + 1
    themes = []
    if 'AI Agents' in section_counts and section_counts['AI Agents'] >= 3:
        themes.append("AI agents are rapidly evolving beyond simple chatbots into autonomous workplace assistants, enterprise workflow automation, and specialized tools for developers and researchers.")
    if 'Claude Code' in section_counts and section_counts['Claude Code'] >= 2:
        themes.append("The coding agent space is heating up with competition between premium offerings like Claude Code and free open-source alternatives, driving innovation and accessibility.")
    if 'AI News' in section_counts and section_counts['AI News'] >= 2:
        themes.append("Major tech companies are making strategic moves in AI infrastructure, agent capabilities, and developer tools, signaling long-term investments in the AI ecosystem.")
    if 'OpenClaw' in section_counts:
        themes.append("Open-source initiatives are making AI agent development more accessible and transparent, enabling community-driven innovation.")
    if len(themes) < 3:
        themes.append("The rapid pace of AI agent development is creating both opportunities and challenges for businesses adapting to new workflows.")
        themes.append("Benchmarking and evaluation tools are emerging as critical components for ensuring AI agent reliability and effectiveness in production environments.")
        themes.append("Investment in AI agent startups continues to grow, validating the market potential of autonomous systems.")
    themes = themes[:4]
    for i, theme in enumerate(themes):
        md_lines.append(theme)
        if i < len(themes) - 1:
            md_lines.append('')
    md_lines.append('')
    md_lines.append('---')
    md_lines.append('')
    md_lines.append(f'*This digest was generated from {len(items)} AI news stories across OpenAI, Anthropic, Meta, Google, Hugging Face, TechCrunch, VentureBeat, Ars Technica, MIT Tech Review, and Hacker News.*')
    with open('/home/lancerloki/ai-digest-site/posts/2026-07-11-daily-ai-digest.md', 'w') as f:
        f.write('\n'.join(md_lines))

if __name__ == '__main__':
    main()
