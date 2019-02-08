"""
Formatting functions for json
"""
import difflib
import json
import sys

JSON_PRETTY_KWARGS = {
    'indent': 2,
    'separators': (',', ': '),
    'sort_keys': True,
}


def _fix_json(before: str) -> str:
    data = json.loads(before)
    after = json.dumps(data, **JSON_PRETTY_KWARGS)  # type: ignore
    return after


def check_json(before: str) -> bool:
    """Check if json is properly formatted.

    The return values may seem unintuitive but the idea is to allow functions
    to return hints as to what is wrong in the case of failure. In the case of
    success no hints would be needed.

    :param before: json string
    :return: True for failure, False for success.
    """
    after = _fix_json(before)
    sys.stdout.writelines(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile='actual',
            tofile='expected'
        )
    )
    return before != after
