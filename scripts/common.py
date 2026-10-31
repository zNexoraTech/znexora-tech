"""Shared helpers used by every script."""
import datetime as dt
import html
import json
import pathlib
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
PAGES_DIR = ROOT / "content" / "pages"
DATA_DIR = ROOT / "data"
USER_AGENT = "Mozilla/5.0 (compatible; ZNexoraTech-bot/1.0)"


# ---------- settings and files ----------
def load_site():
    return json.loads((ROOT / "site.json").read_text(encoding="utf-8"))


def automation(section):
    site = load_site()
    auto = site.get("automation", {})
    return site, auto.get(section, {}), auto.get("ai_model", "claude-haiku-5-5")


def load_json(name, default):
    path = DATA_DIR / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(name, value):
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def today():
    return dt.datetime.now(dt.timezone.utc).date()


def slugify(text, maxlen=80):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:maxlen].rstrip("-") or "post"


def nice_date(d):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d[:10])
    return f"{d.day} {d.strftime('%b %Y')}"


# ---------- posts ----------
def parse_front_matter(text):
    """Split a post into (metadata dict, markdown body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, "\n".join(lines[i + 1:]).strip() + "\n"
        if ":" in lines[i]:
            key, value = lines[i].split(":", 1)
            meta[key.strip()] = value.strip()
    return {}, text


def dump_front_matter(meta, body):
    out = ["---"]
    for key, value in meta.items():
        out.append(f"{key}: {str(value).replace(chr(10), ' ').strip()}")
    out += ["---", "", body.strip(), ""]
    return "\n".join(out)


def existing_post_meta():
    return [parse_front_matter(p.read_text(encoding="utf-8"))[0] for p in POSTS_DIR.glob("*.md")]


# ---------- web ----------
def http_get(url, headers=None, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def http_json(url, headers=None, data=None, method=None, timeout=60):
    hdrs = {"User-Agent": USER_AGENT}
    if data is not None:
        hdrs["Content-Type"] = "application/json"
        data = json.dumps(data).encode("utf-8")
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else {}


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _parse_date(text):
    if not text:
        return None
    try:
        d = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def parse_feed(xml_bytes, source):
    """Read an RSS or Atom feed into a list of {title, link, summary, date, source}."""
    root = ET.fromstring(xml_bytes)
    items = []
    atom = "{http://www.w3.org/2005/Atom}"
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        def find(*names):
            for n in names:
                el = node.find(n)
                if el is not None:
                    return el
            return None
        title = find("title", atom + "title")
        link_el = find("link", atom + "link")
        link = ""
        if link_el is not None:
            link = (link_el.text or link_el.get("href") or "").strip()
        desc = find("description", atom + "summary", atom + "content")
        date = find("pubDate", atom + "updated", atom + "published",
                    "{http://purl.org/dc/elements/1.1/}date")
        if title is None or not link:
            continue
        items.append({
            "title": strip_html(title.text),
            "link": link,
            "summary": strip_html(desc.text if desc is not None else "")[:600],
            "date": _parse_date(date.text if date is not None else ""),
            "source": source,
        })
    return items


def tag_story(text):
    t = text.lower()
    tags = []
    if "ransomware" in t or "extortion" in t:
        tags.append("ransomware")
    if "defac" in t or "hacktivis" in t:
        tags.append("defacement")
    if re.search(r"cve-\d{4}-\d+|zero-day|0-day|vulnerab|exploit", t):
        tags.append("vulnerability")
    if "breach" in t or "leak" in t:
        tags.append("breach")
    return tags


def severity_from_score(score):
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "unscored"
    if s >= 9:
        return "critical"
    if s >= 7:
        return "high"
    if s >= 4:
        return "medium"
    return "low" if s > 0 else "unscored"


# ---------- GitHub: drafts for approval ----------
def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def open_draft(slug, title, content, pr_body):
    """Put one post on its own branch and open a pull request for approval."""
    branch = f"draft/{slug}"
    try:
        git("checkout", "-B", branch, "main")
        path = POSTS_DIR / f"{slug}.md"
        path.write_text(content, encoding="utf-8")
        git("add", str(path))
        git("commit", "-m", f"Draft: {title}")
        git("push", "--force", "origin", branch)
        subprocess.run(["gh", "pr", "create", "--base", "main", "--head", branch,
                        "--title", f"Draft: {title}", "--body", pr_body],
                       cwd=ROOT, check=True, capture_output=True, text=True)
        print(f"  opened draft: {title}")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  could not open the draft: {(exc.stderr or str(exc)).strip()}")
        print("  Check Settings > Actions > General > 'Allow GitHub Actions to create and approve pull requests'.")
        return False
    finally:
        subprocess.run(["git", "checkout", "-f", "main"], cwd=ROOT, capture_output=True)


def save_draft(slug, title, content, pr_body, dry_run):
    if dry_run:
        (POSTS_DIR / f"{slug}.md").write_text(content, encoding="utf-8")
        print(f"  wrote content/posts/{slug}.md")
        return True
    return open_draft(slug, title, content, pr_body)


def commit_state(message, dry_run):
    """Save the robot's memory (data/*.json) on main so nothing is drafted twice."""
    if dry_run:
        return
    git("add", "data")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        return
    git("commit", "-m", message)
    git("pull", "--rebase", "origin", "main")
    git("push", "origin", "main")


PR_FOOTER = """
**To publish:** tap **Merge pull request**. The site updates and the post is shared automatically.
**To reject:** tap **Close pull request**. It will not be drafted again.
**To edit first:** open **Files changed**, then the file menu (…) > **Edit file**, commit, then merge."""
