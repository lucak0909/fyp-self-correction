"""A handful of hand-written problems for offline smoke-testing the pipeline
without needing network access to download a real benchmark.

Not used for the actual research results -- only for development.
"""

from __future__ import annotations

from .base import Problem

_PROBLEMS = [
    Problem(
        problem_id="fixture/add",
        source="fixture",
        prompt=(
            "def add(a: int, b: int) -> int:\n"
            '    """Return the sum of a and b."""\n'
        ),
        entry_point="add",
        test_code=(
            "def check(add):\n"
            "    assert add(2, 3) == 5\n"
            "    assert add(-1, 1) == 0\n"
            "    assert add(0, 0) == 0\n"
        ),
        starter_code=(
            "def add(a: int, b: int) -> int:\n"
            '    """Return the sum of a and b."""\n'
        ),
    ),
    Problem(
        problem_id="fixture/is_palindrome",
        source="fixture",
        prompt=(
            "def is_palindrome(s: str) -> bool:\n"
            '    """Return True if s reads the same forwards and backwards."""\n'
        ),
        entry_point="is_palindrome",
        test_code=(
            "def check(is_palindrome):\n"
            "    assert is_palindrome('racecar') is True\n"
            "    assert is_palindrome('hello') is False\n"
            "    assert is_palindrome('') is True\n"
        ),
        starter_code=(
            "def is_palindrome(s: str) -> bool:\n"
            '    """Return True if s reads the same forwards and backwards."""\n'
        ),
    ),
    Problem(
        problem_id="fixture/fib",
        source="fixture",
        prompt=(
            "def fib(n: int) -> int:\n"
            '    """Return the nth Fibonacci number, fib(0) == 0, fib(1) == 1."""\n'
        ),
        entry_point="fib",
        test_code=(
            "def check(fib):\n"
            "    assert fib(0) == 0\n"
            "    assert fib(1) == 1\n"
            "    assert fib(10) == 55\n"
        ),
        starter_code=(
            "def fib(n: int) -> int:\n"
            '    """Return the nth Fibonacci number, fib(0) == 0, fib(1) == 1."""\n'
        ),
    ),
]


class LocalFixtureLoader:
    """Returns the tiny built-in problem set, ignoring `limit` beyond its size."""

    def load(self, limit: int | None = None) -> list[Problem]:
        if limit is None:
            return list(_PROBLEMS)
        return _PROBLEMS[:limit]
