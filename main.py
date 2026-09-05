import time
import random
import logging
import os
from datetime import datetime
from fetch import fetch_all, get_fallback_items
from dedupe import is_seen, mark_seen
from writer import append_digest_entry, write_note_entry, update_readme, DIGEST_DIR, NOTES_DIR, README_PATH
from committer import commit_changes, make_commit_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='run_log.txt', filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def main():
    if not os.environ.get("SKIP_SLEEP"):
        if os.environ.get("GITHUB_ACTIONS") and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
            # Sleep up to 2 hours in CI for scheduled cron to make timing organic
            sleep_time = random.randint(1, 120 * 60)
        else:
            sleep_time = random.randint(1, 5)
        
        logging.info(f"Sleeping for {sleep_time} seconds before running...")
        time.sleep(sleep_time)

    logging.info("Starting research-digest-bot run.")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Fetch items
    all_items = fetch_all()
    new_items = [item for item in all_items if not is_seen(item['id'])]
    
    # 2. If no new items found from feeds (e.g. weekend/slow arXiv day), draw from foundational backlog
    if not new_items:
        logging.info("Feeds returned 0 unseen items. Checking fallback classic reading list...")
        fallback_candidates = [f for f in get_fallback_items() if not is_seen(f['id'])]
        if fallback_candidates:
            # Pick 1-2 classic papers so there's always meaningful research logged
            new_items = fallback_candidates[:random.randint(1, min(2, len(fallback_candidates)))]
            logging.info(f"Selected {len(new_items)} foundational paper(s) for today's digest.")
        else:
            logging.warning("All fallback items have also been logged previously.")

    if not new_items:
        logging.warning("Zero new items available to log. Checking if README needs tag cloud refresh...")
        update_readme()
        commit_changes(["README.md"], "docs: refresh tag cloud and rolling index")
        logging.info("Run complete with tag cloud refresh.")
        return

    logging.info(f"Processing {len(new_items)} new items for {date_str}.")

    # 3. Determine random number of commits between 1 and 5
    target_commits = random.randint(1, 5)
    logging.info(f"Targeting {target_commits} commit(s) for this run.")

    primary_item = new_items[0]
    extra_items = new_items[1:]
    digest_file = os.path.join(DIGEST_DIR, f"{date_str}.md")
    db_file = os.path.join(os.path.dirname(__file__), "seen.db")

    if target_commits == 1:
        # All in one commit
        for item in new_items:
            append_digest_entry(item, date_str)
            mark_seen(item['id'])
        update_readme()
        msg = make_commit_message("digest_primary", primary_item['title'], primary_item.get('tags', []))
        commit_changes([digest_file, README_PATH, db_file], msg)

    elif target_commits == 2:
        # Commit 1: Digest entry
        for item in new_items:
            append_digest_entry(item, date_str)
            mark_seen(item['id'])
        msg1 = make_commit_message("digest_primary", primary_item['title'], primary_item.get('tags', []))
        commit_changes([digest_file], msg1)

        # Commit 2: README index & seen tracker
        update_readme()
        msg2 = make_commit_message("readme")
        commit_changes([README_PATH, db_file], msg2)

    elif target_commits == 3:
        # Commit 1: Primary paper to digest
        append_digest_entry(primary_item, date_str)
        mark_seen(primary_item['id'])
        msg1 = make_commit_message("digest_primary", primary_item['title'], primary_item.get('tags', []))
        commit_changes([digest_file], msg1)

        # Commit 2: Extra papers OR deep-dive note
        if extra_items:
            for item in extra_items:
                append_digest_entry(item, date_str)
                mark_seen(item['id'])
            msg2 = make_commit_message("digest_extra", extra_items[0]['title'])
            commit_changes([digest_file], msg2)
        else:
            note_path = write_note_entry(primary_item, date_str)
            msg2 = make_commit_message("notes", primary_item['title'])
            commit_changes([note_path], msg2)

        # Commit 3: README & tracker
        update_readme()
        msg3 = make_commit_message("readme")
        commit_changes([README_PATH, db_file], msg3)

    elif target_commits == 4:
        # Commit 1: Primary paper
        append_digest_entry(primary_item, date_str)
        mark_seen(primary_item['id'])
        msg1 = make_commit_message("digest_primary", primary_item['title'], primary_item.get('tags', []))
        commit_changes([digest_file], msg1)

        # Commit 2: Additional papers
        if extra_items:
            for item in extra_items:
                append_digest_entry(item, date_str)
                mark_seen(item['id'])
            msg2 = make_commit_message("digest_extra", extra_items[0]['title'])
            commit_changes([digest_file], msg2)

        # Commit 3: Notes take
        note_path = write_note_entry(primary_item, date_str)
        msg3 = make_commit_message("notes", primary_item['title'])
        commit_changes([note_path], msg3)

        # Commit 4: README & tracker
        update_readme()
        msg4 = make_commit_message("readme")
        commit_changes([README_PATH, db_file], msg4)

    else: # target_commits == 5
        # Commit 1: Primary paper
        append_digest_entry(primary_item, date_str)
        mark_seen(primary_item['id'])
        msg1 = make_commit_message("digest_primary", primary_item['title'], primary_item.get('tags', []))
        commit_changes([digest_file], msg1)

        # Commit 2: Additional papers
        if extra_items:
            for item in extra_items:
                append_digest_entry(item, date_str)
                mark_seen(item['id'])
            msg2 = make_commit_message("digest_extra", extra_items[0]['title'])
            commit_changes([digest_file], msg2)

        # Commit 3: Notes entry
        note_path = write_note_entry(primary_item, date_str)
        msg3 = make_commit_message("notes", primary_item['title'])
        commit_changes([note_path], msg3)

        # Commit 4: README index & tag cloud
        update_readme()
        msg4 = make_commit_message("readme")
        commit_changes([README_PATH], msg4)

        # Commit 5: Seen tracker DB sync
        msg5 = make_commit_message("tracker")
        commit_changes([db_file], msg5)

    logging.info("Run complete.")

if __name__ == "__main__":
    main()
