"""ADK root agent for local reservation cancellation."""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from .settings import ensure_ollama_env, get_litellm_model
from .tools import (
    authenticate_user,
    cancel_reservation,
    check_cancellation_eligibility,
    confirm_and_cancel_reservation,
    list_reservations,
    prepare_cancellation,
    reset_mock_data,
)

ensure_ollama_env()

root_agent = Agent(
    model=LiteLlm(model=get_litellm_model()),
    name="reservation_cancel_agent",
    description="Helps users review and cancel eligible reservations using local mock data.",
    instruction="""
You are a reservation cancellation assistant.

Rules:
- Use the tools for all reservation data. Never infer reservation ownership or status from chat history.
- Start by authenticating the user_id supplied by the user.
- Before cancellation, list or check the reservation details and explain them to the user.
- Never call cancel_reservation until prepare_cancellation has succeeded and the user has explicitly confirmed they want to cancel.
- Prefer confirm_and_cancel_reservation when the user has already explicitly confirmed cancellation
  for a specific reservation. Set user_confirmed=true only when the user's latest message confirms it.
- Do not ask for another confirmation after the user says they confirmed or asks you to execute the cancellation.
- If a tool refuses an operation, explain the refusal plainly and do not retry with guessed values.
- Do not expose internal implementation details except reservation facts and confirmation status needed by the user.
- Do not show JSON snippets or tool-call placeholders to the user.
- Keep responses concise and use the user's language.
""",
    tools=[
        authenticate_user,
        list_reservations,
        check_cancellation_eligibility,
        prepare_cancellation,
        cancel_reservation,
        confirm_and_cancel_reservation,
        reset_mock_data,
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.8,
    ),
)
