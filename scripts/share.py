"""Shares newly approved posts to social channels. Each channel is optional:
it only runs if its secrets are set in GitHub (Settings > Secrets and variables > Actions).

  Telegram:  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  Discord:   DISCORD_WEBHOOK_URL
  Bluesky:   BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
  Mastodon:  MASTODON_INSTANCE, MASTODON_TOKEN
  Facebook:  FACEBOOK_PAGE_ID, FACEBOOK_PAGE_TOKEN
  Instagram: INSTAGRAM_ACCOUNT_ID, FACEBOOK_PAGE_TOKEN  (posts the post's graphic with a caption)
"""
import datetime as dt
import json
import pathlib
import time
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from common import ROOT, USER_AGENT, http_json, load_site, parse_front_matter

SITE = load_site()
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
    own = pathlib.Path(meta.get("image", "")).name
    if own and (ROOT / "assets" / "images" / own).is_file():
        return f"{BASE_URL}/assets/images/{own}"
    return f"{BASE_URL}/covers/{slug}.jpg"


def facebook(meta, link):
    graph_post(f"{env('FACEBOOK_PAGE_ID')}/feed", {
        "message": f"{meta['title']}\n\n{meta.get('summary', '')}\n\n{HASHTAGS.get(meta.get('category'), '#cybersecurity')}",
        "link": link, "access_token": env("FACEBOOK_PAGE_TOKEN")})


def instagram(meta, link):
    caption = (f"{meta['title']}\n\n{meta.get('summary', '')}\n\n"
               f"Read the full post on our website (link in bio).\n\n"
               f"{HASHTAGS.get(meta.get('category'), '#cybersecurity')}")[:2200]
    token, account = env("FACEBOOK_PAGE_TOKEN"), env("INSTAGRAM_ACCOUNT_ID")
    container = graph_post(f"{account}/media", {"image_url": meta["_image"], "caption": caption,
                                                "access_token": token})["id"]
    for _ in range(12):  # Instagram needs a moment to fetch the picture
        status = graph_get(container, {"fields": "status_code", "access_token": token}).get("status_code")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError("Instagram could not read the image")
        time.sleep(5)
    graph_post(f"{account}/media_publish", {"creation_id": container, "access_token": token})


CHANNELS = [
    ("Telegram", ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"), telegram),
    ("Discord", ("DISCORD_WEBHOOK_URL",), discord),
    ("Bluesky", ("BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"), bluesky),
    ("Mastodon", ("MASTODON_INSTANCE", "MASTODON_TOKEN"), mastodon),
    ("Facebook", ("FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_TOKEN"), facebook),
    ("Instagram", ("INSTAGRAM_ACCOUNT_ID", "FACEBOOK_PAGE_TOKEN"), instagram),
]


def main():
    files = (env("NEW_POSTS") or " ".join(sys.argv[1:])).split()
    files = [f for f in files if f.startswith("content/posts/") and f.endswith(".md")]
    if not files:
        print("No new posts to share.")
        return
    active = [(name, fn) for name, keys, fn in CHANNELS if all(env(k) for k in keys)]
    if not active:
        print("No social channels are set up yet; skipping sharing.")
        return
    for f in files:
        path = ROOT / f
        if not path.exists():
            continue
        meta, _ = parse_front_matter(path.read_text(encoding="utf-8"))
        link = f"{BASE_URL}/posts/{path.stem}/"
        meta["_image"] = image_url(meta, path.stem)
        for name, fn in active:
            try:
                fn(meta, link)
                print(f"Shared on {name}: {meta.get('title')}")
            except Exception as exc:  # one failing channel should not stop the others
                print(f"Could not share on {name}: {exc}")


if __name__ == "__main__":
    main()
