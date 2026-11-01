---
title: Sensitive Information
date: 2026-11-01
category: theory
summary: OWASP TOP 10 FOR LLM APPLICATIONS · 2025 Disclosure LLM02:2025 — how AI apps leak data, and how to test for it
author: ZNexora Tech
drafted_by: upload
---

## Key points

### What counts as sensitive?
- THE RISK
- Personal data (PII)
- Names, addresses, IDs, phone numbers
- Financial details
- Card numbers, bank data, salaries
- Health records
- Diagnoses, prescriptions, claims
- Business data
- Contracts, strategy, unreleased plans
- Credentials
- API keys, passwords, tokens
- The model itself
- Training methods, source code, proprietary algorithms
- The risk: any of this appears in the model's output to someone who shouldn't see it.
- LLM02:2025 Sensitive Information Disclosure · 02
- !

[0:30–1:30] OWASP's list of sensitive information is broad: personal data, financial details, health records, confidential business data, security credentials and legal documents. For proprietary models, the training methods and source code themselves can be sensitive. The risk is simple to state: the model's output reveals data to someone who shouldn't see it. That leads to unauthorized data access, privacy violations and intellectual-property breaches. One important note from OWASP: telling the model in its system prompt "never reveal X" helps, but it's not a control. Those restrictions can be bypassed, for example with prompt injection from LLM01.

### Six paths from data to output
- HOW IT LEAKS
- 1 · Training data
- The model memorised data it was trained or fine-tuned on
- 2 · RAG and context
- Retrieval pulls documents the current user isn't allowed to see
- 3 · System prompt
- Keys, internal URLs or rules embedded in the instructions
- 4 · Sessions and memory
- One user's chat or memory bleeds into another's
- 5 · Tools and APIs
- Tool calls fetch full records; the model repeats them
- 6 · Logs and errors
- Prompts stored unmasked; stack traces reveal internals
- Each path is a place to test.
- LLM02:2025 Sensitive Information Disclosure · 03
- 1
- 2
- 3
- 4
- 5
- 6
- DATA
- CONTEXT
- MODEL
- OUTPUT

[1:30–2:30] Here's the mental model I use when testing. Sensitive data reaches the output through six main paths. One, training data: the model memorised something from training or fine-tuning. Two, RAG: the retrieval step pulls documents the current user shouldn't have access to. This is the most common one in real company apps. Three, the system prompt: developers sometimes put API keys or internal URLs right in the instructions. Four, sessions and memory: one user's conversation leaks into another's. Five, tools and APIs: the model calls an API that returns a full customer record, then repeats more than it should. Six, logs and errors: data stored unmasked, or debug errors exposing internals. Each of these is a separate thing to test, and that's what the next slides are about.

### Real leaks behind the OWASP scenarios
- IT HAS ALREADY HAPPENED
- INPUT SIDE
- Samsung, 2023
- Employees pasted confidential source code and meeting notes into ChatGPT. Once sent, the company lost control of that data.
- TRAINING DATA
- "Repeat a word forever"
- Researchers got ChatGPT to spill memorised training data, including personal contact details, by asking it to repeat one word endlessly.
- MODEL EXPOSURE
- Proof Pudding · CVE-2019-20634
- Exposed training data let attackers copy and invert an email-filter model, then craft emails that slipped past it.
- OWASP scenarios: another user's data in a response · filters bypassed by prompt injection · careless data in training
- LLM02:2025 Sensitive Information Disclosure · 04

[2:30–3:30] These aren't hypothetical. Three examples from OWASP's references. Samsung: engineers pasted confidential source code and meeting notes into ChatGPT. This is the input side of the risk: users giving sensitive data to an AI that may store or train on it. "Repeat a word forever": researchers asked ChatGPT to repeat a single word endlessly. Eventually it diverged and output memorised training data, including real people's contact details. Proof Pudding, CVE-2019-20634: training data from an email-filtering model was exposed, letting attackers rebuild the model and craft emails that bypassed it. The three OWASP scenarios at the bottom are what we'll test for: another user's data leaking, prompt injection bypassing filters, and sensitive data carelessly included in training.

