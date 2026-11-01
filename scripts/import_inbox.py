"""Turns Word (.docx) and PowerPoint (.pptx) files you upload into website articles.

How to use: upload your files into the inbox folder on GitHub, inside a folder named after
the section, for example:

    inbox/theory/Zero Trust Explained.docx
    inbox/theory/Zero Trust Explained.pptx      (optional, same name = same article)
    inbox/practical/Harden SSH.docx

The robot converts them and opens a draft (pull request) for your approval, exactly like the
other robots. When you merge it, the article is published and shared everywhere.

Word file    -> the article text, headings, lists, tables and pictures
PowerPoint   -> a PDF download, a slide gallery, and the first slide as the cover picture
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import (PR_FOOTER, ROOT, automation, commit_state, dump_front_matter, git, load_json,
                    save_json, slugify, today)

INBOX = ROOT / "inbox"
SECTIONS = {"news", "weekly-recap", "exploited-vulnerabilities", "theory", "practical"}
IMAGES = ROOT / "assets" / "images"
FILES = ROOT / "assets" / "files"


def file_hash(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def groups():
    """Pair .docx and .pptx files that share a name. Returns {(section, name): {"docx": p, "pptx": p}}."""
    found = {}
    for path in sorted(INBOX.rglob("*")):
        if path.suffix.lower() not in (".docx", ".pptx") or path.name.startswith("~$"):
            continue
        section = path.parent.name if path.parent != INBOX else "theory"
        if section not in SECTIONS:
            section = "theory"
        found.setdefault((section, path.stem.strip()), {})[path.suffix.lower()[1:]] = path
    return found


# ---------------------------------------------------------------- Word
def convert_docx(path, slug):
    import mammoth
    from markdownify import markdownify

    folder = IMAGES / slug
    count = [0]

    def save_image(image):
        count[0] += 1
        ext = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp"}.get(image.content_type)
        if not ext:  # unusual formats (e.g. EMF drawings) are skipped
            return {"src": ""}
        folder.mkdir(parents=True, exist_ok=True)
        name = f"img-{count[0]}.{ext}"
        with image.open() as data:
            (folder / name).write_bytes(data.read())
        return {"src": f"../../assets/images/{slug}/{name}", "alt": image.alt_text or ""}

    with path.open("rb") as f:
        result = mammoth.convert_to_html(f, convert_image=mammoth.images.img_element(save_image))
    html = re.sub(r'<img src=""[^>]*>', "", result.value)
    md = markdownify(html, heading_style="ATX", bullets="-", strip=["span"], table_infer_header=True)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    # Title: the first big heading, or the file name
    title = path.stem.strip()
    m = re.match(r"#\s+(.+)\n", md + "\n")
    if m:
        title = m.group(1).strip()
        md = md[m.end():].lstrip()
    md = re.sub(r"^#\s+", "## ", md, flags=re.M)  # article headings start at level 2 on the website
    first = next((p for p in md.split("\n\n") if p.strip() and not p.startswith(("#", "!", "-", "|", "*"))), "")
    summary = re.sub(r"[*_`\[\]]|\(http[^)]*\)", "", first).strip()
    summary = summary[:220].rsplit(" ", 1)[0] + "…" if len(summary) > 220 else summary
    return title, summary, md


# ---------------------------------------------------------------- PowerPoint
def soffice():
    return shutil.which("soffice") or shutil.which("libreoffice")


def convert_pptx(path, slug):
    """Returns (markdown for the slides section, cover file or None)."""
    from PIL import Image
    if not soffice():
        print("  LibreOffice is not installed; skipping the slides.")
        return "", None
    work = Path(tempfile.mkdtemp())
    subprocess.run([soffice(), "--headless", "--convert-to", "pdf", "--outdir", str(work), str(path)],
                   check=True, capture_output=True, timeout=300)
    pdf = next(work.glob("*.pdf"))
    FILES.mkdir(parents=True, exist_ok=True)
    shutil.copy(pdf, FILES / f"{slug}.pdf")
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=82", "-scale-to", "1280", str(pdf), str(work / "s")],
                   check=True, capture_output=True, timeout=300)
    slides = sorted(work.glob("s-*.jpg"), key=lambda p: int(re.findall(r"\d+", p.stem)[-1]))
    folder = IMAGES / slug / "slides"
    folder.mkdir(parents=True, exist_ok=True)
    names = []
    for i, s in enumerate(slides, 1):
        name = f"slide-{i}.jpg"
        shutil.copy(s, folder / name)
        names.append(name)
    cover = None
    if names:  # first slide becomes the cover, cropped to the 1200 x 630 shape used for previews
        im = Image.open(folder / names[0]).convert("RGB")
        ratio = 1200 / 630
        w, h = im.size
        if w / h > ratio:
            nw = int(h * ratio); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / ratio); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        cover = IMAGES / f"{slug}.jpg"
        im.resize((1200, 630), Image.LANCZOS).save(cover, quality=85, optimize=True)
    gallery = "\n\n".join(f"![Slide {i}](../../assets/images/{slug}/slides/{n})" for i, n in enumerate(names, 1))
    md = (f"## Slides\n\n[Download the slides as PDF](../../assets/files/{slug}.pdf)\n\n{gallery}") if names else ""
    shutil.rmtree(work, ignore_errors=True)
    return md, cover


# ---------------------------------------------------------------- drafts
def make_article(section, name, files, site):
    docx, pptx = files.get("docx"), files.get("pptx")
    title, summary, body = (name, "", "")
    slug_hint = slugify(name)
    if docx:
        title, summary, body = convert_docx(docx, slug_hint)
    slug = slugify(title)
    if slug != slug_hint and (IMAGES / slug_hint).exists():  # keep pictures under the final name
        (IMAGES / slug_hint).rename(IMAGES / slug)
        body = body.replace(f"/images/{slug_hint}/", f"/images/{slug}/")
    slides_md = ""
    if pptx:
        slides_md, _ = convert_pptx(pptx, slug)
    if not summary:
        summary = f"{title}: slides and key points from ZNexora Tech."
    meta = {"title": title, "date": today().isoformat(), "category": section, "summary": summary,
            "author": site.get("author") or site["name"], "drafted_by": "upload"}
    full = "\n\n".join(x for x in (body, slides_md) if x)
    return slug, title, dump_front_matter(meta, full or "Write your article here.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    site, _, _ = automation("articles")
    done = load_json("imported.json", {})
    todo = {k: v for k, v in groups().items()
            if any(done.get(str(p.relative_to(ROOT))) != file_hash(p) for p in v.values())}
    if not todo:
        return print("Nothing new in the inbox.")
    for (section, name), files in todo.items():
        print(f"- {section}: {name} ({', '.join(sorted(files))})")
        sources = [str(p.relative_to(ROOT)) for p in files.values()]
        hashes = {s: file_hash(ROOT / s) for s in sources}
        if args.dry_run:
            slug, title, content = make_article(section, name, files, site)
            (ROOT / "content" / "posts" / f"{slug}.md").write_text(content, encoding="utf-8")
            print(f"  wrote content/posts/{slug}.md")
            done.update(hashes)
            continue
        try:
            branch_slug = slugify(name)
            git("checkout", "-B", f"draft/upload-{branch_slug}", "main")
            slug, title, content = make_article(section, name, files, site)
            post = ROOT / "content" / "posts" / f"{slug}.md"
            post.write_text(content, encoding="utf-8")
            git("add", str(post))
            for extra in (IMAGES / slug, IMAGES / f"{slug}.jpg", FILES / f"{slug}.pdf"):
                if extra.exists():
                    git("add", str(extra))
            git("rm", "-q", *sources)  # the inbox empties itself when you approve
            git("commit", "-m", f"Draft from upload: {title}")
            git("push", "--force", "origin", f"draft/upload-{branch_slug}")
            body = (f"Article converted from your upload ({', '.join(Path(s).name for s in sources)}).\n\n"
                    f"- [ ] Title, headings and pictures look right (see **Files changed**)\n"
                    f"- [ ] The summary in the top section reads well\n\n"
                    f"When you merge, it is published on the website and shared to your channels.\n{PR_FOOTER}")
            subprocess.run(["gh", "pr", "create", "--base", "main", "--head", f"draft/upload-{branch_slug}",
                            "--title", f"Draft: {title}", "--body", body], cwd=ROOT, check=True,
                           capture_output=True, text=True)
            print(f"  opened draft: {title}")
            done.update(hashes)
        except subprocess.CalledProcessError as exc:
            print(f"  could not create the draft: {(exc.stderr or str(exc)).strip()[:300]}")
        finally:
            subprocess.run(["git", "checkout", "-f", "main"], cwd=ROOT, capture_output=True)
            subprocess.run(["git", "clean", "-fdq", "assets/images", "assets/files", "content/posts"], cwd=ROOT,
                           capture_output=True)
    save_json("imported.json", done)
    commit_state("Robot memory: imported uploads", args.dry_run)


if __name__ == "__main__":
    main()
