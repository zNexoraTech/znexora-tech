"""Builds the weekly recap: top security news, newly exploited vulnerabilities,
ransomware activity and web defacement reports. Opens it as a draft for approval."""
import argparse
import collections
import datetime as dt

from common import (POSTS_DIR, PR_FOOTER, parse_front_matter, automation, commit_state, dump_front_matter,
                    load_json, nice_date, save_draft, today)
from writer import ai_json

COUNTRY = {"US": "United States", "GB": "United Kingdom", "UK": "United Kingdom", "DE": "Germany", "FR": "France",
           "IT": "Italy", "ES": "Spain", "CA": "Canada", "AU": "Australia", "JP": "Japan", "IN": "India",
           "BR": "Brazil", "MX": "Mexico", "NL": "Netherlands", "BE": "Belgium", "CH": "Switzerland",
           "SG": "Singapore", "KR": "South Korea", "TW": "Taiwan", "TH": "Thailand", "MY": "Malaysia",
           "ID": "Indonesia", "PH": "Philippines", "VN": "Vietnam", "AE": "United Arab Emirates", "SA": "Saudi Arabia",
           "IL": "Israel", "TR": "Turkey", "ZA": "South Africa", "AR": "Argentina", "CL": "Chile", "CO": "Colombia",
           "PE": "Peru", "AT": "Austria", "SE": "Sweden", "NO": "Norway", "DK": "Denmark", "PL": "Poland", "PT": "Portugal"}

DEFAULT_ACTIONS = """- Patch the newly exploited vulnerabilities listed above, starting with internet-facing systems.
- Check that backups are recent, offline or immutable, and that you have tested a restore.
- Confirm multi-factor authentication is on for remote access, email and admin accounts.
- Monitor your public websites for unexpected changes to pages and files."""


def table(counter, label, n=5, names=None):
    if not counter:
        return ""
    rows = "\n".join(f"| {names.get(k, k) if names else k} | {v} |" for k, v in counter.most_common(n))
    return f"| {label} | Claims |\n|---|---|\n{rows}\n"


