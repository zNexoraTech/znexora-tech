"""Collects the latest security news and drafts posts for approval.

With an AI key: each top story becomes a short news brief written in our own words,
linking to the original report.
Without an AI key: one "news roundup" post lists the latest headlines with links.

Every run also records headlines and ransomware statistics for the weekly recap.
"""
import argparse
import datetime as dt
import hashlib
import os

from common import (PR_FOOTER, automation, commit_state, dump_front_matter, http_get, http_json,
                    load_json, nice_date, parse_feed, save_draft, save_json, slugify, tag_story, today)
from writer import ai_json

RANSOMWARE_API = "https://api.ransomware.live/v2/recentvictims"
PRIORITY = {"vulnerability": 3, "ransomware": 3, "defacement": 3, "breach": 2}


def key(link):
    return hashlib.sha1(link.encode()).hexdigest()[:16]


def collect_news(cfg):
    stories = []
    for feed in cfg.get("feeds", []):
        try:
            items = parse_feed(http_get(feed["url"], timeout=40), feed["name"])
            print(f"  {feed['name']}: {len(items)} stories")
            stories += items
        except Exception as exc:
            print(f"  {feed['name']}: could not read feed ({exc})")
    return stories


def log_ransomware():
    """Keep anonymous statistics only (group, sector, country, date). No victim names are stored."""
    log = load_json("ransomware_log.json", {})
    try:
        for v in http_json(RANSOMWARE_API, timeout=60):
            vid = key((v.get("url") or "") + (v.get("victim") or ""))
            if vid not in log:
                log[vid] = {"group": v.get("group") or "unknown", "sector": v.get("activity") or "Not listed",
                            "country": v.get("country") or "??", "date": (v.get("discovered") or "")[:10]}
        print(f"  ransomware.live: {len(log)} claims in memory")
    except Exception as exc:
        print(f"  ransomware.live: could not read ({exc})")
    cutoff = (today() - dt.timedelta(days=21)).isoformat()
    save_json("ransomware_log.json", {k: v for k, v in log.items() if v["date"] >= cutoff})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    site, cfg, model = automation("news")
    if not cfg.get("enabled", True):
        return print("News drafts are turned off in site.json.")

    print("Reading news feeds...")
    stories = collect_news(cfg)
    log_ransomware()

    news_log = load_json("news_log.json", {})
    for s in stories:
        k = key(s["link"])
        if k not in news_log:
            when = s["date"] or dt.datetime.now(dt.timezone.utc)
            news_log[k] = {"title": s["title"], "link": s["link"], "source": s["source"],
                           "summary": s["summary"][:400], "date": when.astimezone(dt.timezone.utc).isoformat(),
                           "tags": tag_story(s["title"] + " " + s["summary"]), "drafted": False}
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=21)).isoformat()
    news_log = {k: v for k, v in news_log.items() if v["date"] >= cutoff}

    recent_cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=int(cfg.get("lookback_hours", 24)))).isoformat()
    fresh = [(k, v) for k, v in news_log.items() if not v["drafted"] and v["date"] >= recent_cut]
    fresh.sort(key=lambda kv: (sum(PRIORITY.get(t, 0) for t in kv[1]["tags"]), kv[1]["date"]), reverse=True)
    limit = int(cfg.get("max_drafts_per_run", 3))
    print(f"News: {len(fresh)} fresh stories, drafting up to {limit}.")

    drafted = 0
    if fresh and os.environ.get("ANTHROPIC_API_KEY"):
        for k, s in fresh[:limit]:
            ai = ai_json(
                "Write a short news brief (120-220 words) about this report, in your own words. "
                "Use only what the material says. Return "
                '{"title": "neutral factual headline, under 90 characters", "summary": "one sentence", '
                '"body": "markdown: two or three short paragraphs, then a section ## Why it matters with 2-3 sentences"}',
                f"Headline: {s['title']}\nPublished by: {s['source']}\nDate: {s['date'][:10]}\nReport extract: {s['summary']}",
                model, 1200)
            if not ai:
                continue
            title = ai["title"].strip()
            meta = {"title": title, "date": today().isoformat(), "category": "news", "summary": ai["summary"],
                    "source": s["source"], "source_url": s["link"], "tags": ", ".join(s["tags"]), "drafted_by": "ai"}
            body = ai["body"].strip() + f"\n\n## Source\n\nOriginal report: [{s['title']}]({s['link']}) ({s['source']})"
            pr = (f"News brief based on **{s['source']}**: {s['link']}\n\n- [ ] Facts match the original report\n"
                  f"- [ ] Nothing is copied word for word\n{PR_FOOTER}")
            if save_draft(slugify(title) + "-" + today().strftime("%Y%m%d"), title,
                          dump_front_matter(meta, body), pr, args.dry_run):
                news_log[k]["drafted"] = True
                drafted += 1
    if fresh and not drafted:
        picks = fresh[:10]
        title = f"Security news roundup: {nice_date(today())}"
        lines = [f"- [{s['title']}]({s['link']}) ({s['source']})" for _, s in picks]
        body = ("The stories security teams are following today. Each link goes to the original report.\n\n"
                "## Headlines\n\n" + "\n".join(lines))
        meta = {"title": title, "date": today().isoformat(), "category": "news",
                "summary": f"{len(picks)} security stories worth knowing about today, with links to the original reports.",
                "drafted_by": "template"}
        pr = f"Today's headline roundup ({len(picks)} stories). Delete any line you don't want before merging.\n{PR_FOOTER}"
        slug = "security-news-roundup-" + today().isoformat() + "-" + dt.datetime.now(dt.timezone.utc).strftime("%H")
        if save_draft(slug, title, dump_front_matter(meta, body), pr, args.dry_run):
            for k, _ in picks:
                news_log[k]["drafted"] = True

    save_json("news_log.json", news_log)
    commit_state("Robot memory: news and ransomware statistics", args.dry_run)


if __name__ == "__main__":
    main()
