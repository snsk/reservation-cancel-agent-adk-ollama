"""Manual smoke tests for reservation cancellation tools."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reservation_cancel_agent.tools import (
    authenticate_user,
    cancel_reservation,
    check_cancellation_eligibility,
    confirm_and_cancel_reservation,
    list_reservations,
    prepare_cancellation,
    reset_mock_data,
)


def assert_success(result: dict) -> None:
    assert result["status"] == "success", result


def assert_refused(result: dict, reason: str) -> None:
    assert result["status"] == "refused", result
    assert result["reason"] == reason, result


def main() -> None:
    assert_success(reset_mock_data())
    assert_success(authenticate_user("u_alice"))

    reservations = list_reservations("u_alice")
    assert_success(reservations)
    assert {item["reservation_id"] for item in reservations["reservations"]} == {
        "R100",
        "R101",
    }

    assert_success(check_cancellation_eligibility("u_alice", "R100"))
    prepared = prepare_cancellation("u_alice", "R100")
    assert_success(prepared)
    assert_success(cancel_reservation("u_alice", "R100", prepared["confirmation_token"]))

    assert_success(reset_mock_data())
    assert_success(confirm_and_cancel_reservation("u_alice", "R100", True))

    assert_success(reset_mock_data())
    assert_refused(
        prepare_cancellation("u_alice", "R101"),
        "reservation_not_cancellable",
    )
    assert_refused(
        prepare_cancellation("u_alice", "R200"),
        "reservation_not_owned",
    )
    assert_refused(
        cancel_reservation("u_alice", "R100", "missing-token"),
        "invalid_confirmation_token",
    )
    assert_refused(
        confirm_and_cancel_reservation("u_alice", "R100", False),
        "confirmation_required",
    )

    print("manual tests passed")


if __name__ == "__main__":
    main()
