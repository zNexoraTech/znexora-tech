"""Drafts briefings on vulnerabilities that attackers are actively exploiting (CISA KEV)."""
import argparse
import datetime as dt
import os
import time

from common import (POSTS_DIR, PR_FOOTER, automation, commit_state, dump_front_matter,
                    existing_post_meta, http_json, load_json, save_draft, save_json,
                    severity_from_score, slugify, today)
from writer import ai_json

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={}"


def nvd_details(cve):
    headers = {"apiKey": os.environ["NVD_API_KEY"]} if os.environ.get("NVD_API_KEY") else {}
    try:
        vulns = http_json(NVD_URL.format(cve), headers=headers).get("vulnerabilities") or []
    except Exception as exc:
        print(f"  NVD lookup failed ({exc}); continuing without it.")
        return {}
    if not vulns:
        return {}
    c = vulns[0].get("cve", {})
    out = {
        "nvd_description": next((d["value"] for d in c.get("descriptions", []) if d.get("lang") == "en"), ""),
        "references": [r["url"] for r in c.get("references", []) if r.get("url")][:5],
    }
    for key in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30"):
        entries = c.get("metrics", {}).get(key)
        if entries:
            cvss = next((m for m in entries if m.get("type") == "Primary"), entries[0]).get("cvssData", {})
            out.update(score=cvss.get("baseScore"), vector=cvss.get("vectorString", ""))
            break
    return out


def template_body(item):
    score = item.get("score")
    ransomware = (item.get("ransomware") or "").lower() == "known"
    return f"""## What happened

{item.get('short_description') or item.get('nvd_description') or 'Details have not been published yet.'}

CISA added {item['cve']} to its Known Exploited Vulnerabilities catalog on {item.get('date_added')}, which means there is evidence of real-world attacks.

## Who is affected

Organisations running {item['vendor']} {item['product']}. Check the vendor advisory in the sources for the exact affected versions.

## Why it matters

{f"It has a CVSS score of {score}." if score else "A CVSS score has not been published yet."} Exploitation is already happening, so exposed systems are at immediate risk.{" CISA reports use in ransomware campaigns." if ransomware else ""}

## What to do now

{item.get('required_action') or 'Apply the vendor fix as soon as it is available.'}

Find every instance of {item['product']} in your environment, patch internet-facing systems first, and review logs for signs of compromise."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    site, cfg, model = automation("exploited_vulnerabilities")
    if not cfg.get("enabled", True):
        return print("Exploited-vulnerability drafts are turned off in site.json.")

    seen = set(load_json("seen_cves.json", []))
    seen |= {m["cve"] for m in existing_post_meta() if m.get("cve")}
    kev = http_json(KEV_URL)
    save_json("kev_week.json", [v for v in kev.get("vulnerabilities", [])
                                if dt.date.fromisoformat(v["dateAdded"]) >= today() - dt.timedelta(days=8)])
    cutoff = today() - dt.timedelta(days=int(cfg.get("lookback_days", 7)))
    new = sorted([v for v in kev.get("vulnerabilities", []) if v["cveID"] not in seen
                  and dt.date.fromisoformat(v["dateAdded"]) >= cutoff], key=lambda v: v["dateAdded"], reverse=True)
    print(f"Exploited vulnerabilities: {len(new)} new, drafting up to {cfg.get('max_drafts_per_run', 3)}.")

    for i, v in enumerate(new[: int(cfg.get("max_drafts_per_run", 3))]):
        if i:
            time.sleep(1 if os.environ.get("NVD_API_KEY") else 7)
        item = {"cve": v["cveID"], "vendor": v.get("vendorProject", ""), "product": v.get("product", ""),
                "name": v.get("vulnerabilityName", ""), "short_description": v.get("shortDescription", ""),
                "required_action": v.get("requiredAction", ""), "date_added": v.get("dateAdded", ""),
                "ransomware": v.get("knownRansomwareCampaignUse", ""),
                "notes": [u.strip() for u in v.get("notes", "").split(";") if u.strip().startswith("http")]}
        item.update(nvd_details(item["cve"]))
        print(f"- {item['cve']}")
        facts = "\n".join(f"{k}: {item.get(k) or 'not published'}" for k in
                          ["cve", "vendor", "product", "name", "short_description", "nvd_description",
                           "score", "vector", "date_added", "ransomware", "required_action"])
        ai = ai_json("Write a 250-450 word briefing about this actively exploited vulnerability. Return "
                     '{"summary": "one sentence under 30 words", "body": "markdown with exactly these sections: '
                     '## What happened, ## Who is affected, ## Why it matters, ## What to do now"}', facts, model)
        summary = (ai or {}).get("summary") or f"{item['vendor']} {item['product']} has a vulnerability that attackers are actively exploiting."
        body = (ai or {}).get("body") or template_body(item)
        links = ["- [CISA Known Exploited Vulnerabilities catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)",
                 f"- [NVD entry for {item['cve']}](https://nvd.nist.gov/vuln/detail/{item['cve']})"]
        links += [f"- <{u}>" for u in (item["notes"] + item.get("references", []))[:5]]
        title = f"{item['cve']}: {item['name'] or item['vendor'] + ' ' + item['product'] + ' vulnerability'}"
        meta = {"title": title, "date": today().isoformat(), "category": "exploited-vulnerabilities",
                "summary": summary, "cve": item["cve"], "vendor": item["vendor"], "product": item["product"],
                "score": item.get("score") or "", "severity": severity_from_score(item.get("score")),
                "ransomware": item["ransomware"], "drafted_by": "ai" if ai else "template"}
        slug = slugify(f"{item['cve']} {item['vendor']} {item['product']}")
        pr = (f"New exploited-vulnerability briefing ({'AI draft' if ai else 'free template'}).\n\n"
              f"Check before approving:\n- [ ] CVE, vendor and product match the sources\n- [ ] Nothing is invented\n\n"
              f"Source: https://nvd.nist.gov/vuln/detail/{item['cve']}\n{PR_FOOTER}")
        if save_draft(slug, title, dump_front_matter(meta, body + "\n\n## Sources\n\n" + "\n".join(links)), pr, args.dry_run):
            seen.add(item["cve"])

    save_json("seen_cves.json", sorted(seen))
    commit_state("Robot memory: exploited vulnerabilities", args.dry_run)


if __name__ == "__main__":
    main()
