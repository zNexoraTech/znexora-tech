---
title: Japan’s October 2026 Cyber Emergency
date: 2026-11-01
category: theory
summary: THREAT BRIEFING · 27 OCTOBER 2026 Attack types, what happened, how to remediate, and how to prevent the next one
author: ZNexora Tech
drafted_by: upload
---

## Key points

### A record year, then a national emergency
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

Four numbers set the scene. Japan passed 500 cyber incidents this year, already a record before November. A single ransomware attack on one cloud provider, IDC Frontier, affected 495 organisations at once. Police counted 123 ransomware cases in just the first half of the year, the highest ever, and most of them hit small and medium companies. On October 9 the National Cybersecurity Strategy Headquarters declared a state of emergency in cyberspace. The timing matters: the Active Cyber Defense Law came into force on October 1, adding mandatory reporting for critical infrastructure and allowing the government to take steps to neutralize attackers’ tools.

### Five weeks of disclosures
- WHAT HAPPENED
- Sources: CS2 breach-wave analysis; SOCRadar; News On Japan; Bloomberg

Here is the sequence. Late September brought large breaches at Times Car and an outsourced vendor of Tokyo Metro. In early October, ransomware took down Osaka Metropolitan University and then IDC Frontier’s cloud, which rippled out to nearly 500 customers. The government declared the emergency on October 9. Then the focus shifted to a critical PHP vulnerability that attackers began probing on October 17, four days before a fix existed. Most recently, GMO Internet Group disclosed a breach of its FX trading servers and refused a 50 million dollar ransom. TV Asahi counted more than 40 breach announcements in roughly a month.

### Six ways the attacks unfolded
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

The incidents fall into six broad types. Ransomware encrypts systems, and in this wave it often reached the backups too. Data theft with extortion is the biggest driver of the October spike. Supply-chain attacks hit a vendor or a cloud provider and reach everyone who depends on it. Vulnerability exploitation, most notably PHP2Shell, targets unpatched software. Hijacked accounts and misconfigured CMS or API settings opened other doors. And there is a new accelerant: on October 19, GMO Cybersecurity by IERAE linked infrastructure targeting about 20 Japanese companies to ARTEX, a Chinese-developed AI penetration-testing tool. No single attacker has been officially named.

### One shared layer, hundreds of victims
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

The two ransomware cases show why this wave was so damaging. At IDC Frontier, SoftBank’s cloud subsidiary, ransomware hit one region early on October 7 and affected 495 customer organisations at once. Customers like JR East and Views Card then had to disclose possible exposure of millions of member records. IDC Frontier told customers that data in the affected zones would be difficult to recover and to use their own backups. At Osaka Metropolitan University, the attacker reached the virtualization platform underneath many systems, about 500 servers went down, and most backups were encrypted. The common lesson: if your backups depend on the same layer that failed, you don’t really have a backup.

### How the attackers got in
- KEY INCIDENTS · DATA BREACHES
- In 5 of 7 cases with a known discovery route, an outsider noticed first.
- Source: CS2, “Japan’s October 2026 breach wave” (14 Oct 2026). Counts are maximums possibly affected.

Where companies disclosed how attackers got in, the answers were ordinary. A vendor’s server: one overnight intrusion at Scala Communications exposed customers of Daiwa Securities and Citizen Watch. Configuration: Shueisha’s CMS error let an attacker create a high-privilege account and pull data through the API. Software vulnerabilities at GMO Research and AI and Mr Max. A single hijacked Microsoft 365 account at Nikkei. And the virtualization or cloud layer, as we just saw. Equally worrying is detection: in five of the seven cases where we know how the breach was found, the first signal came from outside — a customer, a stranger, a platform provider or a vendor.

### PHP2Shell: exploited before the patch
- KEY INCIDENTS · VULNERABILITY
- CVE-2026-109618
- CVE-2026-109619
- Memory-safety flaws in PHP 5.4–8.5 that allow  remote code execution without authentication
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

PHP2Shell is the name for two critical PHP flaws that affect versions 5.4 through 8.5 and allow an unauthenticated attacker to run code on the web server. PHP is used by a large share of the world’s websites, so this is broad exposure. Exploitation attempts were seen on October 17, four days before PHP shipped fixes on October 21. JPCERT/CC and IPA issued alerts the next day, asking organisations both to patch and to check whether they had already been compromised. On October 23, PHP disclosed a separate session-handling flaw, CVE-2026-115560, which the October 21 releases do not fix. Many Japanese organisations, including banks and government agencies, temporarily took sites offline.

