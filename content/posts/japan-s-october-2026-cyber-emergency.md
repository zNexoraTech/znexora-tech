---
title: Japan’s October 2026 Cyber Emergency
date: 2026-11-01
category: theory
summary: THREAT BRIEFING · 27 OCTOBER 2026 Attack types, what happened, how to remediate, and how to prevent the next one
author: ZNexora Tech
drafted_by: upload
---

[Download the slides as PDF](../../assets/files/japan-s-october-2026-cyber-emergency.pdf)

## A record year, then a national emergency

![A record year, then a national emergency](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-2.jpg)

- THE SCALE
- 500+
- cyber incidents in Japan in 2026, a new annual record
- 495
- companies and local governments hit by one cloud ransomware attack
- 123
- ransomware cases reported to police in the first half of 2026, a record
- Oct 9
- government declares a “state of emergency in cyberspace”
- Japan’s Active Cyber Defense Law took effect on 1 October: mandatory incident reporting for 257 critical infrastructure operators and new powers to neutralize attacker infrastructure.
- Sources: UV Cyber threat advisory; CS2 / National Police Agency; The Next Web

## Five weeks of disclosures

![Five weeks of disclosures](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-3.jpg)

- WHAT HAPPENED
- Sources: CS2 breach-wave analysis; SOCRadar; News On Japan; Bloomberg

## Six ways the attacks unfolded

![Six ways the attacks unfolded](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-4.jpg)

- ATTACK TYPES
- Ransomware
- Encrypts servers and backups, then demands payment
- Data theft and extortion
- Customer records stolen, with threats to leak them
- Supply chain
- A vendor or cloud breach reaches all of its clients
- Vulnerability exploits
- Unpatched software, such as the PHP2Shell flaws
- Accounts and settings
- Hijacked accounts and CMS or API misconfiguration
- AI-accelerated
- An AI pen-testing tool, ARTEX, linked to attacks on ~20 firms
- Sources: CS2; Malware News / SOCRadar; GMO Cybersecurity by IERAE (19 Oct)

## One shared layer, hundreds of victims

![One shared layer, hundreds of victims](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-5.jpg)

- KEY INCIDENTS · RANSOMWARE
- IDC Frontier (SoftBank cloud)
- 7 Oct, about 03:40: ransomware hits IDCF Cloud East Japan Region 1
- 495 companies and local governments affected
- JR East and Views Card: up to ~6M member records possibly exposed
- Customers told to restore from their own backups
- Osaka Metropolitan University
- 2 Oct: outage across all five campuses
- Attacker reached the shared virtualization platform
- About 500 servers stopped
- Most backups were encrypted too
- Lesson: backups and recovery that live on the same layer fail together.
- Sources: CS2 breach-wave analysis (citing TECH+, NHK, IDC Frontier reports); UV Cyber

## How the attackers got in

![How the attackers got in](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-6.jpg)

- KEY INCIDENTS · DATA BREACHES
- In 5 of 7 cases with a known discovery route, an outsider noticed first.
- Source: CS2, “Japan’s October 2026 breach wave” (14 Oct 2026). Counts are maximums possibly affected.

## PHP2Shell: exploited before the patch

![PHP2Shell: exploited before the patch](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-7.jpg)

- KEY INCIDENTS · VULNERABILITY
- CVE-2026-109618
- CVE-2026-109619
- Memory-safety flaws in PHP 5.4–8.5 that allow remote code execution without authentication
- Japanese banks, restaurant chains and government sites paused online services as a precaution
- 17 Oct
- First exploitation attempts observed
- 21 Oct
- Fixes: PHP 8.5.12, 8.4.27, 8.3.36, 8.2.35
- 22 Oct
- JPCERT/CC and IPA issue alerts; patch and check for compromise
- 23 Oct
- Separate flaw CVE-2026-115560 disclosed, not fixed by the 21 Oct releases
- Sources: JPCERT-AT-2026-0033; IPA alert 20261022; SOCRadar; Anadolu Agency; News On Japan

## GMO Internet Group: the latest target

![GMO Internet Group: the latest target](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-8.jpg)

- KEY INCIDENTS · EXTORTION
- $50M
- ransom demanded (about ¥7.9B) — refused by GMO
- Early reports cited $1M; GMO’s president disclosed $50M
- Entry: Onamae.com Desktop Cloud service; up to 26,739 servers potentially exposed
- Impact: five FX margin-trading services breached, unauthorized trades; accounts at 70+ securities and FX firms reached
- Threat: attackers claimed to publish customer data after the deadline
- Response: customers told to scan PCs, back up files, unplug and power off; losses reimbursed plus ¥5,000 per client
- Sources: Bloomberg (26 Oct); News On Japan; BigGo Finance; CoinCentral; TokyoReporter

