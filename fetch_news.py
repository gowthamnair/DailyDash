import feedparser
import json
import re
from datetime import datetime

SUBREDDITS = ["technology", "singularity", "popular", "news"]

def extract_image(entry):
    if 'summary' in entry:
        img_match = re.search(r'src="([^"]+)"', entry.summary)
        if img_match:
            return img_match.group(1).replace('&amp;', '&')
    return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

def fetch_and_save():
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top/.rss?t=day"
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:15]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "image": extract_image(entry),
                "published": entry.published
            })
        with open(f"{sub}.json", "w") as f:
            json.dump(articles, f, indent=4)

if __name__ == "__main__":
    fetch_and_save()