### Seed fake secrets, then hunt for them
- HANDS-ON TESTING
- 01
- Data inventory
- What can the bot reach? RAG stores, tools, memory, logs, fine-tune data.
- 02
- Seed canaries
- Two test accounts, A and B, each with unique fake PII, e.g. CANARY-B-4471.
- 03
- Cross the line
- As A, try to get B's canary through chat, RAG, tools and memory.
- 04
- Inspect traffic
- Burp: do API and tool responses carry more than the UI shows?
- 05
- Measure
- Repeat 5–10 times; record rate, model and date.
- GOLDEN RULE
- Prove access with  your own fake data . If you hit real personal data, stop, screenshot minimally and report it. Never download it.
- LLM02:2025 Sensitive Information Disclosure · 05
- !

[3:30–4:30] Here's the practical method. The key idea: you seed fake secrets, then hunt for them. Step one, inventory: find out everything the bot can reach, including RAG stores, tools, memory features, logs and any fine-tuning data. Step two, seed canaries. Create two test accounts, A and B, and give each unique fake personal data, like a fake name and the string CANARY-B-4471. Step three, from account A, try every path to get B's canary: direct questions, RAG queries, tool calls, memory. Step four, inspect the traffic in Burp. Often the API sends far more than the screen shows. Step five, measure. LLMs are non-deterministic, so repeat each test and record the success rate. And the golden rule: prove access using your own fake data. If you stumble on real personal data, stop and report it; don't collect it.

### Access and context leaks
- TEST CASES · 1 OF 2
- LLM02:2025 Sensitive Information Disclosure · 06

[4:30–5:45] Five tests for access and context leaks. SID-01, the classic: as user A, ask about user B's order using B's seeded fake name. If anything of B's comes back, that's broken access control through the AI. SID-02, RAG permissions: a low-privilege user asks about an HR document you seeded with a canary. If the canary appears, retrieval ignores document permissions. This is one of the most common real findings. SID-03: ask the bot to repeat its instructions. You're looking for API keys, internal hostnames or business rules. SID-04: ask for something that triggers a tool call, then look at the raw tool response in Burp. Even if the chat only shows a name, the response might contain the full customer record. SID-05 only applies if you can influence fine-tuning data in a test environment: seed a unique string, then give the model its first half and see if it completes it.

### Session, filter and storage leaks
- TEST CASES · 2 OF 2
- LLM02:2025 Sensitive Information Disclosure · 07

[5:45–7:00] Five more, around sessions, filters and storage. SID-06: start a fresh session or switch accounts and ask what you talked about earlier. Memory features and caching bugs can leak another user's conversation. SID-07: send oversized input or malformed requests. This links back to Security Misconfiguration: detailed errors can reveal keys, model names or configuration. OWASP itself points to API8:2023 Security Misconfiguration here. SID-08: if the app redacts sensitive data, ask for it encoded in Base64, spelled letter by letter or split with spaces. Pattern-matching redaction often misses these. SID-09: submit fake PII and check whether it lands unmasked in logs or analytics tools, with the client's permission. SID-10: classic IDOR. Change the conversation ID in the request, or open a shared chat link while logged out.

### Look past the chat window
- TRAFFIC AND TOOLS
- In Burp, check for
- Hidden JSON fields: the UI shows 2, the API sends 20
- Tool and RAG results returned to the browser
- System prompt or keys sent client-side
- Guessable conversation and file IDs
- Streaming (SSE) chunks leaking before redaction
- Tools that help
- LLM02:2025 Sensitive Information Disclosure · 08
- REQUEST PATH  ·  FOLLOW THE DATA
- CHAT UI
- API
- RAG / TOOL
- MODEL
- Check raw responses, tool payloads and SSE chunks — not only rendered chat.

