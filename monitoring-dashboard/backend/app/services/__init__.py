"""Transaction state engine"""

from app.models import TransactionStateEnum
from typing import Set, Tuple


class StateTransitionValidator:
    """Validates transaction state transitions"""

    # Define valid transitions
    VALID_TRANSITIONS: dict = {
        TransactionStateEnum.INITIATED: {
            TransactionStateEnum.AUTHORIZED,
            TransactionStateEnum.FAILED,
            TransactionStateEnum.TIMEOUT,
        },
        TransactionStateEnum.AUTHORIZED: {
            TransactionStateEnum.PROCESSING,
            TransactionStateEnum.FAILED,
            TransactionStateEnum.TIMEOUT,
        },
        TransactionStateEnum.PROCESSING: {
            TransactionStateEnum.SWITCHED,
            TransactionStateEnum.SETTLED,
            TransactionStateEnum.FAILED,
            TransactionStateEnum.TIMEOUT,
        },
        TransactionStateEnum.SWITCHED: {
            TransactionStateEnum.SETTLED,
            TransactionStateEnum.FAILED,
            TransactionStateEnum.TIMEOUT,
        },
        TransactionStateEnum.SETTLED: {
            TransactionStateEnum.REVERSED,
            TransactionStateEnum.REFUNDED,
        },
        TransactionStateEnum.FAILED: {
            TransactionStateEnum.REVERSED,
        },
        TransactionStateEnum.REVERSED: set(),
        TransactionStateEnum.REFUNDED: set(),
        TransactionStateEnum.TIMEOUT: {
            TransactionStateEnum.REVERSED,
        },
    }

    @classmethod
    def is_valid_transition(
        cls, from_state: TransactionStateEnum, to_state: TransactionStateEnum
    ) -> bool:
        """Check if transition is valid"""
        if from_state not in cls.VALID_TRANSITIONS:
            return False
        return to_state in cls.VALID_TRANSITIONS[from_state]

    @classmethod
    def get_valid_transitions(cls, from_state: TransactionStateEnum) -> Set[TransactionStateEnum]:
        """Get all valid transitions from current state"""
        return cls.VALID_TRANSITIONS.get(from_state, set())

    @classmethod
    def is_terminal_state(cls, state: TransactionStateEnum) -> bool:
        """Check if state is terminal (no further transitions possible)"""
        return len(cls.get_valid_transitions(state)) == 0


class StateTransitionError(Exception):
    """Raised when invalid state transition is attempted"""

    pass
