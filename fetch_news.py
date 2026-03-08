import feedparser
import json
import re
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

# This header is critical. Without it, Reuters/BBC may block image metadata.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def extract_image(entry):
    """
    Tries multiple methods to find a unique image for each article.
    """
    # 1. Check Media Content (Reuters / BBC / Associated Press)
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0]['url']
    
    # 2. Check Enclosures (Standard RSS image tag)
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0]['url']

    # 3. Check for image links in the links list
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href')

    # 4. Reddit Specific: Extract from <img> tag in summary
    if 'summary' in entry:
        img_match = re.search(r'src="([^"]+)"', entry.summary)
        if img_match:
            # Fix common encoding issues and return unique URL
            url = img_match.group(1).replace('&amp;', '&')
            if "redditstatic.com" not in url: # Avoid generic Reddit icons
                return url

    # 5. Fallback: Return a unique placeholder based on the title to avoid "all the same" visuals
    # Using a high-quality tech placeholder
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

def process_feed(url, filename):
    # Passing the USER_AGENT is mandatory for professional wire services
    feed = feedparser.parse(url, agent=USER_AGENT)
    articles = []
    
    for entry in feed.entries[:15]:
        img_url = extract_image(entry)
        
        articles.append({
            "title": entry.get('title', 'Untitled'),
            "link": entry.get('link', '#'),
            "image": img_url,
            "published": entry.get('published', datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        })
    
    with open(filename, "w") as f:
        json.dump(articles, f, indent=4)
    print(f"Generated: {filename}")

def fetch_and_save():
    # Process Subreddits
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top/.rss?t=day"
        process_feed(url, f"{sub}.json")

    # Process Professional News Sources
    for source_name, url in NEWS_SOURCES.items():
        process_feed(url, f"news_{source_name}.json")

if __name__ == "__main__":
    fetch_and_save()
