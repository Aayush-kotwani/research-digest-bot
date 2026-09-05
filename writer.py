import os
import re
from datetime import datetime
from typing import List, Dict
from collections import Counter
from summarizer import summarize_text

DIGEST_DIR = os.path.join(os.path.dirname(__file__), 'digest')
NOTES_DIR = os.path.join(os.path.dirname(__file__), 'notes')
README_PATH = os.path.join(os.path.dirname(__file__), 'README.md')

def format_tags(tags: List[str]) -> str:
    cleaned = []
    for t in tags:
        t = re.sub(r'[^a-zA-Z0-9]', '', t.lower())
        if t:
            cleaned.append(f"#{t}")
    return " ".join(cleaned[:5])

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text[:40]

def append_digest_entry(item: Dict, date_str: str = None) -> str:
    """Writes or appends a single item to the daily digest file."""
    if not os.path.exists(DIGEST_DIR):
        os.makedirs(DIGEST_DIR, exist_ok=True)

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    filepath = os.path.join(DIGEST_DIR, f"{date_str}.md")

    if not os.path.exists(filepath):
        content = f"# Research Digest: {date_str}\n\n"
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

    summary = summarize_text(item['abstract'])
    tags = format_tags(item.get('tags', []))

    entry_md = f"## [{item['title']}]({item['url']})\n"
    entry_md += f"**Source:** {item.get('source', 'Web')} | {tags}\n\n"
    entry_md += f"{summary}\n\n"
    entry_md += "---\n\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content + entry_md)

    return filepath

def write_digest(items: List[Dict], date_str: str = None) -> str:
    """Writes multiple items to the daily digest file."""
    filepath = ""
    for item in items:
        filepath = append_digest_entry(item, date_str)
    return filepath

def write_note_entry(item: Dict, date_str: str = None) -> str:
    """Writes a longer-form personal note for an interesting paper."""
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR, exist_ok=True)

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    slug = slugify(item['title'])
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(NOTES_DIR, filename)

    tags = format_tags(item.get('tags', []))
    summary = summarize_text(item['abstract'])

    content = f"""# Reading Notes: {item['title']}

- **Date:** {date_str}
- **Source:** [{item['url']}]({item['url']})
- **Category / Tags:** {tags}

## Summary & Core Contribution
{summary}

## Key Highlights
- Focuses on practical ML/DL performance and architecture considerations.
- Method addresses efficiency, scalability, and generalization.

## Open Questions & Future Reads
- How does this approach compare on out-of-distribution benchmarks?
- Potential applicability to multi-modal and agentic workflows.
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")

    return filepath

def extract_tag_cloud() -> str:
    """Collects top tags from recent digest markdown files."""
    tag_counter = Counter()
    if os.path.exists(DIGEST_DIR):
        for f in os.listdir(DIGEST_DIR):
            if f.endswith('.md'):
                with open(os.path.join(DIGEST_DIR, f), 'r', encoding='utf-8') as fp:
                    text = fp.read()
                    found_tags = re.findall(r'#([a-zA-Z0-9_-]+)', text)
                    tag_counter.update(found_tags)

    if not tag_counter:
        return "`#ml` `#ai` `#transformers` `#deeplearning`"

    top_tags = tag_counter.most_common(15)
    return " ".join([f"`#{tag}` ({count})" for tag, count in top_tags])

def update_readme():
    """Updates README.md with the latest digests list and tag cloud."""
    digests = []
    if os.path.exists(DIGEST_DIR):
        for f in os.listdir(DIGEST_DIR):
            if f.endswith('.md'):
                digests.append(f)

    digests.sort(reverse=True)
    latest_10 = digests[:10]

    list_lines = ["\n"]
    for d in latest_10:
        date_str = d.replace('.md', '')
        list_lines.append(f"- [{date_str}](digest/{d})")
    list_lines.append("\n")

    digest_replacement = "\n".join(list_lines)
    tag_cloud_replacement = f"\n{extract_tag_cloud()}\n\n"

    if os.path.exists(README_PATH):
        with open(README_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update digest list
        if '<!-- DIGEST_LIST_START -->' in content and '<!-- DIGEST_LIST_END -->' in content:
            content = re.sub(
                r'(<!-- DIGEST_LIST_START -->).*?(<!-- DIGEST_LIST_END -->)',
                r'\1' + digest_replacement + r'\2',
                content,
                flags=re.DOTALL
            )

        # Update tag cloud if markers exist
        if '<!-- TAG_CLOUD_START -->' in content and '<!-- TAG_CLOUD_END -->' in content:
            content = re.sub(
                r'(<!-- TAG_CLOUD_START -->).*?(<!-- TAG_CLOUD_END -->)',
                r'\1' + tag_cloud_replacement + r'\2',
                content,
                flags=re.DOTALL
            )

        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
