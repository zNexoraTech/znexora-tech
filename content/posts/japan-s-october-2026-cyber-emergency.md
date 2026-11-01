---
title: Japan’s October 2026 Cyber Emergency
date: 2026-11-01
category: theory
summary: A record wave of ransomware, data theft and an exploited PHP flaw pushed Japan to declare a state of emergency in cyberspace. Here is what happened, and how to respond and prevent the next attack.
author: ZNexora Tech
drafted_by: upload
---

Japan’s autumn of 2026 will be remembered as the moment cyberattacks stopped being an IT problem and became a national one. In just five weeks, ransomware took down a university and a major cloud provider, dozens of companies disclosed data breaches, attackers exploited a critical PHP vulnerability before a patch existed, and a large internet group refused a $50 million ransom. This briefing explains the scale of the wave, how the attacks worked, the key incidents, and the steps that organisations should take now.

*Figures are as reported up to 28 October 2026. Many record counts are the maximum number possibly affected, not confirmed leaks, and investigations are ongoing.*

## A record year, then a national emergency

![Japan’s 2026 cyber emergency in numbers: 9 October emergency declaration, 500+ incidents, 495 organisations hit by one cloud ransomware attack, 123 ransomware cases in the first half of 2026](../../assets/images/japan-s-october-2026-cyber-emergency/img-1.jpg)

Four numbers set the scene:

- **500+ cyber incidents** in Japan in 2026, already a new annual record before November.
- **495 companies and local governments** affected by a single ransomware attack on one cloud provider, IDC Frontier.
- **123 ransomware cases** reported to police in the first half of 2026, the highest ever, most of them at small and medium-sized companies.
- **9 October:** the government declared a “state of emergency in cyberspace”.

The timing matters. Japan’s Active Cyber Defense Law took effect on 1 October 2026. It introduces mandatory incident reporting for 257 critical infrastructure operators and gives the government new powers to neutralise attacker infrastructure.

## Five weeks of disclosures

The wave unfolded quickly. TV Asahi counted more than 40 breach announcements in roughly a month.

![Timeline of five weeks of disclosures from 25 September to 27 October 2026](../../assets/images/japan-s-october-2026-cyber-emergency/img-2.jpg)

| **Date** | **Event** |
| --- | --- |
| 25 Sep | Times Car discloses about 6.6 million records; Tokyo Metro’s outsourced mail server is accessed |
| 2 Oct | Ransomware at Osaka Metropolitan University stops about 500 servers |
| 5 Oct | Yakiniku King (10.8 million records); Daiwa Securities hit through its vendor Scala Communications |
| 7 Oct | Ransomware at IDC Frontier’s cloud affects 495 companies and local governments |
| 9 Oct | Government declares a state of emergency in cyberspace |
| 17 Oct | First attempts to exploit the PHP2Shell flaws, before any patch exists |
| 21 Oct | PHP patch released; Japanese banks and agencies pause websites; data of 13,000 Saitama Police staff at risk |
| 26–27 Oct | GMO Internet Group FX breach; $50 million ransom refused |

## Six ways the attacks unfolded

![Six attack types: ransomware, data theft and extortion, supply chain, AI-accelerated, vulnerability exploits, accounts and settings](../../assets/images/japan-s-october-2026-cyber-emergency/img-3.jpg)

The incidents fall into six broad types:

- **Ransomware.** Attackers encrypted servers and, in this wave, often the backups too, then demanded payment.
- **Data theft and extortion.** Customer records were stolen with threats to leak them. This was the biggest driver of the October spike.
- **Supply chain.** A breach at a vendor or cloud provider reached every client that depended on it.
- **Vulnerability exploits.** Unpatched software was targeted, most notably through the PHP2Shell flaws.
- **Accounts and settings.** Hijacked accounts and misconfigured CMS or API settings opened other doors.
- **AI-accelerated attacks.** On 19 October, GMO Cybersecurity by IERAE linked infrastructure targeting about 20 Japanese companies to ARTEX, a Chinese-developed AI penetration-testing tool. No single attacker has been officially named.

## Key incidents

### Ransomware: one shared layer, hundreds of victims

**IDC Frontier (SoftBank’s cloud subsidiary).** At about 03:40 on 7 October, ransomware hit its IDCF Cloud East Japan Region 1, affecting 495 customer organisations at once. Customers such as JR East and Views Card then disclosed that up to about 6 million member records may have been exposed. IDC Frontier told customers that data in the affected zones would be difficult to recover and that they should restore from their own backups.

