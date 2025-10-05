import os
import time
import json
import random
import csv
from datetime import datetime
from playwright.sync_api import sync_playwright

# ==== CONFIG ====
COOKIE_FILE = os.path.join("..","cookies", "twitter_cookies.json")
QUERY_LIST = [
    "traffic jam India", 
    "traffic congestion India", 
    "road jam India", 
    "#trafficjam Bangalore", 
    "traffic jam Delhi",
    "traffic jam Mumbai",  
    "traffic jam Chennai",  
]
MAX_TWEETS = 30
DATE = datetime.today().strftime("%Y-%m-%d")
OUT_FILE = os.path.join("..", "playwright_output", f"traffic1_{DATE}.csv")
LOG_FILE = os.path.join("..", "logs", "scraper_playwright.log")


def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)

def load_cookies(context):
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        # sanitize cookies
        for c in cookies:
            if "sameSite" not in c or c["sameSite"] not in ["Strict", "Lax", "None"]:
                c["sameSite"] = "Lax"

        context.add_cookies(cookies)
        log("✅ Cookies loaded")

    except FileNotFoundError:
        log("⚠️ No cookie file found, might get blocked")

def human_like_wait(min_s=1.5, max_s=4.0):
    """Random sleep to mimic human pauses"""
    time.sleep(random.uniform(min_s, max_s))

def scrape(query):
    with sync_playwright() as p:
        # Random headless mode
        headless_mode = random.choice([True, False])
        browser = p.firefox.launch(headless=headless_mode)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": random.randint(1200, 1920), "height": random.randint(700, 1080)},
        )

        load_cookies(context)
        page = context.new_page()

        # Open search page
        url = f"https://x.com/search?q={query}&src=typed_query&f=live"
        page.goto(url, timeout=60000)
        log(f"🔍 Opened search: {url}")

        tweets = []
        seen_ids = set()

        # Prepare CSV file
        if not os.path.exists(OUT_FILE):
            with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "user", "date", "content"])
                writer.writeheader()

        while len(tweets) < MAX_TWEETS:
            human_like_wait(2, 5)
            tweet_elements = page.locator("article").all()
            new_tweets = []

            for t in tweet_elements:
                if len(tweets) >= MAX_TWEETS:
                    break
                try:
                    content = t.locator("div[data-testid='tweetText']").inner_text(timeout=2000)
                    user = t.locator("div[dir='ltr'] span").nth(0).inner_text(timeout=2000)
                    date = t.locator("time").get_attribute("datetime")
                    tweet_id = str(hash(content + user + (date or "")))

                    if tweet_id not in seen_ids:
                        seen_ids.add(tweet_id)
                        tweet_data = {"id": tweet_id, "user": user, "date": date, "content": content}
                        tweets.append(tweet_data)
                        new_tweets.append(tweet_data)
                except Exception:
                    continue

            # Append new tweets to CSV
            if new_tweets:
                with open(OUT_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "user", "date", "content"])
                    for tweet in new_tweets:
                        writer.writerow(tweet)

            log(f"📥 Collected {len(tweets)} tweets for query: '{query}'")
            
            # Scroll like a human
            scroll_amount = random.randint(2000, 4000)
            page.mouse.wheel(0, scroll_amount)
            human_like_wait(2, 6)

            if random.random() < 0.1:
                log("⏸️ Taking a longer pause to mimic reading...")
                human_like_wait(8, 15)

            if len(tweet_elements) == 0:
                log("⚠️ No more tweets found, stopping")
                break

        browser.close()
        log(f"✅ Finished scraping {len(tweets)} tweets → {os.path.abspath(OUT_FILE)}")

if __name__ == "__main__":
    log("==== 🚦 Playwright Scraper Started ====")
    for query in QUERY_LIST:
        scrape(query)
    log("==== 🏁 Playwright Scraper Finished ====")
