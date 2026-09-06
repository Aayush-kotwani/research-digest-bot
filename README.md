# Research Digest Bot 🤖📚

This repository serves two purposes: it houses the code for **research-digest-bot**, and it acts as the destination for the automated ML/DL/AI research digests that the bot creates. 

> **Transparency Note**: All paper digests and commit activity in this repository are fully automated by this bot. For more information, please see [BOT.md](BOT.md).

## Recent Digests
<!-- DIGEST_LIST_START -->

- [2026-09-06](digest/2026-09-06.md)
- [2026-09-05](digest/2026-09-05.md)
- [2026-09-04](digest/2026-09-04.md)
- [2026-09-03](digest/2026-09-03.md)
- [2026-09-02](digest/2026-09-02.md)
- [2026-08-29](digest/2026-08-29.md)
- [2026-08-27](digest/2026-08-27.md)
- [2026-08-26](digest/2026-08-26.md)
- [2026-08-25](digest/2026-08-25.md)
- [2026-08-22](digest/2026-08-22.md)

<!-- DIGEST_LIST_END -->

## Topic Tag Cloud
<!-- TAG_CLOUD_START -->
`#blog` (72) `#research` (40) `#deeplearning` (2) `#transformers` (1) `#attention` (1) `#nlp` (1) `#computervision` (1) `#resnet` (1) `#lora` (1) `#finetuning` (1) `#llm` (1) `#peft` (1) `#sort` (1) `#arxiv` (1)

<!-- TAG_CLOUD_END -->

## Occasional Notes
Longer-form or manual notes can be kept in the `notes/` directory.

---

## 🛠️ Project Overview
**research-digest-bot** is an automated pipeline designed to fetch, summarize, and commit the latest Machine Learning and AI research daily. By running on a scheduled GitHub Actions cron job and implementing a randomized commit strategy, it maintains a realistic, organic "running log" of research reading.

## 🧰 Tech Stack
- **`requests`**: Used to query the [arXiv API](https://info.arxiv.org/help/api/index.html) for papers in cs.LG, cs.AI, cs.CV, and cs.CL.
- **`feedparser`**: Used to parse and extract the latest blog posts from major AI lab RSS feeds.
- **Gemini API (`google-genai`)**: The `gemini-2.5-flash` model is used to intelligently rewrite scraped abstracts into concise, original one-paragraph summaries.
- **`GitPython`**: Automates parsing the repository's git index and generating a randomized number of commits (1-5) per run to simulate organic activity.
- **SQLite (`seen.db`)**: Tracks previously seen paper IDs and blog URLs to ensure we don't process or commit the same item twice.
- **GitHub Actions**: Orchestrates the scheduled daily runs and pushes the results back to the repository.

## 🏗️ Architecture & Workflow
The pipeline runs daily through the following steps:
1. **Trigger**: `.github/workflows/daily_digest.yml` wakes up the `main.py` entrypoint.
2. **Fetch**: `fetch.py` queries arXiv and RSS feeds for recent items.
3. **Dedupe**: `dedupe.py` checks each item against `seen.db`. Known items are discarded.
4. **Summarize**: `summarizer.py` calls the Gemini API to rewrite the abstract for each new item.
5. **Write**: `writer.py` generates the daily markdown digest in `digest/YYYY-MM-DD.md` and dynamically updates the **Recent Digests** index in this README.
6. **Commit & Push**: `committer.py` logically separates the modified files (e.g., `seen.db`, the new digest, `README.md`) into 1 to 5 random commits with natural-sounding commit messages. The GitHub Action then pushes these back to the repository.

## 📂 Repository Structure
| File/Directory | Description |
|---|---|
| `.github/workflows/daily_digest.yml` | GitHub Actions configuration for daily execution. |
| `digest/` | Directory where the generated daily markdown digests are stored. |
| `notes/` | Directory reserved for manual, longer-form notes. |
| `BOT.md` | Transparency documentation explaining the automated nature of the repo. |
| `committer.py` | Git automation and commit masking logic. |
| `dedupe.py` | SQLite database handler for tracking seen URLs/IDs. |
| `fetch.py` | API integration for arXiv and RSS parsing. |
| `main.py` | The main entrypoint and orchestrator. |
| `requirements.txt` | Python dependencies. |
| `seen.db` | SQLite database persisting the deduplication state. |
| `summarizer.py` | Gemini API integration and text truncation fallbacks. |
| `writer.py` | Markdown generation and README index updater. |

## 🚀 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/research-digest-bot.git
   cd research-digest-bot
   ```

2. **Install dependencies:**
   Ensure you have Python 3.11+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Gemini API Key:**
   To use the summarization features locally, copy the environment template:
   ```bash
   cp .env.example .env
   ```
   Add your API key to `.env`. 
   
   **For GitHub Actions**: Go to your repository on GitHub, navigate to **Settings > Secrets and variables > Actions**, and add a new repository secret named `GEMINI_API_KEY`.

4. **Understand the Cron Schedule:**
   The bot is scheduled to run daily at `02:30 UTC`. However, to simulate organic activity, `main.py` enforces a random sleep delay of up to 2 hours before fetching. To bypass this sleep delay during manual executions, the script checks if it's being triggered manually via push or workflow dispatch.

## ⚙️ Configuration

- **RSS Sources & arXiv Categories**: To change the blogs or arXiv categories the bot monitors, modify the `ARXIV_URL` and `RSS_FEEDS` constants at the top of `fetch.py`.
- **Commit Frequency**: To change the maximum number of commits generated per run, adjust the `max_commits` variable in `committer.py` (currently capped at 5).

## 🧪 Local Testing

You can safely test the script locally without pushing to GitHub.
1. Run the main script with the sleep delay disabled:
   ```bash
   # Windows PowerShell
   $env:SKIP_SLEEP="1"; python main.py
   
   # Linux/macOS
   SKIP_SLEEP=1 python main.py
   ```
2. The script will fetch new items, write them to `digest/`, update `seen.db`, and create local commits.
3. You can review the commits using `git log` and undo them using `git reset HEAD~N` if necessary.

## 📄 License
[MIT License](LICENSE) (or add your preferred license here).
