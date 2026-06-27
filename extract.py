import re, json, os

os.chdir('/data/data/com.termux/files/home/daily-ai-digest')
results = []

# Article 1 - from Wayback Machine cache
with open('article1_wayback.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()
desc_m = re.search(r'<meta property="og:description" content="([^"]+)"', html)
if not desc_m:
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
desc = desc_m.group(1).strip() if desc_m else 'No description available'
title_m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
if not title_m:
    title_m = re.search(r'<title>([^<]+)</title>', html)
title = title_m.group(1).strip() if title_m else 'Unknown title'
results.append({'title': title, 'description': desc, 'url': 'https://openai.com/index/previewing-gpt-5-6-sol/', 'source': 'openai.com'})

# Article 2 - Washington Post (failed to fetch)
results.append({'title': 'Failed to fetch', 'description': 'Washington Post not reachable from this network (connection timeout)', 'url': 'https://www.washingtonpost.com/technology/2026/06/26/openai-says-us-government-will-vet-users-its-latest-ai-model/', 'source': 'washingtonpost.com'})

# Articles 3-8
articles = [
    ('article3.html', 'https://www.semafor.com/article/06/27/2026/us-releases-powerful-anthropic-model-mythos-to-some-us-companies', 'semafor.com'),
    ('article4.html', 'https://alephneuro.com/blog/ultrasound-brain', 'alephneuro.com'),
    ('article5.html', 'https://blog.doubleword.ai/frontier-os-llm', 'blog.doubleword.ai'),
    ('article6.html', 'https://github.com/workweave/router', 'github.com'),
    ('article7.html', 'https://spectrum.ieee.org/ai-in-mathematics', 'spectrum.ieee.org'),
    ('article8.html', 'https://grack.com/blog/2026/06/25/dissecting-a-failed-nation-state-attack/', 'grack.com'),
]

for filename, url, source in articles:
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists(filepath):
        results.append({'title': 'Failed to fetch', 'description': 'Could not reach URL', 'url': url, 'source': source})
        continue
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    desc_m = re.search(r'<meta property="og:description" content="([^"]+)"', html)
    if not desc_m:
        desc_m = re.search(r'<meta name="description" content="([^"]+)"', html)
    desc = desc_m.group(1).strip() if desc_m else 'No description available'
    
    title_m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if not title_m:
        title_m = re.search(r'<title>([^<]+)</title>', html)
    title = title_m.group(1).strip() if title_m else 'Unknown title'
    
    results.append({'title': title, 'description': desc, 'url': url, 'source': source})

print(json.dumps(results, indent=2))
