"""Seed-backed runtime store for mock reservations."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from secrets import token_urlsafe
from threading import RLock
from typing import Any


SEED_PATH = Path(__file__).parent / "data" / "reservations.seed.json"


@dataclass(frozen=True)
class ReservationRef:
    user_id: str
    reservation_id: str


class ReservationStore:
    """In-memory runtime store initialized from seed JSON."""

    def __init__(self, seed_path: Path = SEED_PATH) -> None:
        self._seed_path = seed_path
        self._lock = RLock()
        self._users: dict[str, dict[str, Any]] = {}
        self._pending_tokens: dict[str, ReservationRef] = {}
        self.reset()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            with self._seed_path.open(encoding="utf-8") as seed_file:
                seed_data = json.load(seed_file)
            self._users = deepcopy(seed_data["users"])
            self._pending_tokens = {}
            return self._ok("Mock reservation data has been reset.")

    def authenticate_user(self, user_id: str) -> dict[str, Any]:
        with self._lock:
            user = self._users.get(user_id)
            if user is None:
                return self._refused("unknown_user", f"Unknown user_id: {user_id}")
            return self._ok(
                f"Authenticated user {user_id}.",
                user_id=user_id,
                display_name=user["display_name"],
            )

    def list_reservations(self, user_id: str) -> dict[str, Any]:
        with self._lock:
            user = self._users.get(user_id)
            if user is None:
                return self._refused("unknown_user", f"Unknown user_id: {user_id}")
            return self._ok(
                f"Found {len(user['reservations'])} reservation(s) for {user_id}.",
                user_id=user_id,
                reservations=deepcopy(user["reservations"]),
            )

    def check_cancellation_eligibility(
        self,
        user_id: str,
        reservation_id: str,
    ) -> dict[str, Any]:
        with self._lock:
            validation = self._validate_reservation_for_cancellation(
                user_id,
                reservation_id,
                require_cancellable=True,
            )
            if validation["status"] != "success":
                return validation
            return self._ok(
                f"Reservation {reservation_id} is eligible for cancellation.",
                user_id=user_id,
                reservation=deepcopy(validation["reservation"]),
                eligible=True,
            )

    def prepare_cancellation(self, user_id: str, reservation_id: str) -> dict[str, Any]:
        with self._lock:
            validation = self._validate_reservation_for_cancellation(
                user_id,
                reservation_id,
                require_cancellable=True,
            )
            if validation["status"] != "success":
                return validation

            confirmation_token = token_urlsafe(18)
            self._pending_tokens[confirmation_token] = ReservationRef(
                user_id=user_id,
                reservation_id=reservation_id,
            )
            return self._ok(
                (
                    f"Cancellation for reservation {reservation_id} is prepared. "
                    "Ask the user for explicit confirmation before cancelling."
                ),
                user_id=user_id,
                reservation=deepcopy(validation["reservation"]),
                confirmation_token=confirmation_token,
                prepared_at=datetime.now(timezone.utc).isoformat(),
            )

    def cancel_reservation(
        self,
        user_id: str,
        reservation_id: str,
        confirmation_token: str,
    ) -> dict[str, Any]:
        with self._lock:
            validation = self._validate_reservation_for_cancellation(
                user_id,
                reservation_id,
                require_cancellable=True,
            )
            if validation["status"] != "success":
                return validation

            token_ref = self._pending_tokens.get(confirmation_token)
            if token_ref is None:
                return self._refused(
                    "invalid_confirmation_token",
                    "Cancellation refused: prepare_cancellation must be called first.",
                )
            if token_ref != ReservationRef(user_id=user_id, reservation_id=reservation_id):
                return self._refused(
                    "confirmation_token_mismatch",
                    "Cancellation refused: confirmation token does not match this user and reservation.",
                )

            reservation = validation["reservation"]
            reservation["status"] = "cancelled"
            del self._pending_tokens[confirmation_token]

            return self._ok(
                f"Reservation {reservation_id} has been cancelled.",
                user_id=user_id,
                reservation=deepcopy(reservation),
            )

    def _validate_reservation_for_cancellation(
        self,
        user_id: str,
        reservation_id: str,
        *,
        require_cancellable: bool,
    ) -> dict[str, Any]:
        user = self._users.get(user_id)
        if user is None:
            return self._refused("unknown_user", f"Unknown user_id: {user_id}")

        reservation = self._find_reservation(user, reservation_id)
        if reservation is None:
            return self._refused(
                "reservation_not_owned",
                (
                    f"Reservation {reservation_id} does not belong to user {user_id} "
                    "or does not exist."
                ),
            )

        if reservation["status"] != "active":
            return self._refused(
                "reservation_not_active",
                f"Reservation {reservation_id} is not active.",
                reservation=deepcopy(reservation),
            )

        if require_cancellable and not reservation["cancellable"]:
            return self._refused(
                "reservation_not_cancellable",
                f"Reservation {reservation_id} is not cancellable.",
                reservation=deepcopy(reservation),
            )

        return self._ok(
            f"Reservation {reservation_id} passed cancellation validation.",
            reservation=reservation,
        )

    @staticmethod
    def _find_reservation(
        user: dict[str, Any],
        reservation_id: str,
    ) -> dict[str, Any] | None:
        for reservation in user["reservations"]:
            if reservation["reservation_id"] == reservation_id:
                return reservation
        return None

    @staticmethod
    def _ok(message: str, **payload: Any) -> dict[str, Any]:
        return {"status": "success", "message": message, **payload}

    @staticmethod
    def _refused(reason: str, message: str, **payload: Any) -> dict[str, Any]:
        return {
            "status": "refused",
            "reason": reason,
            "message": message,
            **payload,
        }


STORE = ReservationStore()
