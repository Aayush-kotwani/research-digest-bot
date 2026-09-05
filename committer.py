import os
import random
import logging
from git import Repo

logger = logging.getLogger(__name__)

def get_repo(repo_path: str = None) -> Repo:
    if not repo_path:
        repo_path = os.path.dirname(os.path.abspath(__file__))
    return Repo(repo_path)

def commit_changes(files: list, message: str, repo_path: str = None) -> bool:
    """Stages specified files and commits them with the given message."""
    try:
        repo = get_repo(repo_path)
        for f in files:
            # If path is absolute, make it relative to repo root
            if os.path.isabs(f):
                f = os.path.relpath(f, repo.working_tree_dir)
            repo.index.add([f])

        logger.info(f"Committed: {message} ({files})")
        repo.index.commit(message)
        return True
    except Exception as e:
        logger.error(f"Failed to commit {files}: {e}")
        return False

def make_commit_message(category: str, title: str = "", tags: list = None) -> str:
    """Generates plain, realistic, non-uniform commit messages."""
    tags_str = f" #{tags[0]}" if tags else ""
    clean_title = (title[:30] + "...") if len(title) > 30 else title

    templates = {
        "digest_primary": [
            f"add: new digest entries from arxiv/rss{tags_str}",
            f"add: ML digest entry for {clean_title}",
            f"feat: new paper summaries added to digest",
            f"log: research finds for today",
            f"add: recent papers on {clean_title}",
        ],
        "digest_extra": [
            f"add: secondary paper summaries to digest",
            f"update: digest with additional finds",
            f"add: more reading entries to daily log",
            f"digest: add extra notes on {clean_title}",
        ],
        "readme": [
            "docs: update readme index and tag cloud",
            "update: refresh readme with latest digest link",
            "docs: sync recent digests list",
            "update index & tag cloud in readme",
        ],
        "notes": [
            f"notes: add reading notes on {clean_title}",
            f"notes: preliminary take on {clean_title}",
            f"notes: add takeaways and open questions for {clean_title}",
            "notes: add personal deep dive note",
        ],
        "tracker": [
            "chore: sync seen tracking database",
            "update seen tracker",
            "chore: update deduplication state",
            "db: sync seen.db",
        ],
    }

    choices = templates.get(category, ["minor updates and polish"])
    return random.choice(choices)
