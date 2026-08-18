import os
import random
import logging
from git import Repo

logger = logging.getLogger(__name__)

def generate_commit_message(files):
    has_digest = any('digest/' in f for f in files)
    has_readme = any('README.md' in f for f in files)
    has_db = any('seen.db' in f for f in files) or any('seen.json' in f for f in files)
    
    if has_digest and has_readme and has_db:
        return random.choice([
            "add: daily research digest and update index",
            "feat: new papers added to digest",
            "update daily digest and db tracking"
        ])
    elif has_digest and has_readme:
        return random.choice([
            "add: latest ML papers and update README index",
            "update daily digest and index"
        ])
    elif has_digest:
        return random.choice([
            "add: latest ML papers and blog posts to digest",
            "feat: new digest entry",
            "log new research finds"
        ])
    elif has_readme:
        return random.choice([
            "docs: update readme index",
            "update tag cloud and index in readme",
            "refresh readme with latest digest link"
        ])
    elif has_db:
        return random.choice([
            "chore: sync seen tracking db",
            "update seen tracker",
            "chore: update deduplication database"
        ])
    else:
        return random.choice([
            "minor formatting and updates",
            "fix: minor tweaks",
            "update files"
        ])

def perform_commits(repo_path: str):
    logger.info(f"Checking for changes in {repo_path}")
    try:
        repo = Repo(repo_path)
    except Exception as e:
        logger.error(f"Failed to load git repo: {e}")
        return

    # changed files
    changed_files = [item.a_path for item in repo.index.diff(None)]
    untracked_files = repo.untracked_files
    
    all_changes = list(set(changed_files + untracked_files))
    if not all_changes:
        logger.info("No changes to commit.")
        return
        
    logger.info(f"Found {len(all_changes)} changed files: {all_changes}")
    
    max_commits = min(5, len(all_changes))
    num_commits = random.randint(1, max_commits)
    
    logger.info(f"Will generate {num_commits} commits.")
    
    random.shuffle(all_changes)
    chunks = [all_changes[i::num_commits] for i in range(num_commits)]
    
    for chunk in chunks:
        if not chunk: continue
        for file in chunk:
            repo.index.add([file])
        
        msg = generate_commit_message(chunk)
        logger.info(f"Committing: {msg} for files {chunk}")
        repo.index.commit(msg)
