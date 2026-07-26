from __future__ import annotations

from reservation_cancel_agent.tool_guard import FAILED_AUTH_USER_IDS_KEY
from reservation_cancel_agent.tool_guard import is_repeated_failed_authentication
from reservation_cancel_agent.tool_guard import record_failed_authentication


class FakeTool:
    name = "authenticate_user"


class FakeContext:
    def __init__(self) -> None:
        self.state = {}


def test_record_failed_authentication_marks_unknown_user_terminal() -> None:
    context = FakeContext()

    result = record_failed_authentication(
        FakeTool(),
        {"user_id": "GUEST01"},
        context,
        {
            "status": "refused",
            "reason": "unknown_user",
            "message": "Unknown user_id: GUEST01",
        },
    )

    assert result is not None
    assert result["terminal"] is True
    assert "GUEST01" in result["message"]
    assert context.state[FAILED_AUTH_USER_IDS_KEY] == ["GUEST01"]


def test_repeated_failed_authentication_detects_recorded_user() -> None:
    state = {FAILED_AUTH_USER_IDS_KEY: ["GUEST01"]}

    assert is_repeated_failed_authentication(
        state,
        "authenticate_user",
        {"user_id": "GUEST01"},
    )


def test_repeated_failed_authentication_ignores_other_tools() -> None:
    state = {FAILED_AUTH_USER_IDS_KEY: ["GUEST01"]}

    assert not is_repeated_failed_authentication(
        state,
        "list_reservations",
        {"user_id": "GUEST01"},
    )