[7:00–8:00] The chat window is only half the picture. In Burp, look for hidden JSON fields: the screen shows a name and an order status, but the API returns the full customer record. Check whether tool or RAG results are sent to the browser, whether the system prompt or keys travel client-side, whether conversation IDs are guessable, and whether streamed chunks arrive before redaction is applied. That last one is easy to miss: some apps redact the final message but stream the raw text first. For automation, promptfoo has dedicated PII plugins for direct disclosure, session leakage and API or database access, plus a cross-session-leak plugin that simulates user A sharing a secret and user B trying to extract it. Microsoft Presidio can scan responses and logs for PII, and gitleaks or trufflehog find hard-coded keys in prompts and configs.

### OWASP controls, mapped to your findings
- PREVENTION
- Sanitize data
- Scrub or mask data before training; validate inputs
- Fixes SID-05, SID-09
- Strict access control
- Least privilege; restrict data sources; enforce permissions in retrieval
- Fixes SID-01, 02, 04
- Secure configuration
- Conceal the system preamble; no keys in prompts; generic errors
- Fixes SID-03, SID-07
- Tokenize and redact
- Pattern matching to redact before and after the model
- Fixes SID-08
- Privacy techniques
- Federated learning, differential privacy, homomorphic encryption
- Training-data risk
- Educate and be transparent
- Warn users; clear retention policy; training opt-out
- Samsung-style leaks
- LLM02:2025 Sensitive Information Disclosure · 09

[8:00–9:00] OWASP groups its mitigations into a few families, and here I've mapped each to the test cases we just saw, which is how I'd write recommendations in a report. Sanitization: scrub data before it goes into training, and validate inputs. Strict access controls: least privilege, limit data sources, and enforce document permissions at retrieval time, not in the prompt. Secure configuration: hide the system preamble, keep keys out of prompts, and return generic errors. Tokenization and redaction. Privacy-preserving techniques like federated learning, differential privacy and homomorphic encryption for training-data risk. And finally, user education and transparency: tell users what not to paste, and offer a training opt-out. The key message for developers: the system prompt is not an access-control layer.

### Rate by whose data, and how much
- SEVERITY AND TAKEAWAYS
- Critical
- Any user can pull other users' PII or credentials at scale
- High
- Cross-user or cross-role data, one record at a time
- Medium
- Internal config, model details or system prompt
- Low
- Verbose errors with no sensitive values
- Seed fake secrets · test all six leak paths · check the traffic, not just the chat ·  the system prompt is not access control
- Next: LLM03:2025 Supply Chain
- Source: genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure · MITRE ATLAS AML.T0024

[9:00–10:00] To rate severity, ask whose data leaked and how much. Critical: any user can pull other users' personal data or credentials at scale. High: cross-user or cross-role data, one record at a time. Medium: internal configuration, model details or the system prompt. Low: verbose errors with no sensitive values. Adjust for the data type; leaked health or payment data is always more serious. Four takeaways: seed your own fake secrets so you can prove leaks safely; test all six leak paths, not just the chat box; check the traffic, because the API often says more than the screen; and remember the system prompt is not access control. Next time: LLM03, Supply Chain. Thanks, and questions are welcome.

## Slides

[Download the slides as PDF](../../assets/files/sensitive-information.pdf)

![Slide 1](../../assets/images/sensitive-information/slides/slide-1.jpg)

![Slide 2](../../assets/images/sensitive-information/slides/slide-2.jpg)

![Slide 3](../../assets/images/sensitive-information/slides/slide-3.jpg)

![Slide 4](../../assets/images/sensitive-information/slides/slide-4.jpg)

![Slide 5](../../assets/images/sensitive-information/slides/slide-5.jpg)

![Slide 6](../../assets/images/sensitive-information/slides/slide-6.jpg)

![Slide 7](../../assets/images/sensitive-information/slides/slide-7.jpg)

![Slide 8](../../assets/images/sensitive-information/slides/slide-8.jpg)

![Slide 9](../../assets/images/sensitive-information/slides/slide-9.jpg)

![Slide 10](../../assets/images/sensitive-information/slides/slide-10.jpg)