### GMO Internet Group: the latest target
- KEY INCIDENTS · EXTORTION
- $50M
- ransom demanded (about ¥7.9B) — refused by GMO
- Early reports cited $1M; GMO’s president disclosed $50M
- Entry:  Onamae.com Desktop Cloud service; up to 26,739 servers potentially exposed
- Impact:  five FX margin-trading services breached, unauthorized trades; accounts at 70+ securities and FX firms reached
- Threat:  attackers claimed to publish customer data after the deadline
- Response:  customers told to scan PCs, back up files, unplug and power off; losses reimbursed plus ¥5,000 per client
- Sources: Bloomberg (26 Oct); News On Japan; BigGo Finance; CoinCentral; TokyoReporter

The most recent incident, still developing as of October 27, is GMO Internet Group. Intruders got in through its Onamae.com Desktop Cloud service, potentially exposing more than 26,000 servers. Five FX margin-trading services were breached and unauthorized trades were made, reaching accounts at more than 70 securities and FX firms. The attackers demanded 50 million dollars; some early media reports said 1 million, but GMO’s president disclosed the 50 million figure and said the company will not pay. After the deadline, the attackers claimed to publish customer information. GMO asked customers to scan their PCs, back up files, and unplug their devices, and it will reimburse trading losses and pay each client 5,000 yen.

### If you are affected: six steps now
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

If your organisation is affected, these are the immediate steps. First, contain: isolate affected systems, and if a provider like GMO tells you to disconnect, do it. Second, patch: upgrade PHP to the October 21 releases; the PHP Group says its temporary mitigations only block specific paths and updating is the only real fix. For the newer flaw, CVE-2026-115560, disable session upload progress until a patch ships. Third, hunt: JPCERT/CC asks organisations to check whether they were already compromised, so review logs back to October 17. Fourth, rotate exposed credentials and require MFA. Fifth, restore from backups you control, as IDC Frontier advised, while preserving logs. Finally, report to the police and the Personal Information Protection Commission.

### Close the doors these attacks used
- PREVENTION
- Sources: CS2 checklist (citing National Police Agency data); JPCERT/CC; JVN

For prevention, each control maps to an entry point we saw. Patch or replace VPN appliances and put MFA in front of them; police data show VPNs were the most common first way in for ransomware. Keep at least one backup that your IT provider, hypervisor credentials and cloud provider cannot reach, and actually test a restore. List every vendor that holds your customer data, and get written confirmation of deletion when you leave one — Yoshinoya’s data was taken from a recruiting platform it had stopped using. Alert on new privileged accounts. Review Microsoft 365 or Google Workspace sign-ins every day. Patch quickly and follow JVN and JPCERT alerts. And decide in advance who you will call.

### None of these entry points were new. AI is changing the speed, not the method.
- TAKEAWAY
- The basics — patching, MFA, isolated backups, vendor control and daily monitoring — still stop most of this wave.

If there is one message to take away: none of the ways in were new. Vendor servers, misconfigured APIs, unpatched software, single hijacked accounts and shared infrastructure are long-known weaknesses. What has changed is speed — AI tools help attackers find those weaknesses across many organisations at once, and attackers claimed IDC Frontier’s encryption took only minutes, though that figure is unverified. So detection measured in days is too slow, and the fundamentals matter more than ever. With that, I’m happy to take questions.

### Official advisories and analysis
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

The full links to every source are on this and the next two slides. The official advisories from JPCERT/CC and IPA are the best place to check for updates on the PHP vulnerabilities. Remember that investigations are ongoing and many record counts are maximums that may be affected, not confirmed leaks.

### News: the GMO Internet Group attack
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

These are the news sources for the GMO Internet Group incident. Note that early reports, such as TokyoReporter’s, cited a 1 million dollar demand, while GMO’s president later disclosed the 50 million dollar figure.

### News: the wider wave and PHP2Shell
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

These are the remaining news sources, covering the wider wave of attacks, the government’s warnings and the PHP2Shell shutdowns.

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
