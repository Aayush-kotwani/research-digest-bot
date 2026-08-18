import feedparser
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

ARXIV_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.CV+OR+cat:cs.CL&sortBy=submittedDate&sortOrder=desc&max_results=10"

RSS_FEEDS = [
    "http://googleresearch.blogspot.com/atom.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://huggingface.co/blog/feed.xml",
]

def fetch_arxiv() -> List[Dict]:
    logger.info("Fetching arXiv...")
    feed = feedparser.parse(ARXIV_URL)
    results = []
    for entry in feed.entries:
        results.append({
            "id": entry.id,
            "title": entry.title,
            "url": entry.link,
            "abstract": getattr(entry, 'summary', ''),
            "tags": [t['term'] for t in entry.tags] if 'tags' in entry else ['arxiv'],
            "source": "arXiv"
        })
    return results

def fetch_rss() -> List[Dict]:
    results = []
    for url in RSS_FEEDS:
        logger.info(f"Fetching RSS: {url}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # top 5 per blog
                item_id = getattr(entry, 'id', entry.link)
                results.append({
                    "id": item_id,
                    "title": entry.title,
                    "url": entry.link,
                    "abstract": getattr(entry, 'summary', getattr(entry, 'description', '')),
                    "tags": ['blog'],
                    "source": feed.feed.get('title', 'Blog')
                })
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
    return results

def fetch_all() -> List[Dict]:
    return fetch_arxiv() + fetch_rss()
