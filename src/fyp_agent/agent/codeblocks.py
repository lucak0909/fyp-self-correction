"""Extract a Python code block from a model response. Models reliably wrap
code in ```python ... ``` fences even when asked for "only the code", so we
parse defensively rather than trusting that instruction literally.
"""

from __future__ import annotations

import re

_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def extract_code(text: str) -> str:
    match = _FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()
