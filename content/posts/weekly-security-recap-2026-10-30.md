---
title: Weekly security recap: 24 Oct 2026 to 30 Oct 2026
date: 2026-10-31
category: weekly-recap
summary: Security news, exploited vulnerabilities, ransomware and defacement activity for 24 Oct 2026 to 30 Oct 2026.
drafted_by: template
---

This week we tracked 78 security stories, 10 newly exploited vulnerabilities and 98 ransomware leak-site claims from 24 groups. Here is what defenders should know.

## At a glance

| This week | Count |
|---|---|
| Security stories followed | 78 |
| Newly exploited vulnerabilities (CISA) | 10 |
| Ransomware leak-site claims | 98 |
| Active ransomware groups | 24 |
| Web defacement reports | 0 |

## Top security news

- [Critical Linux kernel flaw allows remote root attacks on MPTCP servers](https://www.bleepingcomputer.com/news/security/critical-linux-kernel-flaw-allows-remote-root-attacks-on-mptcp-servers/) (BleepingComputer)
- [Florida warns that 4.9 million people had Social Security numbers leaked in financial aid site breach](https://therecord.media/florida-warns-5-million-affected-financial-aid-site-breach) (The Record)
- [TeamViewer Flaw Lets Remote Computers Attack Users Who Connect to Control Them](https://thehackernews.com/2026/10/teamviewer-flaw-lets-remote-computers.html) (The Hacker News)
- [In Other News: Anthropic Breach Dispute, UEFI Flaw Hits Most Servers, Cloudflare AI Data Leak](https://www.securityweek.com/in-other-news-anthropic-breach-dispute-uefi-flaw-hits-most-servers-cloudflare-ai-data-leak/) (SecurityWeek)
- [WordPress RCE Flaw Draws Nearly 63,000 Attack Attempts in Just 24 Hours](https://thehackernews.com/2026/10/wordpress-rce-flaw-draws-nearly-63000.html) (The Hacker News)
- [SS7 and Diameter Attacks: How Signaling Flaws Expose Your Phone](https://www.bleepingcomputer.com/news/security/ss7-and-diameter-attacks-how-signaling-flaws-expose-your-phone/) (BleepingComputer)
- [CISA says max severity GitLab flaw now exploited in the wild](https://www.bleepingcomputer.com/news/security/hackers-now-exploiting-max-severity-gitlab-flaw-in-attacks/) (BleepingComputer)
- [Fresh WordPress Vulnerability in Attackers’ Crosshairs](https://www.securityweek.com/fresh-wordpress-vulnerability-in-attackers-crosshairs/) (SecurityWeek)
- [Drupal Commerce Core Vulnerability Exploited Against Online Stores](https://www.securityweek.com/drupal-commerce-core-vulnerability-exploited-against-online-stores/) (SecurityWeek)
- [Hackers Actively Exploit Highly Critical Drupal Commerce Core Authorization Bypass Flaw](https://thehackernews.com/2026/10/hackers-actively-exploit-highly.html) (The Hacker News)

## Newly exploited vulnerabilities

- **CVE-2026-118527**, Ivanti Connect Secure: Ivanti Connect Secure Generation of Predictable Numbers or Identifiers Vulnerability ([details](../cve-2026-118527-ivanti-connect-secure/))
- **CVE-2026-111357**, Ivanti Connect Secure: Ivanti Connect Secure Missing Authentication for Critical Function Vulnerability ([details](../cve-2026-111357-ivanti-connect-secure/))
- **CVE-2026-97229**, GitLab Community Edition and Enterprise Edition: GitLab Community Edition and Enterprise Edition Integer Overflow or Wraparound Vulnerability ([details](../cve-2026-97229-gitlab-community-edition-and-enterprise-edition/))
- **CVE-2026-76418**, Cisco Secure Firewall ASA Software and Cisco Secure FTD Software: Cisco Secure Firewall ASA Software and Cisco Secure FTD Software Unchecked Return Value to NULL Pointer Dereference Vulnerability ([details](../cve-2026-76418-cisco-secure-firewall-asa-software-and-cisco-secure-ftd-software/))
- **CVE-2026-41709**, Broadcom VMware ESX: Broadcom VMWare ESX Insufficient Logging Vulnerability ([details](../cve-2026-41709-broadcom-vmware-esx/))
- **CVE-2026-46300**, Linux Kernel: Linux Kernel Missing Initialization of a Variable Vulnerability ([details](../cve-2026-46300-linux-kernel/))
- **CVE-2026-48356**, Adobe Commerce and Magento: Adobe Commerce and Magento Unrestricted Upload of File with Dangerous Type Vulnerability ([details](../cve-2026-48356-adobe-commerce-and-magento/))
- **CVE-2026-111497**, Google Brotli: Google Brotli Unchecked Return Value Vulnerability ([details](../cve-2026-111497-google-brotli/))
- **CVE-2026-109618**, PHP Group PHP: PHP Memory Corruption Vulnerability ([details](../cve-2026-109618-php-group-php/))
- **CVE-2026-109619**, PHP Group PHP: PHP Stale Internal Request-State Vulnerability ([details](https://nvd.nist.gov/vuln/detail/CVE-2026-109619))

## Ransomware

Ransomware groups posted 98 new claims on their leak sites this week.

| Most active groups | Claims |
|---|---|
| qilin | 14 |
| SilentRansomGroup | 11 |
| genesis | 9 |
| play | 7 |
| akira | 6 |

| Most targeted sectors | Claims |
|---|---|
| Professional Services | 18 |
| Manufacturing | 13 |
| Healthcare | 10 |
| Technology | 10 |
| Financial Services | 8 |

| Most targeted countries | Claims |
|---|---|
| United States | 35 |
| Mexico | 6 |
| Germany | 4 |
| United Kingdom | 4 |
| Italy | 3 |

Claims come from criminal leak sites (collected by ransomware.live) and are often unverified, so we do not name the organisations listed.

**Ransomware in the news**

- [Bulletproof Host Virtualine Loses Its Domain to FBI Seizure](https://www.securityweek.com/bulletproof-host-virtualine-loses-its-domain-to-fbi-seizure/) (SecurityWeek)
- [Japan's GMO Offers $1 Million Bounty to Catch Hackers Behind FX Trading Cloud Breach](https://thehackernews.com/2026/10/japans-gmo-offers-1-million-bounty-to.html) (The Hacker News)

## Web defacement

Our sources did not report any notable website defacement incidents this week.

Defacement is often the visible sign of a deeper compromise. If one of your sites is defaced, take it offline, preserve logs, and look for the way in before restoring from a clean backup.

## What to do this week

- Patch the newly exploited vulnerabilities listed above, starting with internet-facing systems.
- Check that backups are recent, offline or immutable, and that you have tested a restore.
- Confirm multi-factor authentication is on for remote access, email and admin accounts.
- Monitor your public websites for unexpected changes to pages and files.

## Sources

- [CISA Known Exploited Vulnerabilities catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [ransomware.live](https://www.ransomware.live) for leak-site statistics
- News links above go to each original report
