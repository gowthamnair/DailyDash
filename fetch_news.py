import feedparser
import json
import re
from datetime import datetime

SUBREDDITS = ["technology", "singularity", "popular", "news"]

def extract_image(entry):
    """
    Reverted to standard thumbnail extraction.
    Extracts the 'src' from the summary's <img> tag.
    """
    if 'summary' in entry:
        # Standard search for the <img> tag's src attribute
        img_match = re.search(r'src="([^"]+)"', entry.summary)
        
        if img_match:
            # We fix the HTML encoding (&amp; to &) but keep the parameters
            return img_match.group(1).replace('&amp;', '&')

    # Reliable fallback image
    return "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=400&q=80"


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
