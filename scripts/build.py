"""Builds the whole website into the _site folder. Run: python scripts/build.py

Layout: a professional news-magazine design (lead story, latest headlines, sections with
thumbnails, sidebar) and long-form article pages (byline, tags, key points, contents, share).
"""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import shutil
import urllib.parse

import markdown

from blog_feed import read_blog
from common import PAGES_DIR, POSTS_DIR, ROOT, load_site, parse_front_matter
from covers import make_cover

OUT = ROOT / "_site"
SITE = load_site()
BASE_URL = SITE["url"].rstrip("/")
if SITE.get("custom_domain"):
    BASE_URL = "https://" + SITE["custom_domain"].strip().strip("/")
BP = urllib.parse.urlparse(BASE_URL).path.rstrip("/")
CATS = SITE.get("categories", {})
SEV_LABEL = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low", "unscored": "Not scored"}
TONE = {"news": "t-news", "weekly-recap": "t-recap", "exploited-vulnerabilities": "t-exploit",
        "theory": "t-theory", "practical": "t-practical", "blog": "t-blog"}
CAT_INTRO = {
    "news": "The security stories that matter, explained in plain language.",
    "weekly-recap": "Every Monday: the week’s top news, ransomware activity and web defacement in one read.",
    "exploited-vulnerabilities": "Vulnerabilities attackers are using right now, with what to patch first.",
    "theory": "Security concepts made clear, from fundamentals to advanced topics.",
    "practical": "Hands-on, step-by-step guides for defending real systems.",
}
BLOG = []
e = html.escape


def url(path):
    return f"{BP}{path}"


# ---------------------------------------------------------------- content
def render_md(text):
    """Markdown to HTML with raw HTML switched off, so posts can never inject scripts.
    Returns (html, [(id, heading)]) for the article's table of contents."""
    md = markdown.Markdown(extensions=["tables", "pymdownx.superfences", "sane_lists", "toc"])
    md.preprocessors.deregister("html_block")
    md.inlinePatterns.deregister("html")
    out = md.convert(text)
    out = re.sub(r'href="\s*(javascript|data|vbscript):[^"]*"', 'href="#"', out, flags=re.I)
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    toc = [(t["id"], t["name"]) for t in getattr(md, "toc_tokens", []) if t.get("level") == 2]
    return out, toc


