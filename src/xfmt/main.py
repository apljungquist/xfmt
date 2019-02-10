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
    """Collect file paths to be formatted.
    """
    if not os.path.isdir(top):
        if os.path.isfile(top):
            raise ValueError("Collecting from file is meaningless")
        else:
            raise RuntimeError("Huh? {}".format(top))
    paths = filter(os.path.isfile, glob.iglob(os.path.join(top, "**"), recursive=True))
    yield from (os.path.relpath(p, top) for p in paths)


def check(path: str, formatters: List[base.Formatter], fixes: bool) -> List[str]:
    """Check format of file.
    """
    assert formatters
    formatter_matched = False
    feedback = []  # type:  List[str]
    for formatter in formatters:
        if formatter.match(path):
            formatter_matched = True
            if fixes:
                feedback.extend(formatter.fix(path))
            else:
                feedback.extend(formatter.check(path))

    if not formatter_matched:
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


def _gen_formatters() -> Iterable[base.Formatter]:
    for entry_point in pkg_resources.iter_entry_points("xfmt.formatter"):
        factory_func = entry_point.load()
        yield factory_func()


def get_formatters():
    """Instantiate all registered formatters.
    """
    return list(_gen_formatters())


@click.command()
@click.argument("top", type=click.STRING)
@click.option("--fix", is_flag=True, default=False)
def main(top, fix):
    """Recursively check formatting of files under path
    """
    with _exit_codes():
        logging.basicConfig(
            level=logging.DEBUG, handlers=[logging.FileHandler("main.log")]
        )
        logger.info("Logging initialized at %s", datetime.now().isoformat())
        formatters = get_formatters()
        for path in collect(top):
            logger.info("Checking %s", path)
            try:
                feedback = check(os.path.join(top, path), formatters, fix)
                if feedback:
                    sys.stdout.writelines(feedback)
                    sys.stdout.write("\n")
            except LookupError as e:
                logger.debug(e)
