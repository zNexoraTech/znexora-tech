"""Builds the whole website into the _site folder. Run: python scripts/build.py"""
import datetime as dt
import email.utils
import html
import json
import re
import shutil
import urllib.parse

import markdown

from common import PAGES_DIR, POSTS_DIR, ROOT, load_site, parse_front_matter

OUT = ROOT / "_site"
SITE = load_site()
BASE_URL = SITE["url"].rstrip("/")
if SITE.get("custom_domain"):
    BASE_URL = "https://" + SITE["custom_domain"].strip().strip("/")
BP = urllib.parse.urlparse(BASE_URL).path.rstrip("/")  # e.g. "/secbrief" on github.io
CATS = SITE.get("categories", {})
KIND = {"news": "News", "weekly-recap": "Recap", "theory": "Theory", "practical": "Practical"}
SEV_LABEL = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low", "unscored": "Not scored"}
e = html.escape


def url(path):
    return f"{BP}{path}"


def render_md(text):
    """Markdown to HTML with raw HTML switched off, so posts can never inject scripts."""
    md = markdown.Markdown(extensions=["tables", "pymdownx.superfences", "sane_lists"])
    md.preprocessors.deregister("html_block")
    md.inlinePatterns.deregister("html")
    out = md.convert(text)
    out = re.sub(r'href="\s*(javascript|data|vbscript):[^"]*"', 'href="#"', out, flags=re.I)
    return out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def load_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if not meta.get("title") or meta.get("draft", "").lower() == "true":
            continue
        meta["slug"] = path.stem
        meta["path"] = f"/posts/{path.stem}/"
        meta["html"] = render_md(body)
        meta["minutes"] = max(1, round(len(body.split()) / 200))
        meta.setdefault("category", "news")
        meta.setdefault("severity", "")
        meta.setdefault("summary", "")
        meta["date"] = meta.get("date") or dt.date.today().isoformat()
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def nice_date(iso):
    try:
        return dt.date.fromisoformat(iso[:10]).strftime("%-d %b %Y")
    except ValueError:
        return iso


def layout(title, body, description="", path="/", og_type="website"):
    full_title = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    desc = description or SITE["description"]
    canonical = BASE_URL + path
    def nav_link(href, label):
        here = ' aria-current="page"' if path == href else ""
        return f'<a href="{url(href)}"{here}>{e(label)}</a>'
    nav = "".join(nav_link(f"/category/{slug}/", name) for slug, name in CATS.items())
    subscribe = (f'<a class="subscribe" href="{e(SITE["newsletter_url"])}" rel="noopener">Get the email briefing</a>'
                 if SITE.get("newsletter_url") else "")
    year = dt.date.today().year
    return f"""<!doctype html>
<html lang="{e(SITE.get('language', 'en'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:image" content="{BASE_URL}/assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL}/assets/og-image.jpg">
<meta name="theme-color" content="#040a1f">
<link rel="alternate" type="application/rss+xml" title="{e(SITE['name'])}" href="{url('/feed.xml')}">
<link rel="icon" href="{url('/assets/favicon-32.png')}" sizes="32x32" type="image/png">
<link rel="icon" href="{url('/assets/icon-512.png')}" sizes="512x512" type="image/png">
<link rel="apple-touch-icon" href="{url('/assets/apple-touch-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Literata:opsz,wght@7..72,400;7..72,600&display=swap">
<link rel="stylesheet" href="{url('/assets/style.css')}">
<script src="{url('/assets/app.js')}"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead-row">
    <a class="brand" href="{url('/')}"><img src="{url('/assets/logo.png')}" alt="{e(SITE['name'])}" width="347" height="184"></a>
    <div class="tools">
      <div class="search">
        <label class="visually-hidden" for="search-input">Search briefings</label>
        <input id="search-input" type="search" placeholder="Search news, CVEs, topics" autocomplete="off" data-index="{url('/search-index.json')}">
        <ul id="search-results" hidden></ul>
      </div>
      <button id="theme-toggle" type="button" aria-label="Switch light or dark theme">
        <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9Z"/></svg>
      </button>
    </div>
  </div>
  <nav class="wrap catnav" aria-label="Categories">{nav_link("/posts/", "All posts")}{nav}</nav>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="footer">
  <div class="wrap footer-row">
    <p class="mission">{e(SITE.get('mission') or SITE['description'])}</p>
    <p class="footer-links">{subscribe}<a href="{url('/feed.xml')}">RSS</a><a href="{url('/about/')}">About</a><a href="{url('/privacy/')}">Privacy</a></p>
    <p class="fine">© {year} {e(SITE['name'])}. Content summarises public sources. Always confirm details with the vendor or original report.</p>
  </div>
</footer>
</body>
</html>
"""


