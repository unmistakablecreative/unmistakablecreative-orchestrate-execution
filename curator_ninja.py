import json
import feedparser
import os
import schedule
import time
import threading
import concurrent.futures
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

NEWS_SOURCES_FILE = "news_sources.json"
CURATED_ARTICLES_FILE = "curator_articles.json"

class CuratorNinja:
    def __init__(self, run_scheduler=False):
        """Initialize CuratorNinja and start the scheduler only if required."""
        self.load_news_sources()
        if run_scheduler:
            self.start_scheduler()

    def load_news_sources(self):
        """Loads RSS sources from JSON file."""
        if os.path.exists(NEWS_SOURCES_FILE):
            with open(NEWS_SOURCES_FILE, "r") as f:
                self.news_feed_urls = json.load(f)
        else:
            self.news_feed_urls = [
                "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
                "https://news.google.com/rss/search?q=machine+learning&hl=en-US&gl=US&ceid=US:en",
                "https://news.google.com/rss/search?q=AI+ethics&hl=en-US&gl=US&ceid=US:en",
                "https://news.google.com/rss/search?q=AI+startups&hl=en-US&gl=US&ceid=US:en",
                "https://news.google.com/rss/search?q=AI+and+creativity&hl=en-US&gl=US&ceid=US:en"
            ]
            self.save_news_sources()

    def save_news_sources(self):
        """Saves current RSS sources to JSON file."""
        with open(NEWS_SOURCES_FILE, "w") as f:
            json.dump(self.news_feed_urls, f, indent=2)

    def start_scheduler(self):
        """Runs the fetch process daily at 6 AM."""
        schedule.every().day.at("06:00").do(self.fetch_news)

        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        logging.info("✅ Scheduler started. Curator Ninja will run at 6 AM daily.")

    def fetch_news(self):
        """Fetches AI news from RSS feeds and saves them."""
        logging.info("📰 Fetching AI news from RSS feeds...")
        articles = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(feedparser.parse, url): url for url in self.news_feed_urls}

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    feed = future.result()
                    if not feed.entries:
                        logging.warning(f"⚠️ No entries found for {url}")
                        continue

                    for entry in feed.entries[:5]:  # Fetching top 5 per category
                        articles.append({
                            "title": entry.title,
                            "link": entry.link,
                            "published": entry.published if hasattr(entry, 'published') else str(datetime.utcnow())
                        })

                except Exception as e:
                    logging.error(f"❌ Error processing RSS feed {url}: {e}")

        self.store_curations(articles)
        return articles

    def store_curations(self, articles):
        """Stores curated AI news in JSON file."""
        logging.info("💾 Saving curated news to JSON file...")
        try:
            existing_data = []
            if os.path.exists(CURATED_ARTICLES_FILE):
                with open(CURATED_ARTICLES_FILE, "r") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []  # Ensure it's a list before extending

            existing_data.extend(articles)

            with open(CURATED_ARTICLES_FILE, "w") as f:
                json.dump(existing_data, f, indent=2)

            logging.info(f"✅ Saved {len(articles)} articles to {CURATED_ARTICLES_FILE}.")

        except Exception as e:
            logging.error(f"❌ Error saving data to {CURATED_ARTICLES_FILE}: {e}")

    def get_curated_news(self):
        """Fetches stored curated news from JSON."""
        logging.info("📥 Fetching stored curated news...")
        if os.path.exists(CURATED_ARTICLES_FILE):
            with open(CURATED_ARTICLES_FILE, "r") as f:
                return json.load(f)
        return {"error": "⚠️ No curated news available yet."}

    def execute(self, action, params=None):
        """Executes tasks based on action type."""
        if action == "fetch_and_store":
            return self.fetch_news()
        elif action == "get_curated_news":
            return self.get_curated_news()
        else:
            logging.error(f"❌ Unsupported action: {action}")
            return {"error": f"Unsupported action: {action}"}

    def get_supported_actions(self):
        """Returns supported actions for Orchestrate."""
        return {
            "fetch_and_store": [],
            "get_curated_news": []
        }

# Handle external requests
def handler(event, context):
    """Handles API requests or server calls."""
    if isinstance(event, dict) and "action" in event:
        curator_ninja = CuratorNinja(run_scheduler=False)  # Ensure scheduler does NOT start
        return curator_ninja.execute(event["action"], event.get("params"))

    logging.error("❌ Invalid request format.")
    return {"error": "Invalid request format"}

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1 and sys.argv[1] == "execute":
        """Handles CLI execution requests without starting the scheduler."""
        params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        action = sys.argv[2]

        curator_ninja = CuratorNinja(run_scheduler=False)  # Prevents scheduler from running
        result = curator_ninja.execute(action, params)
        print(json.dumps(result, indent=2))
    else:
        """Runs in continuous mode only when explicitly started."""
        logging.info("🚀 Curator Ninja is running continuously...")
        curator_ninja_instance = CuratorNinja(run_scheduler=True)  # Now only starts the scheduler when needed
        while True:
            time.sleep(60)  # Keeps the script alive indefinitely
