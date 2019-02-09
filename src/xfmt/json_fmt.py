"""
Formatting functions for json
"""
import difflib
import json
from typing import Iterable, List

JSON_PRETTY_KWARGS = {
    'indent': 2,
    'separators': (',', ': '),
    'sort_keys': True,
}

_FROMFILE = 'actual'


def _fix_json(before: str) -> str:
    data = json.loads(before)
    after = json.dumps(data, **JSON_PRETTY_KWARGS)  # type: ignore
    return after


def _chunk_lines(lines: Iterable[str]) -> Iterable[str]:
    chunk = []  # type: List[str]
    for line in lines:
        if line == '--- {}\n'.format(_FROMFILE):
            yield ''.join(chunk)
            chunk = []
        chunk.append(line)
    yield ''.join(chunk)


def check_json(before: str) -> List[str]:
    """Check if json is properly formatted.
    """
    after = _fix_json(before)
    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=_FROMFILE,
        tofile='expected'
    )
    chunks = list(_chunk_lines(lines))
    return chunks[1:]  # First chunk is empty
