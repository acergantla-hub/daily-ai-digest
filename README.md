# daily-ai-digest
       Your daily dose of AI agent news. A curated blog covering AI agents, Claude Code, automation tools, and the latest in AI — built with a lightweight static site generator and hosted free on Cloudflare Pages.     Topics/Tags for the repo ai-agents, claude-code, ai-news, static-site, cloudflare-pages, markdown-blog, ai-automation, daily-digest
 markdown
    Daily AI Digest
    
    Your daily dose of AI agent news. A curated blog covering AI agents, Claude Code, automation tools, and the latest in the AI ecosystem.
    
    What is this?
    
    A lightweight static site generator that reads Markdown posts and generates a clean, dark-themed blog. Hosted 100% free on Cloudflare Pages.
    
    How it works
    
    1. Write posts in Markdown inside posts/ folder
    2. Run python build.py to generate the site in dist/
    3. Push to GitHub → auto-deploys to Cloudflare Pages
    
    Adding a new post
    
    Create a new .md file in posts/ with frontmatter:
    
    markdown
    
    title: "Your Post Title"
    date: "2026-05-31"
    excerpt: "A short description for the listing page."
    
 
    
    Source
 
    Where the news came from
    
 
    Why It Matters
    Impact analysis
    
    Recommended Response
    What to do about it
    
    Draft Hook
    Ready-to-use social media post
    
    
    Local development
    
    bash
    pip install markdown
    python build.py
    Open dist/index.html in your browser
    
    
    Tech stack
    
    - Python + Markdown library for site generation
    - Pure HTML/CSS (no frameworks, no JS dependencies)
    - Inter + JetBrains Mono fonts
    - Cloudflare Pages for hosting + CDN + SSL
    
    License
    
    MIT