def score_cell(p):
    score = p.get("score") or ""
    sev = p.get("severity") or ""
    if not sev:
        kind = KIND.get(p.get("category"), "Brief")
        return f'<span class="score kind kind-{e(p.get("category", ""))}"><span class="kind-label">{e(kind)}</span></span>'
    shown = score if score else "?"
    return (f'<span class="score sev-{e(sev)}" title="{e(SEV_LABEL.get(sev, sev))}">'
            f'<span class="score-num">{e(str(shown))}</span>'
            f'<span class="score-sev">{e(SEV_LABEL.get(sev, sev))}</span></span>')


def row(p):
    who = " ".join(x for x in [p.get("vendor", ""), p.get("product", "")] if x) or p.get("source", "")
    meta = f'<span>{e(who)}</span>' if who else f'<span>{e(CATS.get(p["category"], p["category"]))}</span>'
    return (f'<li class="row"><a href="{url(p["path"])}">{score_cell(p)}'
            f'<span class="row-main"><span class="row-title">{e(p["title"])}</span>'
            f'<span class="row-sum">{e(p["summary"])}</span>'
            f'<span class="row-meta">{meta}<time datetime="{e(p["date"])}">{nice_date(p["date"])}</time></span>'
            f'</span></a></li>')


def post_list(posts, empty="No briefings here yet. New ones appear after they are approved."):
    if not posts:
        return f'<p class="empty">{e(empty)}</p>'
    return '<ol class="rows">' + "".join(row(p) for p in posts) + "</ol>"


def write(path, content):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_post(p, posts):
    sev = p.get("severity")
    facts = []
    for label, key in [("CVE", "cve"), ("Vendor", "vendor"), ("Product", "product"), ("CVSS score", "score")]:
        if p.get(key):
            facts.append(f"<div><dt>{label}</dt><dd>{e(str(p[key]))}</dd></div>")
    if sev:
        facts.append(f"<div><dt>Severity</dt><dd>{e(SEV_LABEL.get(sev, sev))}</dd></div>")
    if p.get("level"):
        facts.append(f"<div><dt>Level</dt><dd>{e(p['level'])}</dd></div>")
    if p["category"] in ("theory", "practical", "weekly-recap"):
        facts.append(f"<div><dt>Reading time</dt><dd>{p['minutes']} min</dd></div>")
    if p.get("source") and p.get("source_url", "").startswith("http"):
        facts.append(f'<div><dt>Original report</dt><dd><a href="{e(p["source_url"])}" rel="noopener">{e(p["source"])}</a></dd></div>')
    if p.get("ransomware", "").lower() == "known":
        facts.append("<div><dt>Ransomware use</dt><dd>Reported by CISA</dd></div>")
    meter = ""
    if p.get("score"):
        try:
            v = max(0.0, min(10.0, float(p["score"])))
            meter = (f'<div class="meter sev-{e(sev)}" role="img" aria-label="CVSS {v} out of 10">'
                     f'<span style="width:{v * 10:.0f}%"></span></div>')
        except ValueError:
            pass
    related = [x for x in posts if x["category"] == p["category"] and x["slug"] != p["slug"]][:3]
    related_html = f'<section class="related"><h2>More {e(CATS.get(p["category"], "briefings")).lower()}</h2>{post_list(related)}</section>' if related else ""
    share_url = urllib.parse.quote(BASE_URL + p["path"], safe="")
    share_text = urllib.parse.quote(p["title"], safe="")
    body = f"""<article class="post">
  <header class="post-head">
    <p class="crumb"><a href="{url('/category/' + p['category'] + '/')}">{e(CATS.get(p['category'], p['category']))}</a>
    <time datetime="{e(p['date'])}">{nice_date(p['date'])}</time></p>
    <h1>{e(p['title'])}</h1>
    {f'<p class="lead">{e(p["summary"])}</p>' if p['summary'] else ''}
    {meter}
    {f'<dl class="facts">{"".join(facts)}</dl>' if facts else ''}
  </header>
  <div class="prose">{p['html']}</div>
  <p class="share">Share:
    <a href="https://bsky.app/intent/compose?text={share_text}%20{share_url}" rel="noopener">Bluesky</a>
    <a href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" rel="noopener">LinkedIn</a>
    <a href="https://t.me/share/url?url={share_url}&amp;text={share_text}" rel="noopener">Telegram</a>
  </p>
</article>
{related_html}"""
    write(p["path"], layout(p["title"], body, p["summary"], p["path"], "article"))


