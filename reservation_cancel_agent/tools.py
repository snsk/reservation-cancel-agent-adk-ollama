"""ADK function tools for reservation cancellation."""

from __future__ import annotations

from .store import STORE


def authenticate_user(user_id: str) -> dict:
    """Authenticate a mock user by user_id before reservation operations."""
    return STORE.authenticate_user(user_id)


def list_reservations(user_id: str) -> dict:
    """List reservations owned by the authenticated mock user."""
    return STORE.list_reservations(user_id)


def check_cancellation_eligibility(user_id: str, reservation_id: str) -> dict:
    """Check whether a reservation is active, owned by the user, and cancellable."""
    return STORE.check_cancellation_eligibility(user_id, reservation_id)


def prepare_cancellation(user_id: str, reservation_id: str) -> dict:
    """Prepare a cancellation and return a confirmation token for explicit confirmation."""
    return STORE.prepare_cancellation(user_id, reservation_id)


def cancel_reservation(
    user_id: str,
    reservation_id: str,
    confirmation_token: str,
) -> dict:
    """Cancel a reservation only when a valid confirmation token is provided."""
    return STORE.cancel_reservation(user_id, reservation_id, confirmation_token)


def confirm_and_cancel_reservation(
    user_id: str,
    reservation_id: str,
    user_confirmed: bool,
) -> dict:
    """Prepare and cancel a reservation after explicit user confirmation."""
    if not user_confirmed:
        return {
            "status": "refused",
            "reason": "confirmation_required",
            "message": "Cancellation refused: explicit user confirmation is required.",
        }

    prepared = STORE.prepare_cancellation(user_id, reservation_id)
    if prepared["status"] != "success":
        return prepared

    return STORE.cancel_reservation(
        user_id,
        reservation_id,
        prepared["confirmation_token"],
    )


def reset_mock_data() -> dict:
    """Reset runtime mock data from the seed JSON file."""
    return STORE.reset()
