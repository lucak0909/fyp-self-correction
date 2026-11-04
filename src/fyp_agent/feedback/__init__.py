from .base import FeedbackStrategy
from .binary import BinaryFeedbackStrategy
from .execution import ExecutionFeedbackStrategy
from .none import NoCorrectionStrategy
from .self_reflection import SelfReflectionStrategy

STRATEGIES: dict[str, type[FeedbackStrategy]] = {
    "no_correction": NoCorrectionStrategy,
    "self_reflection": SelfReflectionStrategy,
    "binary": BinaryFeedbackStrategy,
    "execution": ExecutionFeedbackStrategy,
}

__all__ = [
    "FeedbackStrategy",
    "NoCorrectionStrategy",
    "SelfReflectionStrategy",
    "BinaryFeedbackStrategy",
    "ExecutionFeedbackStrategy",
    "STRATEGIES",
]
