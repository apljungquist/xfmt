"""
Functions for collecting and running formatting tools on files.
"""
import glob
import logging
import os
from typing import Iterable, List

from xfmt import json_fmt

logger = logging.getLogger(__name__)


def collect(top: str) -> Iterable[str]:
    """Collect file paths to be checked.
    """
    if not os.path.isdir(top):
        if os.path.isfile(top):
            raise ValueError("Collecting from file is meaningless")
        else:
            raise RuntimeError("Huh? {}".format(top))
    paths = filter(os.path.isfile, glob.iglob(os.path.join(top, '**'), recursive=True))
    yield from (os.path.relpath(p, top) for p in paths)


def check(path: str) -> List[str]:
    """Check format of file.
    """
    _, ext = os.path.splitext(path)
    if ext == '.json':
        with open(path, 'r') as fp:
            return json_fmt.check_json(fp.read())
    raise LookupError("Path did not match any pattern")
