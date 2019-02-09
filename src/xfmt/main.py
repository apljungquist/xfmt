"""
Functions for collecting and running formatting tools on files.
"""
import contextlib
import glob
import logging
import os
import sys
from datetime import datetime
from typing import Iterable, List

import click
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


@contextlib.contextmanager
def _exit_codes():
    try:
        yield
    except Exception as e:  # pylint: disable=W0703
        logger.critical(e)
        exit(1)
    exit(0)


@click.command()
@click.argument('top', type=click.STRING)
def main(top):
    """Recursively check formatting of files under path
    """
    with _exit_codes():
        logging.basicConfig(
            level=logging.DEBUG, handlers=[logging.FileHandler('main.log')]
        )
        logger.info("Logging initialized at %s", datetime.now().isoformat())
        for path in collect(top):
            logger.info("Checking %s", path)
            try:
                feedback = check(os.path.join(top, path))
                sys.stdout.write("# " + path + "\n")
                sys.stdout.writelines(feedback)
            except LookupError as e:
                logger.debug(e)
        sys.stdout.write("\n")
