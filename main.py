import time
import random
import logging
import os
from fetch import fetch_all
from dedupe import is_seen, mark_seen
from writer import write_digest, update_readme
from committer import perform_commits

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='run_log.txt', filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def main():
    if not os.environ.get("SKIP_SLEEP"):
        if os.environ.get("GITHUB_ACTIONS"):
            # Sleep up to 2 hours in CI to make the cron timing organic
            sleep_time = random.randint(1, 120 * 60)
        else:
            # Sleep max 5 seconds locally
            sleep_time = random.randint(1, 5)
        
        logging.info(f"Sleeping for {sleep_time} seconds before running...")
        time.sleep(sleep_time)

    logging.info("Starting research-digest-bot run.")
    
    all_items = fetch_all()
    new_items = []
    
    for item in all_items:
        if not is_seen(item['id']):
            new_items.append(item)
            mark_seen(item['id'])
            
    if not new_items:
        logging.info("No new items found today.")
    else:
        logging.info(f"Found {len(new_items)} new items. Writing digest...")
        write_digest(new_items)
        update_readme()
        
    repo_path = os.path.dirname(os.path.abspath(__file__))
    perform_commits(repo_path)
    
    logging.info("Run complete.")

if __name__ == "__main__":
    main()