**Osaka Metropolitan University.** On 2 October, an outage spread across all five campuses. The attacker reached the shared virtualisation platform underneath many systems, about 500 servers stopped, and most backups were encrypted too.

**The lesson:** backups and recovery systems that live on the same layer as production fail together. If your backups depend on the layer that was attacked, you do not really have a backup.

![Why the backups failed: backups on the same virtualization or cloud layer were encrypted together with production; an isolated backup survives](../../assets/images/japan-s-october-2026-cyber-emergency/img-4.jpg)

### Data breaches: how the attackers got in

Where companies disclosed how attackers got in, the entry points were ordinary:

| **Entry point** | **Disclosed examples** |
| --- | --- |
| A vendor’s server | Scala Communications: Daiwa Securities (~110,000) and Citizen Watch (~100,000); Tokyo Metro’s mail vendor (~59,000) |
| API or CMS setting | Shueisha: a configuration error let an attacker create a high-privilege account through the API |
| Software vulnerability | GMO Research & AI (up to 948,000 records); Mr Max (up to 1.7 million members) |
| One compromised account | Nikkei: a single Microsoft 365 account sent about 9,000 phishing emails |
| Virtualisation or cloud | Osaka Metropolitan University; IDC Frontier and its customers |

Detection was equally worrying. In five of the seven cases where the discovery route is known, an outsider noticed first: a customer, a stranger, a platform provider or a vendor.

### PHP2Shell: exploited before the patch

PHP2Shell is the name given to two critical memory-safety flaws in PHP, **CVE-2026-109618** and **CVE-2026-109619**, which affect PHP 5.4 to 8.5 and allow remote code execution without authentication. Because PHP powers a large share of the world’s websites, the exposure is broad.

![PHP2Shell timeline: exploitation attempts on 17 October, four days before fixes on 21 October; alerts on 22 October; new flaw on 23 October](../../assets/images/japan-s-october-2026-cyber-emergency/img-5.jpg)

- **17 October:** first exploitation attempts observed, four days before a fix existed.
- **21 October:** fixes released in PHP 8.5.12, 8.4.27, 8.3.36 and 8.2.35. Japanese banks, restaurant chains and government sites paused online services as a precaution.
- **22 October:** JPCERT/CC and IPA issued alerts asking organisations both to patch and to check whether they had already been compromised.
- **23 October:** a separate session-handling flaw, CVE-2026-115560, was disclosed. It is not fixed by the 21 October releases.

### GMO Internet Group: the latest target

The most recent incident is still developing. Intruders got in through GMO’s Onamae.com Desktop Cloud service, a virtual desktop service used by retail FX traders, potentially exposing up to 26,739 servers. Five FX margin-trading services were breached and unauthorised trades were made, with accounts reached at more than 70 securities and FX firms.

The attackers demanded $50 million (about ¥7.9 billion). Early media reports cited $1 million, but GMO’s president disclosed the $50 million figure and said the company would not pay. GMO asked customers to scan their PCs, back up files, and unplug and power off their devices, and said it will reimburse trading losses and pay each affected client ¥5,000.

**Since then:** after GMO refused to pay, the attackers published what they claim is customer information on 27 October. GMO had also asked the government to apply the new Active Cyber Defense law, which would be its first use since the law took effect, and its president acknowledged in a blog post that in-house engineers had flagged security issues beforehand that were not fully addressed. GMO has not linked its breach to the PHP flaws.

## If you are affected: six steps now

![Six remediation steps: contain, patch, hunt, reset, restore, report](../../assets/images/japan-s-october-2026-cyber-emergency/img-6.jpg)

1. **Contain.** Isolate affected systems. If a provider tells you to disconnect, do it.
2. **Patch.** Upgrade PHP to the 21 October releases; temporary mitigations only block specific paths, so updating is the only real fix. For CVE-2026-115560, turn off session upload progress until a patch ships.
3. **Hunt.** Review logs back to 17 October for signs of compromise. Patching alone does not remove an attacker who is already in.
4. **Reset.** Rotate exposed credentials and enforce multi-factor authentication.
5. **Restore.** Recover from your own isolated backups, and preserve logs for forensics.
6. **Report.** Notify the police and the Personal Information Protection Commission.

## Prevention: close the doors these attacks used

Each control below maps to an entry point seen in this wave:

