"""
Functions for collecting and running formatting tools on files.
"""
import contextlib
import fnmatch
import glob
import logging
import os
from typing import Callable, Dict

import click
import pkg_resources

logger = logging.getLogger(__name__)


def _match_rule(rules, filepath):
    hits = [(pat, func)
            for pat, func in rules.items()
            if fnmatch.fnmatch(os.path.basename(filepath), pat)]
    if len(hits) != 1:
        raise RuntimeError(
            "Expected exactly one matching function but found {}".format(len(hits))
        )
    return hits[0]


def _check_one(rules, filepath):
    logger.debug("Processing %s", filepath)
    pattern, func = _match_rule(rules, filepath)
    logger.debug("Matching pattern %s", pattern)
    with open(filepath, 'r') as f:
        before = f.read()
    retval = func(before)
    logger.debug("File was %s", 'pretty' if retval else 'ugly')
    return retval


def _check_many(rules, filepaths):
    retval = True
    for filepath in filepaths:
        if not _check_one(rules, filepath):
            retval = False
    return retval


def _fix_one(rules, filepath):
    logger.debug("Processing %s", filepath)
    pattern, func = _match_rule(rules, filepath)
    logger.debug("Matching pattern %s", pattern)
    with open(filepath, 'r') as f:
        before = f.read()
    after = func(before)
    with open(filepath, 'w') as f:
        f.write(after)
    logger.debug("File was %s", 'already pretty' if before == after else 'fixed')


def _fix_many(rules, filepaths):
    for filepath in filepaths:
        _fix_one(rules, filepath)


def _get_rules(category: str) -> Dict[str, Callable]:
    group = 'xfmt.{}'.format(category)
    return {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points(group)
    }


def _main(pattern, fix):
    filepaths = glob.iglob(pattern, recursive=True)

    if fix:
        rules = _get_rules('fixers')
        _fix_many(rules, filepaths)
    else:
        rules = _get_rules('checkers')
        _check_many(rules, filepaths)


@contextlib.contextmanager
def _exit_codes():
    try:
        yield
    except Exception as e:  # pylint: disable=W0703
        logger.error(repr(e))
        exit(1)
    exit(0)


@click.command()
@click.argument('pattern', type=click.STRING)
@click.option('--fix', is_flag=True, default=False)
def main(pattern, fix):
    """
    Attempt to process all files matching some pattern.
    """
    with _exit_codes():
        logging.basicConfig(level=logging.DEBUG)
        _main(pattern, fix)
