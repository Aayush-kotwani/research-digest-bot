import os
import re
from datetime import datetime
from typing import List, Dict
from summarizer import summarize_text

DIGEST_DIR = os.path.join(os.path.dirname(__file__), 'digest')
README_PATH = os.path.join(os.path.dirname(__file__), 'README.md')

def format_tags(tags: List[str]) -> str:
    cleaned = []
    for t in tags:
        t = re.sub(r'[^a-zA-Z0-9]', '', t.lower())
        if t:
            cleaned.append(f"#{t}")
    return " ".join(cleaned[:5])

def write_digest(items: List[Dict]) -> str:
    """Writes the daily digest and returns the file path."""
    if not items:
        return ""
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DIGEST_DIR, f"{date_str}.md")
    
    # Load existing content if running multiple times a day
    existing_content = ""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    else:
        existing_content = f"# Research Digest: {date_str}\n\n"
        
    lines = []
    for item in items:
        summary = summarize_text(item['abstract'])
        tags = format_tags(item['tags'])
        
        lines.append(f"## [{item['title']}]({item['url']})")
        lines.append(f"**Source:** {item['source']} | {tags}\n")
        lines.append(f"{summary}\n")
        lines.append("---\n")
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(existing_content + "\n".join(lines))
        
    return filepath

def update_readme():
    """Updates the README.md with the latest 10 entries using placeholders."""
    digests = []
    if os.path.exists(DIGEST_DIR):
        for f in os.listdir(DIGEST_DIR):
            if f.endswith('.md'):
                digests.append(f)
    
    digests.sort(reverse=True)
    latest_10 = digests[:10]
    
    lines = ["\n"]
    for d in latest_10:
        date_str = d.replace('.md', '')
        lines.append(f"- [{date_str}](digest/{d})")
    lines.append("\n")
    
    replacement = "\n".join(lines)
    
    if os.path.exists(README_PATH):
        with open(README_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        pattern = r'(<!-- DIGEST_LIST_START -->).*?(<!-- DIGEST_LIST_END -->)'
        new_content = re.sub(pattern, r'\1' + replacement + r'\2', content, flags=re.DOTALL)
        
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