| **Control** | **Why it matters** |
| --- | --- |
| Patch VPNs and add MFA | Police data show VPN devices were the most common first entry point for ransomware |
| Keep an isolated backup and test it | Osaka and IDC Frontier lost backups that sat on the same layer as production |
| Inventory your vendors | Know who holds customer data and confirm deletion when contracts end; Yoshinoya’s data was taken from a recruiting platform it had stopped using |
| Alert on new admin accounts | Shueisha’s attacker created a high-privilege account through the API |
| Review sign-ins daily | Outsiders spotted most breaches before the victims did |
| Patch fast and watch JVN alerts | PHP2Shell was exploited before a fix existed |
| Write a response contact list | IT, cloud, forensics, police and the PPC, decided in advance |

## The takeaway

**None of these entry points were new. AI is changing the speed, not the method.**

Vendor servers, misconfigured APIs, unpatched software, single hijacked accounts and shared infrastructure are long-known weaknesses. What has changed is speed: AI tools help attackers find those weaknesses across many organisations at once, and attackers claimed that IDC Frontier’s encryption took only minutes, although that figure is unverified. Detection measured in days is now too slow. The basics, patching, MFA, isolated backups, vendor control and daily monitoring, still stop most of this wave.

## Sources

### Official advisories

- [JPCERT/CC alert JPCERT-AT-2026-0033 (PHP vulnerabilities)](https://www.jpcert.or.jp/at/2026/at260033.html)
- [IPA security alert on PHP2Shell (22 October 2026)](https://www.ipa.go.jp/security/security-alert/2026/alert20261022.html)
- [Japan Vulnerability Notes (JVN)](https://jvn.jp/)

### Analysis

- [CS2: Japan’s October 2026 breach wave](https://www.cybers2.com/blog/japan-breach-wave-october-2026.html)
- [UV Cyber: Japan’s cyber emergency and its ripple effects](https://www.uvcyber.com/resources/threat-advisories/threat-advisory-japans-cyber-emergency-and-its-ripple-effects)
- [Malware News / SOCRadar: Inside the October surge](https://malware.news/t/japan-data-breaches-2026-inside-the-october-surge/126558)
- [SOCRadar: PHP2Shell explained](https://socradar.io/blog/php2shell-cve-2026-109618-cve-2026-109619/)

### News

- [Bloomberg: Trading platform rocked by Japan hack, $50 million ransom](https://www.bloomberg.com/news/articles/2026-10-26/japan-s-katayama-vows-to-address-cyber-attack-on-fx-with-urgency)
- [News On Japan: GMO refuses to pay $50 million cyberattack ransom](https://newsonjapan.com/article/151147.php)
- [Finance Magnates: Hackers publish alleged GMO customer data](https://financemagnates.com/forex/hackers-publish-alleged-gmo-customer-data-as-broker-fxtf-shuts-out-overseas-logins)
- [Kyodo News (via Kumanichi): GMO requests Active Cyber Defense](https://kumanichi.com/articles/2050148)
- [News On Japan: Cyberattacks hit Japanese police and businesses](https://newsonjapan.com/article/151111.php)
- [The Next Web: Japan steps up cyber warnings as data leaks hit millions](https://thenextweb.com/news/japan-cyberattacks-warning-data-leaks)
- [Anadolu Agency: Japan suspends websites over critical PHP vulnerabilities](https://www.aa.com.tr/en/asia-pacific/japan-suspends-several-websites-over-critical-php-security-vulnerabilities/4096314)
- [Tech Times: Japan declares first cyberspace emergency](https://www.techtimes.com/articles/328908/20261012/japan-declares-first-cyberspace-emergency-ai-turns-ransomware-carpet-bombing.htm)

## Slides

[Download the slides as PDF](../../assets/files/japan-s-october-2026-cyber-emergency.pdf)

![Slide 1](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-1.jpg)

![Slide 2](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-2.jpg)

![Slide 3](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-3.jpg)

![Slide 4](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-4.jpg)

![Slide 5](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-5.jpg)

![Slide 6](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-6.jpg)

![Slide 7](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-7.jpg)

![Slide 8](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-8.jpg)

![Slide 9](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-9.jpg)

![Slide 10](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-10.jpg)

![Slide 11](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-11.jpg)

![Slide 12](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-12.jpg)

![Slide 13](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-13.jpg)

![Slide 14](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-14.jpg)
