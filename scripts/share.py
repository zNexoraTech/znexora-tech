"""Shares newly approved posts to social channels. Each channel is optional:
it only runs if its secrets are set in GitHub (Settings > Secrets and variables > Actions).

  Telegram:  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  Discord:   DISCORD_WEBHOOK_URL
  Bluesky:   BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
  Mastodon:  MASTODON_INSTANCE, MASTODON_TOKEN
  Facebook:  FACEBOOK_PAGE_ID, FACEBOOK_PAGE_TOKEN
  Instagram: INSTAGRAM_ACCOUNT_ID, FACEBOOK_PAGE_TOKEN  (posts the post's graphic with a caption)
  Blogger:   BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN (full article, linked back)
  LinkedIn:  LINKEDIN_TOKEN (+ LINKEDIN_AUTHOR = urn:li:organization:<id> to post as a company page)
Share kit:   for WhatsApp Channels and TikTok, which have no public posting API, a ready-to-copy
             message and the slide pictures are sent to you as a GitHub notification (issue).
"""
import datetime as dt
import html
import json
import pathlib
import re
import time
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from common import ROOT, USER_AGENT, http_json, load_site, parse_front_matter

SITE = load_site()
CATEGORY_NAMES = dict(SITE.get("categories", {}))
CATEGORY_NAMES.setdefault("cheatsheets", "Cheat sheets")
CATEGORY_NAMES.setdefault("courses", "Courses")
BASE_URL = ("https://" + SITE["custom_domain"].strip().strip("/")) if SITE.get("custom_domain") else SITE["url"].rstrip("/")
env = os.environ.get


def message(meta, link, limit=None):
    text = f"{meta['title']}\n\n{meta.get('summary', '')}"
    if limit and len(text) + len(link) + 2 > limit:
        text = text[: limit - len(link) - 3].rstrip() + "…"
    return f"{text}\n\n{link}"


def telegram(meta, link):
    http_json(f"https://api.telegram.org/bot{env('TELEGRAM_BOT_TOKEN')}/sendMessage",
              data={"chat_id": env("TELEGRAM_CHAT_ID"), "text": message(meta, link)}, method="POST")


def discord(meta, link):
    http_json(env("DISCORD_WEBHOOK_URL"), data={"content": message(meta, link, 1900)}, method="POST")


