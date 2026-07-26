"""Callbacks that prevent local models from retrying terminal tool failures."""

from __future__ import annotations

from typing import Any


FAILED_AUTH_USER_IDS_KEY = "reservation_cancel_agent.failed_auth_user_ids"


def record_failed_authentication(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
    tool_response: dict[str, Any],
) -> dict[str, Any] | None:
    """Record unknown user IDs so repeated auth attempts can be stopped."""
    if (
        getattr(tool, "name", None) != "authenticate_user"
        or tool_response.get("status") != "refused"
        or tool_response.get("reason") != "unknown_user"
    ):
        return None

    user_id = args.get("user_id")
    if not isinstance(user_id, str) or not user_id:
        return None

    failed_user_ids = set(tool_context.state.get(FAILED_AUTH_USER_IDS_KEY, []))
    failed_user_ids.add(user_id)
    tool_context.state[FAILED_AUTH_USER_IDS_KEY] = sorted(failed_user_ids)

    updated_response = dict(tool_response)
    updated_response["terminal"] = True
    updated_response["message"] = unknown_user_message(user_id)
    return updated_response


def is_repeated_failed_authentication(
    state: Any,
    action: str,
    arguments: dict[str, Any],
) -> bool:
    """Return True when the model tries to authenticate a known-bad user again."""
    if action != "authenticate_user":
        return False

    user_id = arguments.get("user_id")
    if not isinstance(user_id, str):
        return False

    return user_id in set(state.get(FAILED_AUTH_USER_IDS_KEY, []))


def unknown_user_message(user_id: str) -> str:
    """User-facing response for a terminal unknown-user authentication failure."""
    return (
        f"ユーザーID「{user_id}」は登録されていません。"
        "正しいユーザーIDを入力してください。動作確認用なら u_alice または u_bob を使えます。"
    )
