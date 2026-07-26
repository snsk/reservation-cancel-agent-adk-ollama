from __future__ import annotations

from reservation_cancel_agent.agent import AGENT_INSTRUCTION, root_agent


def test_greeting_instruction_uses_correct_name() -> None:
    instruction = AGENT_INSTRUCTION.lower()

    assert "greeting" in instruction
    assert "greeding" not in instruction


def test_greeting_only_messages_do_not_call_reservation_tools() -> None:
    instruction = AGENT_INSTRUCTION.lower()

    assert "greeting-only" in instruction
    assert "do not call reservation tools" in instruction


def test_greeting_with_cancellation_intent_continues_normal_flow() -> None:
    instruction = AGENT_INSTRUCTION.lower()

    assert "both a greeting and reservation or cancellation intent" in instruction
    assert "normal reservation cancellation flow" in instruction


def test_root_agent_uses_instruction_constant() -> None:
    assert root_agent.instruction == AGENT_INSTRUCTION