def bluesky(meta, link):
    session = http_json("https://bsky.social/xrpc/com.atproto.server.createSession",
                        data={"identifier": env("BLUESKY_HANDLE"), "password": env("BLUESKY_APP_PASSWORD")}, method="POST")
    text = message(meta, link, 290)
    start = len(text.encode("utf-8")) - len(link.encode("utf-8"))
    record = {
        "$type": "app.bsky.feed.post", "text": text,
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "facets": [{"index": {"byteStart": start, "byteEnd": start + len(link.encode("utf-8"))},
                    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": link}]}],
    }
    http_json("https://bsky.social/xrpc/com.atproto.repo.createRecord",
              headers={"Authorization": f"Bearer {session['accessJwt']}"},
              data={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record}, method="POST")


def mastodon(meta, link):
    instance = env("MASTODON_INSTANCE").rstrip("/")
    if not instance.startswith("http"):
        instance = "https://" + instance
    req = urllib.request.Request(f"{instance}/api/v1/statuses",
                                 data=urllib.parse.urlencode({"status": message(meta, link, 480)}).encode(),
                                 headers={"Authorization": f"Bearer {env('MASTODON_TOKEN')}", "User-Agent": USER_AGENT})
    urllib.request.urlopen(req, timeout=60).read()


GRAPH = "https://graph.facebook.com/v25.0"   # Meta API version, supported until 2028
HASHTAGS = {
    "news": "#cybersecurity #infosec #securitynews",
    "weekly-recap": "#cybersecurity #ransomware #weeklyrecap #infosec",
    "exploited-vulnerabilities": "#cybersecurity #vulnerability #patchnow #infosec",
    "theory": "#cybersecurity #learning #infosec",
    "practical": "#cybersecurity #howto #sysadmin #infosec",
    "cheatsheets": "#cheatsheet #cybersecurity #infosec #sysadmin #learning",
    "courses": "#cybersecurity #course #learning #infosec #careers",
}


def graph_post(path, fields):
    req = urllib.request.Request(f"{GRAPH}/{path}", data=urllib.parse.urlencode(fields).encode(),
                                 headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:  # show Meta's explanation, not just the code
        raise RuntimeError(exc.read().decode(errors="replace")[:400]) from None


def graph_get(path, fields):
    with urllib.request.urlopen(f"{GRAPH}/{path}?{urllib.parse.urlencode(fields)}", timeout=60) as resp:
        return json.loads(resp.read())


def image_url(meta, slug):
    """The small JPEG preview made by the website build (works for Instagram, WhatsApp and LinkedIn)."""
    own = pathlib.Path(meta.get("image", "")).name
    if not own:
        own = next((f"{slug}{x}" for x in (".jpg", ".jpeg", ".png", ".webp") if (ROOT / "assets" / "images" / f"{slug}{x}").is_file()), "")
    if own and (ROOT / "assets" / "images" / own).is_file():
        return f"{BASE_URL}/share/assets-images-{own.rsplit('.', 1)[0]}.jpg"
    return f"{BASE_URL}/share/covers-{slug}.jpg"


def facebook(meta, link):
    if meta.get("category") == "cheatsheets":  # a full photo post shows the whole cheat sheet in the feed
        graph_post(f"{env('FACEBOOK_PAGE_ID')}/photos", {
            "url": f"{BASE_URL}/share/full-{meta['_slug']}.jpg",
            "caption": f"{meta['title']}\n\n{meta.get('summary', '')}\n\nDownload it free: {link}\n\n{HASHTAGS['cheatsheets']}",
            "access_token": env("FACEBOOK_PAGE_TOKEN")})
        return
    graph_post(f"{env('FACEBOOK_PAGE_ID')}/feed", {
        "message": f"{meta['title']}\n\n{meta.get('summary', '')}\n\n{HASHTAGS.get(meta.get('category'), '#cybersecurity')}",
        "link": link, "access_token": env("FACEBOOK_PAGE_TOKEN")})


def instagram(meta, link):
    caption = (f"{meta['title']}\n\n{meta.get('summary', '')}\n\n"
               f"Read the full post on our website (link in bio).\n\n"
               f"{HASHTAGS.get(meta.get('category'), '#cybersecurity')}")[:2200]
    token, account = env("FACEBOOK_PAGE_TOKEN"), env("INSTAGRAM_ACCOUNT_ID")
    image = f"{BASE_URL}/share/ig-{meta['_slug']}.jpg" if meta.get("category") == "cheatsheets" else meta["_image"]
    container = graph_post(f"{account}/media", {"image_url": image, "caption": caption,
                                                "access_token": token})["id"]
    for _ in range(12):  # Instagram needs a moment to fetch the picture
        status = graph_get(container, {"fields": "status_code", "access_token": token}).get("status_code")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError("Instagram could not read the image")
        time.sleep(5)
    graph_post(f"{account}/media_publish", {"creation_id": container, "access_token": token})


# ---------------- Blogger (Google Blogger API v3)
def google_token():
    data = urllib.parse.urlencode({"client_id": env("BLOGGER_CLIENT_ID"), "client_secret": env("BLOGGER_CLIENT_SECRET"),
                                   "refresh_token": env("BLOGGER_REFRESH_TOKEN"), "grant_type": "refresh_token"}).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())["access_token"]


def article_html(meta, link):
    """The article as HTML for Blogger, with pictures pointing to the website."""
    import markdown
    body = meta.get("_body", "")
    body = body.replace("../../assets/", f"{BASE_URL}/assets/")
    html_body = markdown.markdown(body.replace("<", "&lt;"), extensions=["tables", "sane_lists"])
    cover = f'<p><a href="{link}"><img src="{meta["_image"]}" alt="" style="max-width:100%"></a></p>'
    if (SITE.get("blogger") or {}).get("mode", "full") == "summary":
        return (cover + f"<p>{html.escape(meta.get('summary', ''))}</p>"
                f'<p><a href="{link}"><strong>Read the full article on ZNexora Tech →</strong></a></p>')
    note = (f'<p><em>Originally published on <a href="{link}">ZNexora Tech</a>. '
            f'Follow us for weekly cybersecurity news, recaps and guides.</em></p>')
    return cover + html_body + note


def blogger(meta, link):
    cats = (SITE.get("blogger") or {}).get("categories", ["theory", "practical", "courses", "weekly-recap", "cheatsheets"])
    if meta.get("category") not in cats:
        raise SkipChannel("this section is not sent to the blog (see blogger.categories in site.json)")
    token = google_token()
    headers = {"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT}
    blog_url = (SITE.get("social") or {}).get("Blog", "")
    blog_id = env("BLOGGER_BLOG_ID") or http_json(
        "https://www.googleapis.com/blogger/v3/blogs/byurl?url=" + urllib.parse.quote(blog_url, safe=""), headers=headers)["id"]
    labels = [CATEGORY_NAMES.get(meta.get("category"), "ZNexora Tech")] + [t.strip() for t in meta.get("tags", "").split(",") if t.strip()][:4]
    http_json(f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/", headers=headers, method="POST",
              data={"kind": "blogger#post", "title": meta["title"], "content": article_html(meta, link), "labels": labels})


# ---------------- LinkedIn (Posts API)
def linkedin_author():
    """Your LinkedIn identity. Set LINKEDIN_AUTHOR for a company page; otherwise your own profile is used."""
    if env("LINKEDIN_AUTHOR"):
        return env("LINKEDIN_AUTHOR")
    info = http_json("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {env('LINKEDIN_TOKEN')}"})
    return f"urn:li:person:{info['sub']}"


def linkedin(meta, link):
    version = str((SITE.get("linkedin") or {}).get("api_version", "202609"))
    payload = {"author": linkedin_author(), "commentary": message(meta, link, 2900).replace("(", "[").replace(")", "]"),
               "visibility": "PUBLIC", "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False,
               "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
               "content": {"article": {"source": link, "title": meta["title"][:200], "description": meta.get("summary", "")[:250]}}}
    req = urllib.request.Request("https://api.linkedin.com/rest/posts", data=json.dumps(payload).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {env('LINKEDIN_TOKEN')}", "Linkedin-Version": version,
                                          "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json",
                                          "User-Agent": USER_AGENT})
    try:
        urllib.request.urlopen(req, timeout=60).read()
    except urllib.error.HTTPError as exc:
        hint = {401: "token expired (LinkedIn tokens last 60 days; create a new one)",
                426: "API version retired; update linkedin.api_version in site.json"}.get(exc.code, "")
        raise RuntimeError(f"{exc.code} {hint} {exc.read().decode(errors='replace')[:200]}") from None


# ---------------- Share kit for WhatsApp Channels and TikTok (no public posting API)
def share_kit(meta, link):
    cats = (SITE.get("share_kit") or {}).get("categories", ["theory", "practical", "courses", "weekly-recap", "cheatsheets"])
    if meta.get("category") not in cats:
        raise SkipChannel("no share kit for this section")
    repo = env("GITHUB_REPOSITORY")
    slides = re.findall(r"\(\.\./\.\./(assets/images/[^)]+/slides/slide-\d+\.jpg)\)", meta.get("_body", ""))
    tags = HASHTAGS.get(meta.get("category"), "#cybersecurity")
    whatsapp = f"{link}\n\n*{meta['title']}*\n\n{meta.get('summary', '')}"
    tiktok = f"{meta['title']} 🔐\n{meta.get('summary', '')[:150]}\nFull article: link in bio\n{tags} #fyp #techtok"
    if meta.get("category") == "cheatsheets":
        pics = f"1. {BASE_URL}/share/full-{meta['_slug']}.jpg (full cheat sheet)\n2. {BASE_URL}/share/ig-{meta['_slug']}.jpg (square-ish version)"
    else:
        pics = "\n".join(f"{i}. {BASE_URL}/{s}" for i, s in enumerate(slides, 1)) or f"1. {meta['_image']}"
    body = f"""Your article is live: {link}

## 💬 WhatsApp Channel
Open your channel in WhatsApp and paste this message. **Wait 2-3 seconds until the link card with the picture appears**, then send:
```
{whatsapp}
```

## 🎵 TikTok (photo post)
1. Open each picture below on your phone and save it.
2. In TikTok tap **+**, choose **Photo**, select the pictures in order, and paste this caption:
```
{tiktok}
```
Pictures:
{pics}

Close this issue when you are done."""
    http_json(f"https://api.github.com/repos/{repo}/issues", method="POST",
              headers={"Authorization": f"Bearer {env('GH_TOKEN')}", "Accept": "application/vnd.github+json"},
              data={"title": f"Share kit: {meta['title']}"[:250], "body": body})


class SkipChannel(Exception):
    pass


CHANNELS = [
    ("Telegram", ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"), telegram),
    ("Discord", ("DISCORD_WEBHOOK_URL",), discord),
    ("Bluesky", ("BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"), bluesky),
    ("Mastodon", ("MASTODON_INSTANCE", "MASTODON_TOKEN"), mastodon),
    ("Facebook", ("FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_TOKEN"), facebook),
    ("Instagram", ("INSTAGRAM_ACCOUNT_ID", "FACEBOOK_PAGE_TOKEN"), instagram),
    ("Blogger", ("BLOGGER_CLIENT_ID", "BLOGGER_CLIENT_SECRET", "BLOGGER_REFRESH_TOKEN"), blogger),
    ("LinkedIn", ("LINKEDIN_TOKEN",), linkedin),
    ("Share kit (WhatsApp & TikTok)", ("GH_TOKEN", "GITHUB_REPOSITORY"), share_kit),
]


def main():
    files = (env("NEW_POSTS") or " ".join(sys.argv[1:])).split()
    files = [f for f in files if f.startswith("content/posts/") and f.endswith(".md")]
    if not files:
        print("No new posts to share.")
        return
    active = [(name, fn) for name, keys, fn in CHANNELS if all(env(k) for k in keys)]
    only = [c.strip().lower() for c in (env("ONLY_CHANNELS") or "").split(",") if c.strip() and c.strip().lower() != "all"]
    if only:  # "Share an article again" can pick channels, e.g. "Blogger"
        active = [(n, f) for n, f in active if any(n.lower().startswith(o) for o in only)]
        print("Sharing only to:", ", ".join(n for n, _ in active) or "(none connected with that name)")
    if not active:
        print("No social channels are set up yet; skipping sharing.")
        return
    for f in files:
        path = ROOT / f
        if not path.exists():
            continue
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        meta["_body"] = body
        meta["_slug"] = path.stem
        link = f"{BASE_URL}/posts/{path.stem}/"
        meta["_image"] = image_url(meta, path.stem)
        for name, fn in active:
            try:
                fn(meta, link)
                print(f"Shared on {name}: {meta.get('title')}")
            except SkipChannel as why:
                print(f"Skipped {name}: {why}")
            except Exception as exc:  # one failing channel should not stop the others
                print(f"Could not share on {name}: {exc}")


if __name__ == "__main__":
    main()
