import feedparser
import json
import re
from datetime import datetime

SUBREDDITS = ["technology", "singularity", "popular", "news"]

def extract_image(entry):
    """
    Extracts the highest resolution image available from Reddit RSS.
    Bypasses the 140x140 thumbnails.
    """
    if 'summary' in entry:
        # 1. Look for the 'preview' image link which is usually full size
        # We look for the 'https://preview.redd.it/...' pattern
        img_match = re.search(r'href="(https://preview\.redd\.it/[^"]+)"', entry.summary)
        
        if not img_match:
            # 2. Fallback: Search for any standard image tag
            img_match = re.search(r'src="([^"]+)"', entry.summary)
            
        if img_match:
            img_url = img_match.group(1).replace('&amp;', '&')
            
            # 3. Clean 'Small' Parameters
            # If the URL contains width/height/crop parameters, we strip them
            # to force Reddit to serve the original source image.
            clean_url = img_url.split('?')[0] 
            
            # Validation: Ensure it's a common image format
            if any(ext in clean_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return clean_url
                
    # Professional Technology Placeholder if no image is found
    return "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"


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
