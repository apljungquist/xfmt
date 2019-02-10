"""
Formatting functions for json
"""
import difflib
import json
import os
from typing import Iterable, List, Optional

from xfmt import base

JSON_PRETTY_KWARGS = {
    'indent': 2,
    'separators': (',', ': '),
    'sort_keys': True,
}


def _chunk_lines(lines: Iterable[str], fromfile: str) -> Iterable[str]:
    chunk = []  # type: List[str]
    for line in lines:
        if line == '--- {}\n'.format(fromfile):
            yield ''.join(chunk)
            chunk = []
        chunk.append(line)
    yield ''.join(chunk)


def _diff(before: str, after: str, path: Optional[str] = None) -> List[str]:
    if path is None:
        fromfile = 'actual'
        tofile = 'expected'
    else:
        fromfile = tofile = path

    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=fromfile,
        tofile=tofile
    )
    chunks = list(_chunk_lines(lines, fromfile))
    return chunks[1:]  # First chunk is empty


def fix_content_json(before: str) -> str:
    """Fix json formatting, returning the pretty version.
    """
    data = json.loads(before)
    after = json.dumps(data, **JSON_PRETTY_KWARGS)  # type: ignore
    return after


def check_content_json(before: str) -> List[str]:
    """Check json formatting, returning any differences to the pretty version.
    """
    after = fix_content_json(before)
    if before == after:
        return []
    return _diff(before, after)


def fix_file_json(path: str) -> List[str]:
    """Fix json formatting, returning any changes that have been made.
    """
    with open(path, 'r') as fp:
        before = fp.read()

    after = fix_content_json(before)

    if before == after:
        return []

    with open(path, 'w') as fp:
        fp.write(after)

    return _diff(before, after)


def check_file_json(path: str) -> List[str]:
    """Check json formatting, returning any changes that should be made.
    """
    with open(path, 'r') as fp:
        before = fp.read()

    after = fix_content_json(before)
    if before == after:
        return []

    return _diff(before, after, path)


class JsonFormatter(base.Formatter):
    """Plugin for checking the format of json files.
    """

    def check(self, path):
        return check_file_json(path)

    def fix(self, path: str):
        return fix_file_json(path)

    def match(self, path):
        _, ext = os.path.splitext(path)
        return ext == '.json'