def headlines(items):
    return "\n".join(f"- [{s['title']}]({s['link']}) ({s['source']})" for s in items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    site, cfg, model = automation("weekly_recap")
    if not cfg.get("enabled", True):
        return print("Weekly recap is turned off in site.json.")

    end = today() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=6)
    in_week = lambda d: start.isoformat() <= (d or "")[:10] <= end.isoformat()

    news = sorted([s for s in load_json("news_log.json", {}).values() if in_week(s["date"])],
                  key=lambda s: s["date"], reverse=True)
    ransom_news = [s for s in news if "ransomware" in s["tags"]][:6]
    deface_news = [s for s in news if "defacement" in s["tags"]][:6]
    top_news = [s for s in news if s not in ransom_news and s not in deface_news]
    top_news.sort(key=lambda s: ("vulnerability" in s["tags"] or "breach" in s["tags"], s["date"]), reverse=True)
    picked, per_source = [], collections.Counter()
    for s in top_news:
        if s["title"].lower().startswith("cisa adds") or per_source[s["source"]] >= 3:
            continue  # already covered in the exploited section / keep sources balanced
        per_source[s["source"]] += 1
        picked.append(s)
    top_news = picked[: int(cfg.get("top_news", 10))]

    kev = [v for v in load_json("kev_week.json", []) if in_week(v.get("dateAdded"))]
    our_posts = {}
    for path in POSTS_DIR.glob("*.md"):
        cve = parse_front_matter(path.read_text(encoding="utf-8"))[0].get("cve")
        if cve:
            our_posts[cve] = path.stem
    claims = [c for c in load_json("ransomware_log.json", {}).values() if in_week(c["date"])]
    groups = collections.Counter(c["group"] for c in claims)
    sectors = collections.Counter(c["sector"] for c in claims if c["sector"] not in ("", "Not listed", "Not Found"))
    countries = collections.Counter(c["country"] for c in claims if c["country"] not in ("", "??"))

    label = f"{nice_date(start)} to {nice_date(end)}"
    print(f"Recap {label}: {len(news)} stories, {len(kev)} exploited CVEs, {len(claims)} ransomware claims.")

    kev_lines = []
    for v in kev:
        slug = our_posts.get(v["cveID"])
        target = f"../{slug}/" if slug else f"https://nvd.nist.gov/vuln/detail/{v['cveID']}"
        kev_lines.append(f"- **{v['cveID']}**, {v.get('vendorProject', '')} {v.get('product', '')}: "
                         f"{v.get('vulnerabilityName', '')} ([details]({target}))")

    material = (f"Week: {label}\nExploited vulnerabilities added: {len(kev)}\n"
                + "\n".join(f"- {v['cveID']} {v.get('vendorProject')} {v.get('product')}: {v.get('vulnerabilityName')}" for v in kev[:15])
                + f"\nRansomware leak-site claims: {len(claims)} from {len(groups)} groups. Top groups: {groups.most_common(5)}. "
                f"Top sectors: {sectors.most_common(5)}\nTop headlines:\n"
                + "\n".join(f"- {s['title']} ({s['source']})" for s in (top_news + ransom_news + deface_news)[:20]))
    ai = ai_json('Write the opening and the advice for a weekly security recap. Return {"summary": "one sentence", '
                 '"intro": "markdown, 80-150 words, the main themes of the week", '
                 '"actions": "markdown bullet list of 3-5 practical defensive actions based on this week"}',
                 material, model, 1200)

    intro = (ai or {}).get("intro") or (
        f"This week we tracked {len(news)} security stories, {len(kev)} newly exploited "
        f"{'vulnerability' if len(kev) == 1 else 'vulnerabilities'} and {len(claims)} ransomware leak-site claims "
        f"from {len(groups)} groups. Here is what defenders should know.")
    body = f"""{intro}

## At a glance

| This week | Count |
|---|---|
| Security stories followed | {len(news)} |
| Newly exploited vulnerabilities (CISA) | {len(kev)} |
| Ransomware leak-site claims | {len(claims)} |
| Active ransomware groups | {len(groups)} |
| Web defacement reports | {len(deface_news)} |

## Top security news

{headlines(top_news) or 'No major stories were collected this week.'}

## Newly exploited vulnerabilities

{chr(10).join(kev_lines) or 'CISA did not add any vulnerabilities to its exploited list this week.'}

## Ransomware

{f"Ransomware groups posted {len(claims)} new claims on their leak sites this week." if claims else "No ransomware statistics were collected this week."}

{table(groups, 'Most active groups')}
{table(sectors, 'Most targeted sectors')}
{table(countries, 'Most targeted countries', names=COUNTRY)}
Claims come from criminal leak sites (collected by ransomware.live) and are often unverified, so we do not name the organisations listed.

{('**Ransomware in the news**' + chr(10) + chr(10) + headlines(ransom_news)) if ransom_news else ''}

## Web defacement

{headlines(deface_news) if deface_news else 'Our sources did not report any notable website defacement incidents this week.'}

Defacement is often the visible sign of a deeper compromise. If one of your sites is defaced, take it offline, preserve logs, and look for the way in before restoring from a clean backup.

## What to do this week

{(ai or {}).get('actions') or DEFAULT_ACTIONS}

## Sources

- [CISA Known Exploited Vulnerabilities catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [ransomware.live](https://www.ransomware.live) for leak-site statistics
- News links above go to each original report
"""
    title = f"Weekly security recap: {label}"
    meta = {"title": title, "date": today().isoformat(), "category": "weekly-recap",
            "summary": (ai or {}).get("summary") or f"Security news, exploited vulnerabilities, ransomware and defacement activity for {label}.",
            "drafted_by": "ai" if ai else "template"}
    pr = (f"This week's recap is ready.\n\n- [ ] Headlines look relevant (delete any that are not)\n"
          f"- [ ] Numbers look reasonable\n{PR_FOOTER}")
    save_draft(f"weekly-security-recap-{end.isoformat()}", title, dump_front_matter(meta, body), pr, args.dry_run)
    commit_state("Robot memory: weekly recap", args.dry_run)


if __name__ == "__main__":
    main()
