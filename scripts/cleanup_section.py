"""Removes every article in one section except the ones you choose to keep, together with
their pictures, slide images and PDFs.

Run from Actions > "Clean up a section". Mode "preview" only lists what would be removed;
mode "delete" removes it and republishes the website.
"""
import os
import re
import shutil
import sys

from common import POSTS_DIR, ROOT, git, parse_front_matter

IMAGES = ROOT / "assets" / "images"
FILES = ROOT / "assets" / "files"


def names(text):
    """Accept article names or full web addresses, separated by commas or new lines."""
    out = set()
    for part in re.split(r"[,\n]+", text or ""):
        part = re.sub(r"[?#].*$", "", part.strip()).rstrip("/")
        part = part.rsplit("/", 1)[-1].removesuffix(".md")
        if part:
            out.add(re.sub(r"[^a-z0-9-]", "", part.lower()))
    return out


def related_files(slug):
    found = [POSTS_DIR / f"{slug}.md", IMAGES / slug, FILES / f"{slug}.pdf"]
    found += [IMAGES / f"{slug}{ext}" for ext in (".jpg", ".jpeg", ".png", ".webp")]
    return [p for p in found if p.exists()]


def main():
    section = (os.environ.get("SECTION") or "").strip().lower()
    keep = names(os.environ.get("KEEP", ""))
    mode = (os.environ.get("MODE") or "preview").strip().lower()
    if not section:
        sys.exit("Please choose a section.")
    remove, kept = [], []
    for post in sorted(POSTS_DIR.glob("*.md")):
        meta, _ = parse_front_matter(post.read_text(encoding="utf-8"))
        if meta.get("category") != section:
            continue
        (kept if post.stem in keep else remove).append((post.stem, meta.get("title", post.stem)))
    missing = keep - {s for s, _ in kept}
    print(f"Section: {section}")
    print(f"Keeping {len(kept)} article(s):")
    for slug, title in kept:
        print(f"   KEEP    {title}   ({slug})")
    if missing:
        print(f"Warning: no article in '{section}' is named: {', '.join(sorted(missing))}")
        if mode == "delete":
            sys.exit("Nothing was deleted. Check the name of the article to keep and run again.")
    print(f"Removing {len(remove)} article(s):")
    for slug, title in remove:
        extras = [str(p.relative_to(ROOT)) for p in related_files(slug)]
        print(f"   REMOVE  {title}   ({slug})")
        for x in extras:
            print(f"             - {x}")
    if mode != "delete":
        print("\nPreview only: nothing was deleted. Run again with mode 'delete' to remove the articles above.")
        return
    if not remove:
        print("Nothing to remove.")
        return
    for slug, _ in remove:
        for p in related_files(slug):
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    git("add", "-A", "content/posts", "assets/images", "assets/files")
    git("commit", "-m", f"Clean up section '{section}': removed {len(remove)} article(s)")
    git("pull", "--rebase", "origin", "main")
    git("push", "origin", "main")
    print(f"\nRemoved {len(remove)} article(s). The website is being republished now.")


if __name__ == "__main__":
    main()
