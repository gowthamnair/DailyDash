import feedparser
import json
import re
import os
from datetime import datetime

# Configuration
SUBREDDITS = ["technology", "singularity", "popular", "news"]

NEWS_SOURCES = {
    "reuters": "https://www.reuters.com/arc/outboundfeeds/news-all/?outputType=xml",
    "ap": "https://news.google.com/rss/search?q=when:24h+source:Associated_Press",
    "afp": "https://news.google.com/rss/search?q=when:24h+source:AFP",
    "bbc": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "google": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
}

def extract_image(entry):
    """
    Enhanced extraction to handle both Reddit thumbnails 
    and Professional News media tags.
    """
    # 1. Check for standard News Enclosures (BBC, AP, etc.)
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href')

    # 2. Check for Media:Content (Common in News Agency feeds)
    if 'media_content' in entry:
        return entry.media_content[0]['url']

    # 3. Check for Reddit/Legacy Thumbnails in Summary
    if 'summary' in entry:
        img_match = re.search(r'src="([^"]+)"', entry.summary)
        if img_match:
            return img_match.group(1).replace('&amp;', '&')

    # 4. Reliable fallback image
    return "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80"

def fetch_and_save():
    # Process Subreddits
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top/.rss?t=day"
        process_feed(url, f"{sub}.json")

    # Process Professional News Sources
    for source_name, url in NEWS_SOURCES.items():
        process_feed(url, f"news_{source_name}.json")

def process_feed(url, filename):
    feed = feedparser.parse(url)
    articles = []
    
    # Process top 15 entries
    for entry in feed.entries[:15]:
        articles.append({
            "title": entry.get('title', 'Untitled'),
            "link": entry.get('link', '#'),
            "image": extract_image(entry),
            "published": entry.get('published', datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        })
    
    with open(filename, "w") as f:
        json.dump(articles, f, indent=4)
    print(f"Generated: {filename}")

if __name__ == "__main__":
    fetch_and_save()