def build_home(posts):
    by = lambda *cats: [p for p in posts if p["category"] in cats]
    recap = by("weekly-recap")[:1]
    recap_html = ""
    if recap:
        r = recap[0]
        recap_html = f"""<section class="recap-feature">
  <p class="recap-kicker">This week in security</p>
  <h2><a href="{url(r['path'])}">{e(r['title'])}</a></h2>
  <p>{e(r['summary'])}</p>
  <a class="recap-link" href="{url(r['path'])}">Read the weekly recap</a>
</section>"""

    def block(title, items, link, empty):
        return (f'<section><div class="section-head"><h2>{e(title)}</h2>'
                f'<a href="{url(link)}">See all</a></div>{post_list(items, empty)}</section>')

    body = f"""<section class="hero">
  <h1>{e(SITE['tagline'])}</h1>
  <p>{e(SITE['description'])}</p>
  <ul class="hero-topics">
    <li><a href="{url('/category/news/')}">Latest news</a></li>
    <li><a href="{url('/category/weekly-recap/')}">Weekly recap</a></li>
    <li><a href="{url('/category/exploited-vulnerabilities/')}">Exploited vulnerabilities</a></li>
    <li><a href="{url('/learn/')}">Theory and practice</a></li>
  </ul>
</section>
{recap_html}
<div class="home-grid">
  <div>
    {block("Latest news", by("news")[:6], "/category/news/", "The latest stories appear here once they are approved.")}
    {block("Exploited vulnerabilities", by("exploited-vulnerabilities")[:5], "/category/exploited-vulnerabilities/", "New exploited vulnerabilities appear here once they are approved.")}
  </div>
  <div>
    {block("Learn: theory and practice", by("theory", "practical")[:6], "/learn/", "Theory articles and practical guides appear here once they are approved.")}
  </div>
</div>"""
    write("/", layout(SITE["name"], body))


def build_lists(posts):
    learn = [p for p in posts if p["category"] in ("theory", "practical")]
    write("/learn/", layout("Learn", '<h1 class="page-title">Learn: theory and practice</h1>' + post_list(learn), path="/learn/"))
    write("/posts/", layout("All briefings", f'<h1 class="page-title">All briefings</h1>{post_list(posts)}', path="/posts/"))
    for slug, name in CATS.items():
        items = [p for p in posts if p["category"] == slug]
        write(f"/category/{slug}/", layout(name, f'<h1 class="page-title">{e(name)}</h1>{post_list(items)}',
                                            f"{name} from {SITE['name']}", f"/category/{slug}/"))


def build_pages():
    for path in PAGES_DIR.glob("*.md"):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem.title())
        write(f"/{path.stem}/", layout(title, f'<article class="post"><h1 class="page-title">{e(title)}</h1>'
                                              f'<div class="prose">{render_md(body)}</div></article>', path=f"/{path.stem}/"))


def build_feeds(posts):
    index = [{"t": p["title"], "u": url(p["path"]), "s": p["summary"], "c": p.get("cve", ""),
              "v": f'{p.get("vendor", "")} {p.get("product", "")}'} for p in posts]
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

    pages = ["/", "/posts/", "/learn/"] + [f"/category/{s}/" for s in CATS] + [p["path"] for p in posts]
    urls = "".join(f"<url><loc>{BASE_URL}{u}</loc></url>" for u in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    posts = load_posts()
    for p in posts:
        build_post(p, posts)
    build_home(posts)
    build_lists(posts)
    build_pages()
    build_feeds(posts)
    write("/404.html", layout("Page not found", '<h1 class="page-title">Page not found</h1>'
                                                f'<p>This page does not exist. <a href="{url("/")}">Go to the latest briefings</a> or search above.</p>'))
    (OUT / ".nojekyll").write_text("")
    if SITE.get("custom_domain"):
        (OUT / "CNAME").write_text(SITE["custom_domain"].strip() + "\n")
    print(f"Built {len(posts)} post(s) into _site/")


if __name__ == "__main__":
    main()
