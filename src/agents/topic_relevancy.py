"""
Implements a guardrail to check user queries are relevant to the topic of books and recommendations.
"""

import json
import os

from dotenv import load_dotenv

from src.agents.openai_client import create_openai_client
from src.prompts.guardrails import GUARDRAIL_SYSTEM

load_dotenv()

guardrail_client = create_openai_client(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    timeout=10,
)


def classify_query(user_message: str, context: list[dict]) -> dict:
    """
    Runs the guardrail classifier.
    Passes the conversation context so mid-conversation steering is caught.
    Context is a list of {"role": "user"/"assistant"/"system", "content": str} dicts representing the conversation history and
    controlled by the caller.

    Returns {"allowed": bool, "reason": str}
    """
    model = os.getenv("QUERY_CLASSIFIER_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free")
    context_str = _format_context(context)
    user_message = f"CONVERSATION HISTORY:\n{context_str}\n\nUSER MESSAGE:\n{user_message}"
    messages = [{"role": "system", "content": GUARDRAIL_SYSTEM}] + [
        {"role": "user", "content": user_message}
    ]

    response = guardrail_client.chat.completions.create(
        model=model,
        max_completion_tokens=1000,
        messages=messages,
        extra_body={"reasoning": {"enabled": False}},
    )

    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fail open — if classifier output is malformed, allow the query
        return {"allowed": True, "reason": "classifier parse error"}


def _format_context(context: list[dict]) -> str:
    """Helper to format conversation context for the guardrail classifier."""
    formatted = []
    for turn in context:
        role = turn["role"]
        content = turn["content"]
        formatted.append(f"{role.upper()}: {content}")
    return "\n".join(formatted)
