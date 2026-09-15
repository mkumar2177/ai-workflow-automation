"""
ai_summary.py
Generates a short, human-readable summary of the processed batch using
the OpenAI API. Falls back to an offline DEMO mode (no API key /
no internet) so the project can still be run and graded without
exposing any credentials.

The AI is only ever asked to DRAFT a summary. Nothing it produces is
sent anywhere automatically — it is written to the report for a human
reviewer to check, per the human-in-the-loop step in main.py.
"""

import os

DEMO_MODE_NOTICE = (
    "[DEMO MODE: OPENAI_API_KEY not set — using offline fallback summary "
    "instead of a live API call.]"
)


def _build_prompt(stats: dict) -> str:
    return (
        "You are a support-operations assistant. In 3-4 sentences, "
        "summarise this batch of customer requests for a manager, "
        "highlighting anything that needs urgent attention:\n"
        f"{stats}"
    )


def _call_openai(prompt: str) -> str:
    """
    Calls the OpenAI API. Requires the OPENAI_API_KEY environment
    variable to be set — no key is ever hard-coded in this file.
    """
    from openai import OpenAI  # imported lazily so DEMO mode has no dependency

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()


def _demo_summary(stats: dict) -> str:
    """
    Offline fallback: builds a template-based summary using the same
    statistics an LLM call would be given, so DEMO mode and live mode
    are answering the same question.
    """
    total = stats.get("total_valid", 0)
    high = stats.get("priority_counts", {}).get("High", 0)
    billing = stats.get("type_counts", {}).get("Billing", 0)

    return (
        f"{DEMO_MODE_NOTICE}\n"
        f"Of {total} valid requests processed in this batch, {high} were "
        f"flagged High priority and {billing} were Billing-related. "
        f"High-priority billing issues (refunds, duplicate charges) should "
        f"be reviewed first, as these directly affect customer trust. "
        f"The remaining requests are routine and can be handled in the "
        f"normal queue."
    )


def generate_summary(stats: dict) -> dict:
    """
    Returns a dict: {"summary": str, "mode": "LIVE" | "DEMO"}
    Never raises on a missing API key — always falls back to DEMO mode.
    """
    prompt = _build_prompt(stats)

    if os.environ.get("OPENAI_API_KEY"):
        try:
            summary = _call_openai(prompt)
            return {"summary": summary, "mode": "LIVE"}
        except Exception as exc:  # API failure -> safe fallback, never crash the batch
            fallback = _demo_summary(stats)
            return {"summary": fallback, "mode": f"DEMO (API call failed: {exc})"}

    return {"summary": _demo_summary(stats), "mode": "DEMO"}
