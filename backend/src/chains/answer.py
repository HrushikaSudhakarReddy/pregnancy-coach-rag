from typing import List, Dict, Any
from ollama import Client
from config import OLLAMA_HOST, OLLAMA_LLM_MODEL
import re

DISCLAIMER = (
    "This is general educational info, not medical advice. "
    "Please check anything important with your obstetric provider."
)

SYSTEM_PROMPT = (
    "You are a warm, supportive pregnancy fitness & nutrition assistant.\n"
    "Write in plain English with a natural, conversational tone.\n"
    "Use short paragraphs and 3–6 quick bullets. You may use **bold** labels (e.g., **Breakfast:**) sparingly.\n"
    "Avoid tables, code blocks, numbered 'Week X:' sections, or big headings.\n"
    "Ground facts in the provided snippets; if a fact isn't covered, say so briefly."
)

def _format_plan_header(profile: Dict[str, Any]) -> str:
    parts = []
    if profile.get("trimester"): parts.append(f"trimester {profile['trimester']}")
    if profile.get("weeks_pregnant"): parts.append(f"{profile['weeks_pregnant']} weeks")
    if profile.get("activity_level"): parts.append(profile["activity_level"])
    if profile.get("dietary_pref"): parts.append(profile["dietary_pref"])
    return ", ".join(parts) or "no profile details provided"

def _polish_text(msg: str) -> str:
    # remove code fences & headings and 'Week X:' labels
    msg = re.sub(r"```.+?```", "", msg, flags=re.S)
    msg = re.sub(r"(?m)^\s*#{1,6}\s*", "", msg)
    msg = re.sub(r"(?m)^\s*Week\s*\d+\s*:\s*", "", msg)
    # turn escaped \n into real newlines
    msg = msg.replace("\\n", "\n").replace("\\t", "\t")
    # collapse extra blank lines
    msg = re.sub(r"\n{3,}", "\n\n", msg)
    return msg.strip()

def _extract_from_repr(s: str) -> str:
    # If we somehow got a repr like: Message(role='assistant', content="..."),
    # pull the quoted content safely.
    m = re.search(r"content=(?P<q>['\"])(?P<txt>.*?)(?<!\\)(?P=q)", s, re.S)
    if not m:
        return ""
    text = m.group("txt")
    # unescape common sequences
    text = text.replace("\\n", "\n").replace("\\t", "\t").replace("\\\"", "\"").replace("\\'", "'")
    return text

def _extract_content(out) -> str:
    # Normal dict/object shapes
    try:
        if isinstance(out, dict):
            m = out.get("message")
            if isinstance(m, dict):
                c = m.get("content")
                if isinstance(c, str):
                    return c
        m = getattr(out, "message", None)
        if m is not None:
            c = getattr(m, "content", None)
            if isinstance(c, str):
                return c
            if isinstance(m, dict):
                c = m.get("content")
                if isinstance(c, str):
                    return c
    except Exception:
        pass
    # Fallback if someone did str(out) upstream
    if isinstance(out, str):
        return _extract_from_repr(out)
    return ""

def compose_answer(text: str, intent: str, docs: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
    citations = [d.get("source","") for d in docs if d.get("source")][:5]  # internal only
    snippets = "\n".join([f"- {d.get('snippet','')}" for d in docs[:6]])
    header = _format_plan_header(profile)

    user_prompt = f"""User message: {text}
User profile: {header}
Intent: {intent}

Relevant snippets (use these for facts):
{snippets}

Write a concise, friendly answer tailored to the profile. No tables or code blocks.
"""

    client = Client(host=OLLAMA_HOST)
    out = client.chat(
        model=OLLAMA_LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0.5, "top_p": 0.9, "num_ctx": 4096}
    )

    msg = _extract_content(out)
    msg = _polish_text(msg)
    msg = f"{msg}\n\n{DISCLAIMER}"

    facts = []
    if profile.get("dietary_pref"): facts.append(f"dietary_pref={profile['dietary_pref']}")
    if profile.get("activity_level"): facts.append(f"activity_level={profile['activity_level']}")

    return {"message": msg, "citations": citations, "facts_to_remember": facts}
