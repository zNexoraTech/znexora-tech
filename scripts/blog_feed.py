"""Reads the latest posts from your Blogger blog so the website can show them.

Blogger publishes a public feed of every blog at <blog>/feeds/posts/default?alt=rss.
We read the title, date, labels, first image and a short excerpt, and always link back
to the full post on your blog. If the blog can't be reached, the site still builds.
"""
import html
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from common import http_get

MEDIA = "{http://search.yahoo.com/mrss/}"
IMG_HOSTS = ("https://blogger.googleusercontent.com/", "https://1.bp.blogspot.com/", "https://2.bp.blogspot.com/",
             "https://3.bp.blogspot.com/", "https://4.bp.blogspot.com/", "https://lh3.googleusercontent.com/")


def feed_url(site):
    blog = (site.get("blog") or {}).get("url") or (site.get("social") or {}).get("Blog", "")
    blog = str(blog).strip().rstrip("/")
    if not blog.startswith("https://"):
        return ""
    return f"{blog}/feeds/posts/default?alt=rss&max-results=12"


def bigger(img):
    """Blogger image links carry their size (s72-c, w679-h382 ...). Ask for a sharp 800px version."""
    return re.sub(r"/(?:s|w|h)\d+(?:-[a-z0-9]+)*/(?=[^/]+$)", "/w1000/", img, count=1)


def text_of(desc):
    plain = re.sub(r"<[^>]+>", " ", desc or "")
    plain = re.sub(r"\s+", " ", html.unescape(plain)).strip()
    return plain[:220].rsplit(" ", 1)[0] + "…" if len(plain) > 220 else plain


def read_blog(site, timeout=25):
    url = feed_url(site)
    if not url:
        return []
    try:
        root = ET.fromstring(http_get(url, timeout=timeout))
    except Exception as exc:
        print(f"Blog feed not available ({exc}); building without blog posts.")
        return []
    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link.startswith("https://"):
            continue
        desc = item.findtext("description") or ""
        img = ""
        thumb = item.find(MEDIA + "thumbnail")
        if thumb is not None and thumb.get("url"):
            img = thumb.get("url")
        else:
            m = re.search(r'<img[^>]+src="([^"]+)"', desc)
            img = m.group(1) if m else ""
        img = bigger(img) if img.startswith(IMG_HOSTS) else ""
        try:
            date = parsedate_to_datetime(item.findtext("pubDate")).date().isoformat()
        except Exception:
            date = ""
        posts.append({"title": title, "link": link, "image": img, "date": date,
                      "excerpt": text_of(desc), "labels": [c.text for c in item.findall("category") if c.text][:2]})
    print(f"Blog: {len(posts)} post(s) from {url.split('/feeds')[0]}")
    return posts
