import feedparser
import json
import requests
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

# Configuration
SUBREDDITS = ["technology", "singularity", "popular", "news"]
NEWS_SOURCES = {
    "bbc": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "cnn": "http://rss.cnn.com/rss/edition_world.rss"
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def get_bbc_image(url):
    """Visits BBC article to find high-res og:image."""
    try:
        res = requests.get(url, headers={"User-Agent": UA}, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            img = soup.find("meta", property="og:image")
            return img["content"] if img else None
    except:
        return None

def extract_reddit_image(summary_html):
    """
    Specifically parses the Reddit <summary> HTML to find the unique <img> src.
    """
    if not summary_html:
        return None
    # Look for the src attribute in the <img> tag
    match = re.search(r'src="([^"]+)"', summary_html)
    if match:
        url = match.group(1).replace('&amp;', '&')
        # Ensure we don't return the tiny generic Reddit icon
        if "redditstatic.com" not in url:
            return url
    return None

def fetch_reddit_rss(url):
    session = requests.Session()
    try:
        session.get("https://www.reddit.com", headers={"User-Agent": UA}, timeout=10)
        response = session.get(url, headers={"User-Agent": UA}, timeout=10)
        if response.status_code == 200:
            return feedparser.parse(response.text)
    except:
        pass
    return None

def process_and_save(feed_data, filename, source_type):
    if not feed_data or not feed_data.entries:
        return

    articles = []
    for entry in feed_data.entries[:15]:
        img = None
        
        if source_type == "bbc":
            img = get_bbc_image(entry.get('link'))
        elif source_type == "reddit":
            # Extract the UNIQUE image for this specific Reddit post
            img = extract_reddit_image(entry.get('summary'))
        
        # Fallback for Google News or missing images
        if not img:
            if 'media_content' in entry:
                img = entry.media_content[0]['url']
            elif 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''):
                        img = link.get('href')

        articles.append({
            "title": entry.get('title', 'Untitled'),
            "link": entry.get('link', '#'),
            "image": img or "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800",
            "published": entry.get('published', datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        })

    with open(filename, "w") as f:
        json.dump(articles, f, indent=4)
    print(f"Generated: {filename} with {len(articles)} articles.")

def fetch_and_save():
    # Process Reddit
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.rss?t=day"
        feed = fetch_reddit_rss(url)
        process_and_save(feed, f"{sub}.json", "reddit")
        time.sleep(1)

    # Process News
    for name, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url, agent=UA)
        process_and_save(feed, f"news_{name}.json", name)

if __name__ == "__main__":
    fetch_and_save()
