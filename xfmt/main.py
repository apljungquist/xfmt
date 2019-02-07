"""
Functions for collecting and running formatting tools on files.
"""
import glob
import logging
import os

from xfmt import json_fmt

logger = logging.getLogger(__name__)


def _gen_paths(path):
    if os.path.isdir(path):
        yield from glob.iglob(os.path.join(path, '*'))
    elif os.path.isfile(path):
        yield path
    elif not os.path.exists(path):
        raise RuntimeError("Path does not exist: {path}".format_map(locals()))
    else:
        raise RuntimeError("Unknown error")


def _check_one(path):
    _, ext = os.path.splitext(path)
    if ext == '.json':
        with open(path, 'r') as fp:
            return json_fmt.check_json(fp.read())
    else:
        logger.info("No matching extension for %s", path)
        return False


def check_all(path):
    """
    Check all files at or under path against matching formatter.

    :param path: The path to check
    :return: Two lists for passing and failing paths respectively
    """
    goods = []
    bads = []
    for filepath in _gen_paths(path):
        if _check_one(filepath):
            bads.append(filepath)
        else:
            goods.append(filepath)
    return goods, bads
