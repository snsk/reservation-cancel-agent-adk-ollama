"""Bridge local models that emit ReAct-style JSON back into ADK tool calls."""

from __future__ import annotations

import json
import re
from typing import Any

from google.adk.agents.context import Context
from google.adk.models.llm_response import LlmResponse
from google.genai import types


ALLOWED_ACTIONS = {
    "authenticate_user",
    "list_reservations",
    "check_cancellation_eligibility",
    "prepare_cancellation",
    "cancel_reservation",
    "confirm_and_cancel_reservation",
    "reset_mock_data",
}


def rewrite_react_json_action(
    callback_context: Context,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """Convert `{"action": ..., "arguments": ...}` text into an ADK function call."""
    del callback_context

    if llm_response.get_function_calls():
        return None

    text = _response_text(llm_response)
    if not text:
        return None

    payload = _parse_json_object(text)
    if not payload:
        return None

    message = payload.get("message")
    if isinstance(message, str) and "action" not in payload:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=message)],
            )
        )

    action = payload.get("action")
    arguments = payload.get("arguments", {})
    if action not in ALLOWED_ACTIONS or not isinstance(arguments, dict):
        return None

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part.from_function_call(
                    name=action,
                    args=arguments,
                )
            ],
        )
    )


def _response_text(llm_response: LlmResponse) -> str | None:
    parts = llm_response.content.parts if llm_response.content else None
    if not parts:
        return None

    texts = [part.text for part in parts if part.text]
    if not texts:
        return None
    return "\n".join(texts).strip()


def _parse_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", stripped, re.DOTALL)
    if fenced:
        stripped = fenced.group(1)

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None
    return parsed
