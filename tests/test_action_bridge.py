from __future__ import annotations

from google.adk.models.llm_response import LlmResponse
from google.genai import types

from reservation_cancel_agent.action_bridge import rewrite_react_json_action


def text_response(text: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=text)],
        )
    )


def test_rewrites_react_json_action_to_function_call() -> None:
    response = text_response(
        '{"thought":"Need reservations","action":"list_reservations",'
        '"arguments":{"user_id":"u_alice"}}'
    )

    rewritten = rewrite_react_json_action(None, response)  # type: ignore[arg-type]

    assert rewritten is not None
    calls = rewritten.get_function_calls()
    assert len(calls) == 1
    assert calls[0].name == "list_reservations"
    assert calls[0].args == {"user_id": "u_alice"}


def test_ignores_unknown_action() -> None:
    response = text_response(
        '{"action":"delete_everything","arguments":{"user_id":"u_alice"}}'
    )

    assert rewrite_react_json_action(None, response) is None  # type: ignore[arg-type]


def test_unwraps_message_json_to_plain_text() -> None:
    response = text_response('{"message":"予約 R100 をキャンセルしました。"}')

    rewritten = rewrite_react_json_action(None, response)  # type: ignore[arg-type]

    assert rewritten is not None
    assert rewritten.content is not None
    assert rewritten.content.parts is not None
    assert rewritten.content.parts[0].text == "予約 R100 をキャンセルしました。"


def test_ignores_plain_text() -> None:
    response = text_response("こんにちは。ユーザーIDを教えてください。")

    assert rewrite_react_json_action(None, response) is None  # type: ignore[arg-type]
