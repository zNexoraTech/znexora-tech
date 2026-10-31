"""AI writing helper. Every function returns None when there is no ANTHROPIC_API_KEY
or the AI call fails, so the robots can fall back to free templates."""
import json
import os
import re

from common import http_json

STYLE = """House style for ZNexora Tech:
- Plain, calm, accurate English for IT and security readers. No hype, no emojis, no marketing.
- Use ONLY the facts you are given. Never invent names, numbers, versions, dates, quotes or links.
- If something is unknown, say it has not been reported yet.
- Write in your own words. Never copy sentences from the material you are given.
- Defensive focus: explain how to detect, prevent and respond. Never give attack instructions."""


def ai_json(task, material, model, max_tokens=2000):
    """Ask the AI for a JSON object. Returns a dict, or None to use the free template."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": STYLE + "\n\nReply with one JSON object only, no code fences.",
        "messages": [{"role": "user", "content": f"{task}\n\nMATERIAL:\n{material}"}],
    }
    try:
        data = http_json("https://api.anthropic.com/v1/messages",
                         headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                         data=payload, method="POST", timeout=180)
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start:end + 1])
    except Exception as exc:
        print(f"  AI writing failed ({exc}); using the free template instead.")
        return None