def load_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if not meta.get("title") or meta.get("draft", "").lower() == "true":
            continue
        meta["slug"], meta["path"] = path.stem, f"/posts/{path.stem}/"
        meta["html"], meta["toc"] = render_md(body)
        meta["minutes"] = max(1, round(len(body.split()) / 220))
        meta.setdefault("category", "news")
        meta.setdefault("severity", "")
        meta.setdefault("summary", "")
        meta["date"] = meta.get("date") or dt.date.today().isoformat()
        own = pathlib.Path(meta.get("image", "")).name
        if not own:  # easy way: a photo named exactly like the article, e.g. assets/images/<article-name>.jpg
            own = next((f"{path.stem}{ext}" for ext in (".jpg", ".jpeg", ".png", ".webp")
                        if (ROOT / "assets" / "images" / f"{path.stem}{ext}").is_file()), "")
        if own and (ROOT / "assets" / "images" / own).is_file():
            meta["cover"], meta["cover_alt"], meta["own_image"] = f"/assets/images/{own}", meta.get("image_alt", ""), True
        else:
            meta["cover"], meta["cover_alt"], meta["own_image"] = f"/covers/{path.stem}.jpg", "", False
        meta["tag_list"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def nice_date(iso, long=False):
    try:
        d = dt.date.fromisoformat(iso[:10])
    except ValueError:
        return iso
    return d.strftime("%A, %-d %B %Y") if long else d.strftime("%-d %b %Y")


# ---------------------------------------------------------------- icons & channels
ICON = {
    "news": '<path d="M4 5h13v14H6a2 2 0 0 1-2-2V5Z"/><path d="M17 9h3v8a2 2 0 0 1-2 2"/><path d="M7 9h7M7 12h7M7 15h4"/>',
    "weekly-recap": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M8 14h2M12 14h2M16 14h.5M8 17h2M12 17h2"/>',
    "exploited-vulnerabilities": '<path d="M12 3 4.5 6v6c0 4.5 3.2 7.8 7.5 9 4.3-1.2 7.5-4.5 7.5-9V6L12 3Z"/><path d="M12 8v5M12 16h.01"/>',
    "theory": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/>',
    "practical": '<path d="M14.5 6.5a4 4 0 0 0-5.3 5.3l-5 5a1.7 1.7 0 0 0 2.4 2.4l5-5a4 4 0 0 0 5.3-5.3l-2.5 2.5-2.4-.4-.4-2.4 2.9-2.1Z"/>',
    "share": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.5M8.2 13.2l7.6 4.5"/>',
    "send": '<path d="M21 3 3 10.5l7 2.5 2.5 7L21 3Z"/><path d="m10 13 4.5-4.5"/>',
    "bell": '<path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15L6 16Z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    "people": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 14.2A4.5 4.5 0 0 1 21 18.5"/>',
    "camera": '<rect x="3" y="6.5" width="18" height="13" rx="3"/><path d="M8.5 6.5 10 4h4l1.5 2.5"/><circle cx="12" cy="13" r="3.5"/>',
    "music": '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
    "play": '<rect x="2.5" y="5" width="19" height="14" rx="4"/><path d="m10 9 5 3-5 3V9Z"/>',
    "chat": '<path d="M4 19.5 5.3 16A8 8 0 1 1 8.6 19L4 19.5Z"/><path d="M9 10.5h6M9 13.5h4"/>',
    "pen": '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M3 12.5h18"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "thumb": '<path d="M7 11v9H4v-9h3Z"/><path d="M7 11l4-7a2 2 0 0 1 2 2.3L12.5 10H18a2 2 0 0 1 2 2.3l-1.2 6A2 2 0 0 1 16.8 20H7"/>',
}


def icon(name, size=24):
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


CHANNEL = {"facebook": ("people", "t-news"), "instagram": ("camera", "t-theory"), "tiktok": ("music", "t-exploit"),
           "youtube": ("play", "t-exploit"), "whatsapp": ("chat", "t-practical"), "telegram": ("send", "t-news"),
           "blog": ("pen", "t-recap"), "linkedin": ("briefcase", "t-news")}


def social_channels():
    out = []
    for label, link in (SITE.get("social") or {}).items():
        link = str(link).strip()
        if link.startswith("https://"):
            ico, tone = CHANNEL.get(label.lower(), ("link", "t-recap"))
            out.append((label, link, ico, tone))
    return out


def social_pills(cls="follow"):
    items = "".join(f'<li><a class="chan {tone}" href="{e(link)}" rel="noopener" target="_blank">'
                    f'<span class="chan-ico">{icon(ico, 18)}</span>{e(label)}</a></li>'
                    for label, link, ico, tone in social_channels())
    return f'<ul class="{cls}">{items}</ul>' if items else ""


def blog_home():
    return str((SITE.get("blog") or {}).get("url") or (SITE.get("social") or {}).get("Blog", "")).strip()


# ---------------------------------------------------------------- page frame
def layout(title, body, description="", path="/", og_type="website", image="/assets/og-image.jpg"):
    full_title = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    desc = description or SITE["description"]
    canonical = BASE_URL + path
    image_abs = image if image.startswith("https://") else BASE_URL + image

    def nav_link(href, label):
        here = ' aria-current="page"' if path == href else ""
        return f'<li><a href="{url(href)}"{here}>{e(label)}</a></li>'
    nav = (nav_link("/", "Home") + "".join(nav_link(f"/category/{s}/", n) for s, n in CATS.items())
           + (nav_link("/blog/", "Blog") if blog_home().startswith("https://") else "") + nav_link("/about/", "About"))
    top_social = "".join(f'<li><a href="{e(link)}" rel="noopener" target="_blank" aria-label="{e(label)}">{icon(ico, 15)}</a></li>'
                         for label, link, ico, tone in social_channels())
    subscribe_href = SITE.get("newsletter_url") or url("/feed.xml")
    foot_social = "".join(f'<li><a class="foot-chan" href="{e(link)}" rel="noopener" target="_blank">{icon(ico, 16)}{e(label)}</a></li>'
                          for label, link, ico, tone in social_channels())
    today = dt.date.today()
    return f"""<!doctype html>
<html lang="{e(SITE.get('language', 'en'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data: https://blogger.googleusercontent.com https://*.bp.blogspot.com https://lh3.googleusercontent.com; connect-src 'self'; manifest-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:image" content="{e(image_abs)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{e(image_abs)}">
<meta name="theme-color" content="#0b1a3a">
<link rel="alternate" type="application/rss+xml" title="{e(SITE['name'])}" href="{url('/feed.xml')}">
<link rel="icon" href="{url('/assets/favicon-32.png')}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{url('/assets/apple-touch-icon.png')}">
<link rel="preload" href="{url('/assets/fonts/archivo-var.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{url('/assets/style.css')}">
<script src="{url('/assets/app.js')}"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap topbar-row">
  <span class="today">{today.strftime('%A, %-d %B %Y')}</span>
  <span class="topbar-tag">Cybersecurity news, insights &amp; practical guides</span>
  <ul class="topbar-social">{top_social}</ul>
  <a class="topbar-sub" href="{e(subscribe_href)}">{icon("bell", 15)}Subscribe</a>
</div></div>
<header class="masthead">
  <div class="wrap masthead-row">
    <a class="brand" href="{url('/')}"><img class="logo-on-light" src="{url('/assets/logo-light.png')}" alt="{e(SITE['name'])}" width="379" height="120"><img class="logo-on-dark" src="{url('/assets/logo.png')}" alt="{e(SITE['name'])}" width="347" height="184"></a>
    <div class="tools">
      <div class="search">
        <label class="visually-hidden" for="search-input">Search ZNexora Tech</label>
        <input id="search-input" type="search" placeholder="Search news, CVEs, topics" autocomplete="off" data-index="{url('/search-index.json')}">
        <ul id="search-results" hidden></ul>
      </div>
      <button id="theme-toggle" type="button" aria-label="Switch light or dark theme">
        <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9Z"/></svg>
      </button>
    </div>
  </div>
  <nav class="mainnav" aria-label="Sections"><div class="wrap"><ul>{nav}</ul></div></nav>
  <div class="color-strip" aria-hidden="true"></div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="footer">
  <div class="color-strip" aria-hidden="true"></div>
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <img src="{url('/assets/logo.png')}" alt="{e(SITE['name'])}" width="347" height="184" loading="lazy">
      <p class="mission">{e(SITE.get('mission') or SITE['description'])}</p>
    </div>
    <nav aria-label="Sections"><h2>Sections</h2><ul>{"".join(f'<li><a href="{url("/category/" + s + "/")}">{e(n)}</a></li>' for s, n in CATS.items())}{'<li><a href="' + url('/blog/') + '">Blog</a></li>' if blog_home().startswith('https://') else ''}</ul></nav>
    <div><h2>Follow us</h2><ul class="foot-follow">{foot_social}<li><a class="foot-chan" href="{url('/feed.xml')}">{icon("bell", 16)}RSS feed</a></li></ul></div>
    <div><h2>Company</h2><ul><li><a href="{url('/about/')}">About</a></li><li><a href="{url('/privacy/')}">Privacy</a></li><li><a href="{url('/posts/')}">All articles</a></li></ul></div>
  </div>
  <div class="wrap footer-bottom">
    <p class="motto"><span>Stay curious.</span> <span>Stay secure.</span> <span>Stay ahead.</span></p>
    <p class="fine">© {today.year} {e(SITE['name'])}. Content summarises public sources. Always confirm details with the vendor or original report.</p>
  </div>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------- building blocks
def kicker(p):
    name = "Blog" if p.get("category") == "blog" else CATS.get(p["category"], p["category"])
    return f'<span class="kicker {TONE.get(p["category"], "t-news")}">{e(name)}</span>'


def sev_chip(p):
    sev = p.get("severity")
    if p.get("category") != "exploited-vulnerabilities" or not sev:
        return ""
    score = p.get("score") or "?"
    return f'<span class="sev sev-{e(sev)}">{e(str(score))} {e(SEV_LABEL.get(sev, sev))}</span>'


def meta_line(p):
    return f'<p class="meta">{sev_chip(p)}<time datetime="{e(p["date"])}">{nice_date(p["date"])}</time></p>'


def img_tag(src, alt="", w=1200, h=630, lazy=True):
    loading = ' loading="lazy"' if lazy else ""
    return f'<img src="{e(src)}" alt="{e(alt)}" width="{w}" height="{h}"{loading} decoding="async">'


def card(p, size="md"):
    """A story card: picture, section, headline, date."""
    href = url(p["path"])
    pic = img_tag(url(p["cover"]), p.get("cover_alt", ""))
    dek = f'<p class="dek">{e(p["summary"])}</p>' if size in ("lg",) and p["summary"] else ""
    return (f'<article class="card card-{size}"><a class="card-pic" href="{href}" tabindex="-1" aria-hidden="true">{pic}</a>'
            f'<div class="card-body">{kicker(p)}<h3><a href="{href}">{e(p["title"])}</a></h3>{dek}{meta_line(p)}</div></article>')


def row(p):
    """A list row: small picture on the left, text on the right."""
    href = url(p["path"])
    return (f'<article class="row"><a class="row-pic" href="{href}" tabindex="-1" aria-hidden="true">{img_tag(url(p["cover"]))}</a>'
            f'<div class="row-body">{kicker(p)}<h3><a href="{href}">{e(p["title"])}</a></h3>'
            f'<p class="dek">{e(p["summary"])}</p>{meta_line(p)}</div></article>')


def blog_card(b):
    pic = (img_tag(b["image"], "", 800, 450) if b["image"]
           else f'<span class="blog-noimg">{icon("pen", 28)}</span>')
    label = b["labels"][0] if b["labels"] else "Blog"
    return (f'<article class="card card-md"><a class="card-pic" href="{e(b["link"])}" rel="noopener" tabindex="-1" aria-hidden="true">{pic}</a>'
            f'<div class="card-body"><span class="kicker t-blog">{e(label)}</span>'
            f'<h3><a href="{e(b["link"])}" rel="noopener">{e(b["title"])}</a></h3>'
            f'<p class="meta"><time datetime="{e(b["date"])}">{nice_date(b["date"]) if b["date"] else ""}</time><span class="ext">On our blog {icon("link", 13)}</span></p></div></article>')


def section_head(title, tone, link=None, label="See all"):
    more = f'<a class="more" href="{e(link)}">{e(label)} →</a>' if link else ""
    return f'<div class="section-head {tone}"><h2>{e(title)}</h2>{more}</div>'


def empty(msg):
    return f'<p class="empty">{e(msg)}</p>'


# ---------------------------------------------------------------- sidebar
def sidebar(posts, skip_exploited=False):
    parts = []
    cves = [p for p in posts if p["category"] == "exploited-vulnerabilities"][:6]
    if cves and not skip_exploited:
        items = "".join(f'<li><a href="{url(p["path"])}"><span class="sev sev-{e(p.get("severity") or "unscored")}">{e(str(p.get("score") or "?"))}</span>'
                        f'<span>{e(p.get("cve") or p["title"])}<small>{e((p.get("vendor", "") + " " + p.get("product", "")).strip())}</small></span></a></li>'
                        for p in cves)
        parts.append(f'<section class="widget t-exploit"><h2>Exploited right now</h2><ul class="cve-list">{items}</ul>'
                     f'<a class="more" href="{url("/category/exploited-vulnerabilities/")}">All exploited vulnerabilities →</a></section>')
    recap = [p for p in posts if p["category"] == "weekly-recap"][:1]
    if recap:
        r = recap[0]
        parts.append(f'<section class="widget widget-recap"><p class="kicker-light">Weekly recap</p>'
                     f'<h2><a href="{url(r["path"])}">{e(r["title"])}</a></h2><p>{e(r["summary"])}</p>'
                     f'<a class="more" href="{url(r["path"])}">Read this week’s recap →</a></section>')
    if social_channels():
        parts.append(f'<section class="widget"><h2>Follow ZNexora Tech</h2>{social_pills("follow follow-compact")}</section>')
    parts.append(f'<section class="widget widget-about"><a href="{url("/about/")}" tabindex="-1" aria-hidden="true">'
                 f'{img_tag(url("/assets/cover-900.jpg"), "", 900, 600)}</a><h2>About ZNexora Tech</h2>'
                 f'<p>{e(SITE.get("mission") or SITE["description"])}</p><a class="more" href="{url("/about/")}">Learn more →</a></section>')
    sub = SITE.get("newsletter_url") or url("/feed.xml")
    parts.append(f'<section class="widget widget-sub"><h2>Never miss an update</h2><p>Get new articles as soon as they are published.</p>'
                 f'<a class="btn" href="{e(sub)}">{icon("bell", 16)}Subscribe</a></section>')
    return '<aside class="sidebar">' + "".join(parts) + "</aside>"


# ---------------------------------------------------------------- pages
def write(path, content):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_home(posts):
    lead, rest = (posts[0], posts[1:]) if posts else (None, [])
    top = ""
    if lead:
        latest = "".join(f'<li>{kicker(p)}<a href="{url(p["path"])}">{e(p["title"])}</a>'
                         f'<time datetime="{e(p["date"])}">{nice_date(p["date"])}</time></li>' for p in posts[1:7])
        top = (f'<section class="top-grid"><article class="lead">'
               f'<a class="lead-pic" href="{url(lead["path"])}" tabindex="-1" aria-hidden="true">{img_tag(url(lead["cover"]), "", lazy=False)}</a>'
               f'{kicker(lead)}<h1 class="lead-title"><a href="{url(lead["path"])}">{e(lead["title"])}</a></h1>'
               f'<p class="dek">{e(lead["summary"])}</p>{meta_line(lead)}</article>'
               f'<aside class="latest-rail"><h2>Latest</h2><ol>{latest or "<li>New stories appear here once approved.</li>"}</ol></aside></section>')
    else:
        top = f'<section class="welcome"><h1>{e(SITE["tagline"])}</h1><p>{e(SITE["description"])}</p></section>'
    trio = rest[:3]
    trio_html = f'<section class="card-row">{"".join(card(p) for p in trio)}</section>' if trio else ""
    used = {p["slug"] for p in ([lead] if lead else []) + trio}
    news = [p for p in posts if p["slug"] not in used and p["category"] in ("news", "exploited-vulnerabilities", "weekly-recap")][:8]
    learn = [p for p in posts if p["category"] in ("theory", "practical")][:5]
    learn_html = ""
    if learn:
        learn_html = (section_head("Learn: theory & practical", "t-theory", url("/learn/"))
                      + f'<div class="learn-grid">{card(learn[0], "lg")}<div class="learn-list">{"".join(row(p) for p in learn[1:5])}</div></div>')
    blog_html = ""
    if BLOG:
        blog_html = (section_head("From the ZNexora Blog", "t-blog", url("/blog/"), "More from the blog")
                     + f'<div class="card-grid">{"".join(blog_card(b) for b in BLOG[:4])}</div>')
    community = ""
    if social_channels():
        community = (f'<section class="community"><div><h2>Join the ZNexora community</h2>'
                     f'<p>Daily security news, tips and guides on your favourite platform.</p></div>{social_pills()}</section>')
    body = f"""{top}
{trio_html}
<div class="with-sidebar">
  <div class="main-col">
    {section_head("Latest cybersecurity news", "t-news", url("/posts/"))}
    <div class="rows">{"".join(row(p) for p in news) or empty("The latest stories appear here once they are approved.")}</div>
    {learn_html}
    {blog_html}
  </div>
  {sidebar(posts)}
</div>
{community}"""
    write("/", layout(SITE["name"], body))


def build_post(p, posts):
    facts = []
    for label, key in [("CVE", "cve"), ("Vendor", "vendor"), ("Product", "product"), ("CVSS score", "score")]:
        if p.get(key):
            facts.append(f"<div><dt>{label}</dt><dd>{e(str(p[key]))}</dd></div>")
    if p.get("severity") and p["category"] == "exploited-vulnerabilities":
        facts.append(f"<div><dt>Severity</dt><dd>{e(SEV_LABEL.get(p['severity'], p['severity']))}</dd></div>")
    if p.get("ransomware", "").lower() == "known":
        facts.append("<div><dt>Ransomware use</dt><dd>Reported by CISA</dd></div>")
    if p.get("level"):
        facts.append(f"<div><dt>Level</dt><dd>{e(p['level'])}</dd></div>")
    if p.get("source") and p.get("source_url", "").startswith("http"):
        facts.append(f'<div><dt>Original report</dt><dd><a href="{e(p["source_url"])}" rel="noopener">{e(p["source"])}</a></dd></div>')
    keypoints = ""
    if p["summary"] or facts:
        keypoints = (f'<section class="keypoints {TONE.get(p["category"], "")}"><h2>Key points</h2>'
                     f'{"<p>" + e(p["summary"]) + "</p>" if p["summary"] else ""}'
                     f'{"<dl class=facts>" + "".join(facts) + "</dl>" if facts else ""}</section>')
    tags = [f'<a class="tag {TONE.get(p["category"], "")}" href="{url("/category/" + p["category"] + "/")}">{e(CATS.get(p["category"], p["category"]))}</a>']
    tags += [f'<span class="tag">{e(t)}</span>' for t in p["tag_list"][:5]]
    share_url = urllib.parse.quote(BASE_URL + p["path"], safe="")
    share_text = urllib.parse.quote(p["title"], safe="")
    shares = [("LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}", "briefcase"),
              ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={share_url}", "people"),
              ("WhatsApp", f"https://wa.me/?text={share_text}%20{share_url}", "chat"),
              ("Telegram", f"https://t.me/share/url?url={share_url}&text={share_text}", "send")]
    share_html = "".join(f'<li><a href="{e(h)}" rel="noopener" target="_blank" aria-label="Share on {n}">{icon(i, 18)}<span>{n}</span></a></li>'
                         for n, h, i in shares)
    toc = ""
    if len(p["toc"]) >= 2:
        toc = '<nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>' + "".join(
            f'<li><a href="#{e(i)}">{e(n)}</a></li>' for i, n in p["toc"]) + "</ol></nav>"
    related = [x for x in posts if x["category"] == p["category"] and x["slug"] != p["slug"]][:3]
    if len(related) < 3:
        related += [x for x in posts if x["slug"] != p["slug"] and x not in related][:3 - len(related)]
    related_html = (section_head("Related content", "t-news") + f'<div class="card-row">{"".join(card(x) for x in related)}</div>') if related else ""
    thanks = f"""<section class="thanks" aria-labelledby="thanks-title">
  <h2 id="thanks-title">Thank you for reading!</h2>
  <p>Let’s continue to build a safer and more trustworthy digital future together.</p>
  {('<p class="thanks-follow">Follow ZNexora Tech</p>' + social_pills()) if social_channels() else ''}
  <p class="thanks-motto">Stay curious. Stay secure. Stay ahead.</p>
</section>"""
    body = f"""<div class="article-layout">
<article class="article">
  <header class="article-head">
    <p class="crumbs"><a href="{url('/')}">Home</a> <span aria-hidden="true">/</span> <a href="{url('/category/' + p['category'] + '/')}">{e(CATS.get(p['category'], p['category']))}</a></p>
    <h1>{e(p['title'])}</h1>
    <p class="byline">By <strong>{e(p.get('author') or SITE.get('author') or SITE['name'])}</strong>
      <span class="dot" aria-hidden="true"></span><time datetime="{e(p['date'])}">{nice_date(p['date'], True)}</time>
      <span class="dot" aria-hidden="true"></span>{p['minutes']} min read</p>
    <div class="tags">{"".join(tags)}</div>
  </header>
  {keypoints}
  <figure class="article-cover">{img_tag(url(p['cover']), p['cover_alt'], lazy=False)}</figure>
  <div class="prose">{p['html']}</div>
  <section class="share-bottom"><h2>Share this article</h2><ul class="share-list">{share_html}</ul></section>
  {thanks}
</article>
<aside class="article-aside">
  <div class="aside-sticky">
    <section class="share-side"><h2>Share</h2><ul class="share-list">{share_html}</ul></section>
    {toc}
  </div>
</aside>
</div>
<section class="related">{related_html}</section>"""
    write(p["path"], layout(p["title"], body, p["summary"], p["path"], "article", p["cover"]))


def list_page(path, title, intro, items, tone, posts, image=None):
    body = f"""<header class="page-head {tone}"><p class="kicker {tone}">Section</p><h1>{e(title)}</h1><p>{e(intro)}</p></header>
<div class="with-sidebar">
  <div class="main-col"><div class="rows">{"".join(row(p) for p in items) or empty("Articles appear here once they are approved.")}</div></div>
  {sidebar(posts, skip_exploited=(tone == "t-exploit"))}
</div>"""
    write(path, layout(title, body, f"{title}: {intro}", path, image=image or "/assets/og-image.jpg"))


def build_lists(posts):
    list_page("/posts/", "All articles", "Everything published on ZNexora Tech, newest first.", posts, "t-news", posts)
    list_page("/learn/", "Learn: theory & practical", "Concepts and hands-on guides for defenders.",
              [p for p in posts if p["category"] in ("theory", "practical")], "t-theory", posts)
    for slug, name in CATS.items():
        list_page(f"/category/{slug}/", name, CAT_INTRO.get(slug, ""), [p for p in posts if p["category"] == slug],
                  TONE.get(slug, "t-news"), posts)


def build_blog_page(posts):
    home = blog_home()
    if not home.startswith("https://"):
        return
    grid = "".join(blog_card(b) for b in BLOG) or empty("Our latest blog posts will appear here shortly.")
    body = f"""<header class="page-head t-blog"><p class="kicker t-blog">Blog</p><h1>The ZNexora Blog</h1>
<p>In-depth guides, awareness articles and security insights from our team.</p>
<a class="btn" href="{e(home)}" rel="noopener">{icon("pen", 16)}Visit the full blog</a></header>
<div class="card-grid card-grid-3">{grid}</div>"""
    write("/blog/", layout("Blog", body, "In-depth guides and security insights from the ZNexora Tech blog.", "/blog/"))


def build_pages():
    for path in PAGES_DIR.glob("*.md"):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem.title())
        content, _ = render_md(body)
        figure = follow = ""
        if path.stem == "about":
            figure = f'<figure class="article-cover">{img_tag(url("/assets/cover.jpg"), "ZNexora Tech: Empowering minds. Securing futures.", 1536, 1024, False)}</figure>'
            if social_channels():
                follow = '<section class="about-follow"><h2>Follow ZNexora Tech</h2>' + social_pills() + '</section>'
        body_html = (f'<article class="article article-page"><header class="article-head"><h1>{e(title)}</h1></header>'
                     f'{figure}<div class="prose">{content}</div>{follow}</article>')
        write(f"/{path.stem}/", layout(title, body_html, path=f"/{path.stem}/"))


def build_feeds(posts):
    index = [{"t": p["title"], "u": url(p["path"]), "s": p["summary"], "c": p.get("cve", ""),
              "v": f'{p.get("vendor", "")} {p.get("product", "")}'} for p in posts]
    index += [{"t": b["title"], "u": b["link"], "s": b["excerpt"], "c": "", "v": "blog"} for b in BLOG]
    (OUT / "search-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    def rfc822(iso):
        d = dt.datetime.fromisoformat(iso[:10]).replace(hour=8, tzinfo=dt.timezone.utc)
        return email.utils.format_datetime(d)
    items = "".join(f"""<item><title>{e(p['title'])}</title><link>{BASE_URL}{p['path']}</link>
<guid isPermaLink="true">{BASE_URL}{p['path']}</guid><pubDate>{rfc822(p['date'])}</pubDate>
<description>{e(p['summary'])}</description></item>""" for p in posts[:30])
    (OUT / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{e(SITE['name'])}</title><link>{BASE_URL}/</link>
<description>{e(SITE['description'])}</description><language>{e(SITE.get('language', 'en'))}</language>
{items}</channel></rss>
""", encoding="utf-8")
    pages = ["/", "/posts/", "/learn/", "/blog/", "/about/"] + [f"/category/{s}/" for s in CATS] + [p["path"] for p in posts]
    urls = "".join(f"<url><loc>{BASE_URL}{u}</loc></url>" for u in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")


def main():
    global BLOG
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    BLOG = read_blog(SITE)
    posts = load_posts()
    for p in posts:
        if not p["own_image"]:
            make_cover(OUT / "covers" / f"{p['slug']}.jpg", p["title"], p["category"],
                       p.get("score", ""), p.get("severity", ""), key=p["slug"])
    print(f"Drew {sum(not p['own_image'] for p in posts)} graphic(s)")
    for p in posts:
        build_post(p, posts)
    build_home(posts)
    build_lists(posts)
    build_blog_page(posts)
    build_pages()
    build_feeds(posts)
    write("/404.html", layout("Page not found", '<header class="page-head"><h1>Page not found</h1>'
                                                f'<p>This page does not exist. <a href="{url("/")}">Go to the latest news</a> or search above.</p></header>'))
    (OUT / ".nojekyll").write_text("")
    contact = SITE.get("security_contact") or SITE.get("contact_email", "")
    if contact:
        expires = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=365)).strftime("%Y-%m-%dT00:00:00Z")
        contact_uri = contact if contact.startswith(("mailto:", "https://")) else "mailto:" + contact
        (OUT / ".well-known").mkdir(exist_ok=True)
        (OUT / ".well-known" / "security.txt").write_text(
            f"Contact: {contact_uri}\nExpires: {expires}\nPreferred-Languages: en\n"
            f"Canonical: {BASE_URL}/.well-known/security.txt\nPolicy: {BASE_URL}/about/\n")
    if SITE.get("custom_domain"):
        (OUT / "CNAME").write_text(SITE["custom_domain"].strip() + "\n")
    print(f"Built {len(posts)} post(s) into _site/")


if __name__ == "__main__":
    main()
