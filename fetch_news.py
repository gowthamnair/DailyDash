import feedparser
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Configuration
SUBREDDITS = ["technology", "singularity", "popular", "news"]
NEWS_SOURCES = {
    "cnn": "http://rss.cnn.com/rss/edition_world.rss",
    "bbc": "https://feeds.bbci.co.uk/news/world/rss.xml"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def scrape_bbc_image(url):
    """
    Specifically visits the BBC article to find the high-res Open Graph image.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.find("meta", property="og:image")
            if img_tag:
                return img_tag["content"]
    except Exception as e:
        print(f"Scrape failed for {url}: {e}")
    return None

def extract_image(entry, source_name):
    """
    Decides whether to scrape or use RSS metadata based on the source.
    """
    # Force BeautifulSoup for BBC
    if source_name == "bbc":
        scraped_url = scrape_bbc_image(entry.link)
        if scraped_url:
            return scraped_url

    # Default RSS Metadata Extraction (Used for CNN and Fallback)
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0]['url']
    if 'summary' in entry:
        img_match = re.search(r'src="([^"]+)"', entry.summary)
        if img_match:
            return img_match.group(1).replace('&amp;', '&')

    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

def process_feed(url, filename, source_name=None):
    feed = feedparser.parse(url, agent="Mozilla/5.0")
    articles = []
    
    # Process top 10 for scraping efficiency
    for entry in feed.entries[:10]:
        articles.append({
            "title": entry.get('title', 'Untitled'),
            "link": entry.get('link', '#'),
            "image": extract_image(entry, source_name),
            "published": entry.get('published', datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        })
    
    with open(filename, "w") as f:
        json.dump(articles, f, indent=4)
    print(f"Generated: {filename}")

def fetch_and_save():
    # Process Subreddits (Standard)
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top/.rss?t=day"
        process_feed(url, f"{sub}.json")

    # Process News (Hybrid)
    for name, url in NEWS_SOURCES.items():
        process_feed(url, f"news_{name}.json", source_name=name)

if __name__ == "__main__":
    fetch_and_save()
