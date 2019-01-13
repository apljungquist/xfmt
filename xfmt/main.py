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
    # TODO: Glob style rules that are aware of directory
    hits = [
        (pat, func) for pat, func
        in rules.items()
        if fnmatch.fnmatch(os.path.basename(filepath), pat)
    ]
    if len(hits) != 1:
        raise RuntimeError("Expected exactly one matching function but found %d", len(hits))
    return hits[0]


def _check_one(rules, filepath):
    logger.debug("Processing %s", filepath)
    pattern, func = _match_rule(rules, filepath)
    logger.debug("Matching pattern %s", pattern)
    with open(filepath, 'r') as fp:
        before = fp.read()
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
    with open(filepath, 'r') as fp:
        before = fp.read()
    after = func(before)
    with open(filepath, 'w') as fp:
        fp.write(after)
    logger.debug("File was %s", 'already pretty' if before == after else 'fixed')


def _fix_many(rules, filepaths):
    for filepath in filepaths:
        _fix_one(rules, filepath)


def _get_rules(category: str) -> Dict[str, Callable]:
    return {
        entry_point.name: entry_point.load()
        for entry_point in pkg_resources.iter_entry_points('xfmt.{}'.format(category))
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
    except Exception as e:
        logger.error(repr(e))
        raise
        exit(1)
    exit(0)


@click.command()
@click.argument('pattern', type=click.STRING)
@click.option('--fix', is_flag=True, default=False)
def main(pattern, fix):
    with _exit_codes():
        logging.basicConfig(level=logging.DEBUG)
        _main(pattern, fix)
