from fyp_agent.agent.codeblocks import extract_code


def test_extracts_fenced_python_block():
    text = "Here is the solution:\n```python\ndef f():\n    return 1\n```\nDone."
    assert extract_code(text) == "def f():\n    return 1"


def test_extracts_plain_fenced_block():
    text = "```\ndef f():\n    return 1\n```"
    assert extract_code(text) == "def f():\n    return 1"


def test_falls_back_to_raw_text_when_no_fence():
    text = "def f():\n    return 1"
    assert extract_code(text) == "def f():\n    return 1"
