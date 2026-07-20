from __future__ import annotations

from reservation_cancel_agent.tools import (
    cancel_reservation,
    confirm_and_cancel_reservation,
    list_reservations,
    prepare_cancellation,
    reset_mock_data,
)


def setup_function() -> None:
    reset_mock_data()


def test_alice_can_cancel_r100_after_confirmation() -> None:
    prepared = prepare_cancellation("u_alice", "R100")

    assert prepared["status"] == "success"

    cancelled = cancel_reservation(
        "u_alice",
        "R100",
        prepared["confirmation_token"],
    )

    assert cancelled["status"] == "success"
    assert cancelled["reservation"]["status"] == "cancelled"


def test_confirm_and_cancel_helper_requires_confirmation() -> None:
    result = confirm_and_cancel_reservation("u_alice", "R100", False)

    assert result["status"] == "refused"
    assert result["reason"] == "confirmation_required"


def test_confirm_and_cancel_helper_cancels_when_confirmed() -> None:
    result = confirm_and_cancel_reservation("u_alice", "R100", True)

    assert result["status"] == "success"
    assert result["reservation"]["status"] == "cancelled"


def test_alice_cannot_cancel_non_cancellable_r101() -> None:
    result = prepare_cancellation("u_alice", "R101")

    assert result["status"] == "refused"
    assert result["reason"] == "reservation_not_cancellable"


def test_alice_cannot_cancel_bobs_r200() -> None:
    result = prepare_cancellation("u_alice", "R200")

    assert result["status"] == "refused"
    assert result["reason"] == "reservation_not_owned"


def test_cancel_without_prepare_is_refused() -> None:
    result = cancel_reservation("u_alice", "R100", "missing-token")

    assert result["status"] == "refused"
    assert result["reason"] == "invalid_confirmation_token"


def test_reset_restores_cancelled_reservation() -> None:
    prepared = prepare_cancellation("u_alice", "R100")
    cancel_reservation("u_alice", "R100", prepared["confirmation_token"])

    reset_mock_data()
    reservations = list_reservations("u_alice")
    r100 = next(
        item for item in reservations["reservations"] if item["reservation_id"] == "R100"
    )

    assert r100["status"] == "active"