## If you are affected: six steps now

![If you are affected: six steps now](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-9.jpg)

- REMEDIATION
- 01
- Contain
- Isolate affected systems; follow vendor instructions to disconnect
- 02
- Patch
- Upgrade PHP now; for CVE-2026-115560, turn off session upload progress until fixed
- 03
- Hunt
- Check logs back to 17 Oct for signs of compromise, not just patch
- 04
- Reset
- Rotate exposed credentials and enforce multi-factor authentication
- 05
- Restore
- Recover from your own isolated backups; preserve logs for forensics
- 06
- Report
- Notify police and the Personal Information Protection Commission
- Sources: JPCERT-AT-2026-0033; IPA alert 20261022; IDC Frontier guidance via CS2; GMO customer notice

## Close the doors these attacks used

![Close the doors these attacks used](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-10.jpg)

- PREVENTION
- Sources: CS2 checklist (citing National Police Agency data); JPCERT/CC; JVN

## None of these entry points were new. AI is changing the speed, not the method.

![None of these entry points were new. AI is changing the speed, not the method.](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-11.jpg)

- TAKEAWAY
- The basics — patching, MFA, isolated backups, vendor control and daily monitoring — still stop most of this wave.

## Official advisories and analysis

![Official advisories and analysis](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-12.jpg)

- REFERENCES · 1 OF 3
- Official advisories
- JPCERT/CC alert JPCERT-AT-2026-0033 (PHP vulnerabilities)
- https://www.jpcert.or.jp/at/2026/at260033.html
- IPA security alert on PHP2Shell (22 Oct 2026)
- https://www.ipa.go.jp/security/security-alert/2026/alert20261022.html
- Japan Vulnerability Notes (JVNVU#99905564)
- https://jvn.jp/
- Analysis
- CS2: Japan’s October 2026 breach wave
- https://www.cybers2.com/blog/japan-breach-wave-october-2026.html
- UV Cyber: Japan’s cyber emergency and its ripple effects
- https://www.uvcyber.com/resources/threat-advisories/threat-advisory-japans-cyber-emergency-and-its-ripple-effects
- Malware News / SOCRadar: Inside the October surge
- https://malware.news/t/japan-data-breaches-2026-inside-the-october-surge/126558
- SOCRadar: PHP2Shell explained
- https://socradar.io/blog/php2shell-cve-2026-109618-cve-2026-109619/

## News: the GMO Internet Group attack

![News: the GMO Internet Group attack](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-13.jpg)

- REFERENCES · 2 OF 3
- Bloomberg: Trading platform rocked by Japan hack, $50 million ransom (26 Oct)
- https://www.bloomberg.com/news/articles/2026-10-26/japan-s-katayama-vows-to-address-cyber-attack-on-fx-with-urgency
- News On Japan: GMO refuses to pay $50 million cyberattack ransom
- https://newsonjapan.com/article/151147.php
- BigGo Finance: GMO refuses $50 million ransom, will repay FX losses
- https://finance.biggo.com/news/b79624a0-b5ec-4c7d-bc8b-9dcb4f00ed22
- CoinCentral: GMO warns users to unplug computers
- https://coincentral.com/gmo-internet-group-warns-users-to-unplug-computers-as-hackers-threaten-ransomware-attack
- TokyoReporter: GMO refuses ransom demand after cyberattack
- https://www.tokyoreporter.com/japan-news/tech-giant-gmo-refuses-1m-ransom-demand-from-hacker-syndicate-after-massive-cyberattack/

## News: the wider wave and PHP2Shell

![News: the wider wave and PHP2Shell](../../assets/images/japan-s-october-2026-cyber-emergency/slides/slide-14.jpg)

- REFERENCES · 3 OF 3
- News On Japan: Cyberattacks hit Japanese police and businesses
- https://newsonjapan.com/article/151111.php
- The Next Web: Japan steps up cyber warnings as data leaks hit millions
- https://thenextweb.com/news/japan-cyberattacks-warning-data-leaks
- Anadolu Agency: Japan suspends websites over critical PHP vulnerabilities
- https://www.aa.com.tr/en/asia-pacific/japan-suspends-several-websites-over-critical-php-security-vulnerabilities/4096314
- Tech Times: Japan declares first cyberspace emergency
- https://www.techtimes.com/articles/328908/20261012/japan-declares-first-cyberspace-emergency-ai-turns-ransomware-carpet-bombing.htm
- Figures as reported up to 27 Oct 2026; many are maximums possibly affected, not confirmed leaks.
