"""Drafts one theory or practical article from topics.json each week.

With an AI key the robot writes a full first draft for you to check.
Without one it opens an outline for you to fill in (marked draft, so it stays hidden until you finish)."""
import argparse

from common import (PR_FOOTER, ROOT, automation, commit_state, dump_front_matter, load_json,
                    save_draft, save_json, slugify, today)
from writer import ai_json

SECTIONS = {
    "theory": ["Overview", "Key ideas", "How it works", "A real-world example", "Common misconceptions", "Key takeaways"],
    "practical": ["What you will achieve", "Before you start", "Steps", "Check that it worked", "Troubleshooting",
                  "Security notes"],
}
GUIDANCE = {
    "theory": "Explain the concept clearly with an everyday analogy and one realistic example. 700-1000 words.",
    "practical": ("A hands-on defensive guide for system administrators. Under 'Steps' use numbered steps with "
                  "commands in fenced code blocks, and explain what each command does. Include how to undo risky "
                  "changes. Assume a test machine first. 700-1100 words."),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    site, cfg, model = automation("articles")
    if not cfg.get("enabled", True):
        return print("Article drafts are turned off in site.json.")

    import json
    topics = json.loads((ROOT / "topics.json").read_text(encoding="utf-8"))
    done = set(load_json("topics_done.json", []))
    topic = next((t for t in topics if t["title"] not in done), None)
    if not topic:
        return print("All topics in topics.json are used. Add new ones to keep weekly articles coming.")
    kind = topic.get("type", "theory") if topic.get("type") in SECTIONS else "theory"
    print(f"Article: {topic['title']} ({kind})")

    sections = SECTIONS[kind]
    ai = ai_json(
        f"Write a {kind} cybersecurity article titled: {topic['title']}. Level: {topic.get('level', 'Beginner')}. "
        f"{GUIDANCE[kind]} Notes from the editor: {topic.get('notes', 'none')}. "
        "Do not include links. Return "
        f'{{"summary": "one sentence", "body": "markdown using exactly these ## sections in order: {", ".join(sections)}"}}',
        f"Topic: {topic['title']}", model, 4000)

    meta = {"title": topic["title"], "date": today().isoformat(), "category": kind,
            "summary": (ai or {}).get("summary") or "Write a one-sentence summary here.",
            "level": topic.get("level", "Beginner"), "drafted_by": "ai" if ai else "outline"}
    if ai:
        body = ai["body"]
        checks = ("- [ ] Facts are correct\n- [ ] Every command was tested on a test machine\n"
                  "- [ ] Add your own experience or opinion somewhere (Google rewards original insight)")
    else:
        meta["draft"] = "true"
        body = "\n\n".join(f"## {s}\n\nWrite this section." for s in sections)
        checks = ("This is an outline because no AI key is set. Fill in each section in **Files changed > Edit file**, "
                  "write the summary, and change `draft: true` to `draft: false` before merging.")
    pr = f"This week's {kind} article.\n\n{checks}\n{PR_FOOTER}"
    if save_draft(slugify(topic["title"]), topic["title"], dump_front_matter(meta, body), pr, args.dry_run):
        done.add(topic["title"])
    save_json("topics_done.json", sorted(done))
    commit_state("Robot memory: article topics", args.dry_run)


if __name__ == "__main__":
    main()
