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
import pkg_resources
from xfmt import base

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


def check(path: str, checkers: List[base.Checker]) -> List[str]:
    """Check format of file.
    """
    assert checkers
    checker_matched = False
    feedback = []  # type:  List[str]
    for checker in checkers:
        if checker.match(path):
            checker_matched = True
            feedback.extend(checker.check(path))

    if not checker_matched:
        raise LookupError("Path did not match any pattern")

    return feedback


@contextlib.contextmanager
def _exit_codes():
    try:
        yield
    except Exception as e:  # pylint: disable=W0703
        logger.critical(e)
        exit(1)
    exit(0)


def _gen_checkers() -> Iterable[base.Checker]:
    for entry_point in pkg_resources.iter_entry_points('xfmt.checker'):
        factory_func = entry_point.load()
        yield factory_func()


def get_checkers():
    """Instantiate all registered checkers.
    """
    return list(_gen_checkers())


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
        checkers = get_checkers()
        for path in collect(top):
            logger.info("Checking %s", path)
            try:
                feedback = check(os.path.join(top, path), checkers)
                sys.stdout.write("# " + path + "\n")
                sys.stdout.writelines(feedback)
            except LookupError as e:
                logger.debug(e)
        sys.stdout.write("\n")
