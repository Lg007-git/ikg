import os
import time
import json
import random
import csv
from datetime import datetime
from dateutil import parser
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright

# ==== CONFIG ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COOKIE_FILE = os.path.join(BASE_DIR, "..", "cookies", "twitter_cookies.json")
IST = ZoneInfo("Asia/Kolkata")  # Indian Standard Time

QUERY_LIST = [
    "Bangalore traffic jam", "Bengaluru traffic jam", "Bangalore traffic congestion", "Bengaluru traffic congestion",
    "Bangalore road jam", "Bangalore traffic update", "Bengaluru traffic update", "Bangalore traffic alert",
    "Bangalore traffic news", "Bangalore traffic today", "stuck in traffic Bangalore", "horrible traffic Bangalore",
    "bumper to bumper Bangalore", "insane traffic Bangalore", "Bangalore traffic sucks", "jammed roads Bangalore",
    "traffic nightmare Bangalore", "chaos at Silk Board", "Silk Board traffic", "Silk Board jam",
    "Outer Ring Road traffic", "ORR traffic Bangalore", "Electronic City traffic", "Whitefield traffic jam",
    "KR Puram traffic", "Hebbal traffic", "HSR Layout traffic", "Marathahalli traffic",
    "Koramangala traffic jam", "Bellandur traffic", "Yeshwanthpur traffic jam", "Hosur Road traffic",
    "BangaloreTraffic", "BangaloreJam", "BengaluruTraffic", "BengaluruJam", "SilkBoardTraffic",
    "ORRTraffic", "WhitefieldTraffic", "ElectronicCityTraffic", "BangaloreTrafficUpdate",
    "BangaloreTrafficAlert", "BangaloreTrafficJam"
]

MAX_TWEETS = 10
TODAY_DATE = datetime.now(IST).date()
TODAY_DATE_STR = TODAY_DATE.strftime("%Y-%m-%d")

LOG_FILE = os.path.join(BASE_DIR, "..", "logs", "scraper_playwright.log")
OUT_FILE = os.path.join(BASE_DIR, "..", "scrapped_data", f"traffic_{TODAY_DATE_STR}.csv")
RAW_TWEET_FILE = os.path.join(BASE_DIR, "..", "scrapped_data", f"raw_{TODAY_DATE_STR}.txt")


# === UTILS ===
def log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)


def load_cookies(context):
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        for c in cookies:
            if "sameSite" not in c or c["sameSite"] not in ["Strict", "Lax", "None"]:
                c["sameSite"] = "Lax"

        context.add_cookies(cookies)
        log("✅ Cookies loaded")
    except FileNotFoundError:
        log("⚠️ No cookie file found, might get blocked")


def human_like_wait(min_s=1.5, max_s=4.0):
    time.sleep(random.uniform(min_s, max_s))


# === MAIN SCRAPER ===
def scrape(query):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": random.randint(1200, 1920), "height": random.randint(700, 1080)},
        )

        load_cookies(context)
        page = context.new_page()

        url = f"https://x.com/search?q={query}&src=typed_query&f=live"
        page.goto(url, timeout=60000)
        page.wait_for_selector("article", timeout=30000)
        human_like_wait(5, 8)
        log(f"🔍 Opened search: {url}")

        tweets = []
        seen_ids = set()
        os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)

        if not os.path.exists(OUT_FILE):
            with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "user", "date", "content", "query_for"])
                writer.writeheader()

        while len(tweets) < MAX_TWEETS:
            human_like_wait(2, 5)
            tweet_elements = page.locator("article").all()
            log(f"🧩 Found {len(tweet_elements)} tweet containers.")

            # if len(tweet_elements) == 0:
            #     page.screenshot(path="no_tweets.png", full_page=True)
            #     log("📸 No tweets found, saved screenshot no_tweets.png")
            #     break

            new_tweets = []

            for idx, t in enumerate(tweet_elements):
                if len(tweets) >= MAX_TWEETS:
                    break
                try:
                    t.scroll_into_view_if_needed(timeout=5000)
                    human_like_wait(1.5, 2.5)

                    # Robust content extraction
                    try:
                        content = t.locator("div[data-testid='tweetText']").inner_text(timeout=5000)
                    except:
                        content = t.inner_text(timeout=5000)

                    user = t.locator("div[dir='ltr'] span").nth(0).inner_text(timeout=2000)
                    date_str = t.locator("time").get_attribute("datetime")
                    tweet_id = str(hash(content + user + (date_str or "")))

                    tweet_dt = parser.isoparse(date_str).astimezone(IST)
                    tweet_date = tweet_dt.date()

                    # Skip old tweets
                    if tweet_date != TODAY_DATE:
                        log(f"🛑 Older tweet (from {tweet_date}) skipped for query '{query}'")
                        continue

                    # Log tweet
                    log(f"\n🧵 [{idx + 1}/{len(tweet_elements)}] @{user}")
                    log(f"🕒 {date_str}")
                    log(f"💬 {content}\n{'-'*80}")

                    if tweet_id not in seen_ids:
                        seen_ids.add(tweet_id)
                        tweet_data = {
                            "id": tweet_id,
                            "user": user,
                            "date": date_str,
                            "content": content,
                            "query_for": query
                        }
                        tweets.append(tweet_data)
                        new_tweets.append(tweet_data)

                except Exception as e:
                    log(f"⚠️ Failed to extract tweet: {e}")
                    continue

            # Write to CSV
            if new_tweets:
                with open(OUT_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "user", "date", "content", "query_for"])
                    for tweet in new_tweets:
                        writer.writerow(tweet)

                # Write to raw text
                with open(RAW_TWEET_FILE, "a", encoding="utf-8") as f:
                    for tweet in new_tweets:
                        f.write(f"@{tweet['user']} [{tweet['date']}]\n{tweet['content']}\n{'='*100}\n")

            log(f"📥 Collected {len(tweets)} tweets for query: '{query}'")

            # Scroll like human
            scroll_amount = random.randint(2000, 4000)
            page.mouse.wheel(0, scroll_amount)
            human_like_wait(2, 6)

            if random.random() < 0.1:
                log("⏸️ Taking a longer pause to mimic reading...")
                human_like_wait(8, 15)

        browser.close()
        log(f"✅ Finished scraping {len(tweets)} tweets → {os.path.abspath(OUT_FILE)}")


# === ENTRY POINT ===
if __name__ == "__main__":
    log("==== 🚦 Playwright Scraper Started ====")
    for query in QUERY_LIST:
        scrape(query)
    log("==== 🏁 Playwright Scraper Finished ====")
