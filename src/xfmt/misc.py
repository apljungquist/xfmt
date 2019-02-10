"""
Miscellaneous utilities
"""
import difflib
from typing import Iterable, List, Optional


def _chunk_lines(lines: Iterable[str], fromfile: str) -> Iterable[str]:
    chunk = []  # type: List[str]
    for line in lines:
        if line == "--- {}\n".format(fromfile):
            yield "".join(chunk)
            chunk = []
        chunk.append(line)
    yield "".join(chunk)


def diff(before: str, after: str, path: Optional[str] = None) -> List[str]:
    """Produce feedback from the difference between two versions.
    """
    if path is None:
        fromfile = "actual"
        tofile = "expected"
    else:
        fromfile = tofile = path

    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=fromfile,
        tofile=tofile,
    )
    chunks = list(_chunk_lines(lines, fromfile))
    return chunks[1:]  # First chunk is empty
