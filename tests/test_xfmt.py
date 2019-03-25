"""
This is for pytest to find and stop being upset not finding any tests.

>>> 'Happy?'[:-1]
'Happy'
"""
# pylint: disable=C0111,W0621
import os
from contextlib import contextmanager

import pytest  # type: ignore

from xfmt import json_fmt, misc

_BAD_SAMPELS = [
    "mumbo_jumbo.json",
    "nested_directory/argle_bargle.json",
    "short_and_squat.py",
]
_GOOD_SAMPLES = ["spruce.json", "great_and_small.py"]
_OTHER_SAMPLES = ["nesbitt.sh", "conifer.tree", "nested_directory/evergreen.tree"]
_SAMPLES_PATH = os.path.normpath(os.path.join(__file__, "..", "..", "samples"))


@contextmanager
def change_working_directory(new_path):
    old_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(old_path)


@pytest.fixture()
def formatters():
    yield misc.get_formatters()


def test_collect_finds_expected_samples():
    # Sort to ignore order of paths
    # Use lists, instead of say sets, to pay attention to number of occurrences
    expected = sorted(_BAD_SAMPELS + _GOOD_SAMPLES + _OTHER_SAMPLES)
    actual = sorted(misc.collect(_SAMPLES_PATH))

    assert actual == expected


@pytest.mark.xfail
def test_collect_includes_links_terminating_inside_working_directory():
    with change_working_directory(_SAMPLES_PATH):
        files = set(misc.collect(_SAMPLES_PATH))

    assert "nested_directory/argle_bargle.json" in files
    assert "nested_directory/evergreen.tree" in files


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize("path", _BAD_SAMPELS + _GOOD_SAMPLES + _OTHER_SAMPLES)
def test_collect_on_file_inside_working_directory_returns_file(path):
    expected = [path]
    actual = list(misc.collect(path))

    assert actual == expected


# Files outside the repository should be considered unsafe to write to and therefore to
# collect because they may not be under version control and the user may be unaware
# that running the formatter may change them.
# The working directory is used as a proxy for repository root.
# TODO: Consider making `.git` off limits


@pytest.mark.xfail(strict=True)
def test_collect_excludes_links_terminating_outside_working_directory():
    with change_working_directory(os.path.join(_SAMPLES_PATH, "nested_directory")):
        files = set(misc.collect(_SAMPLES_PATH))

    assert "argle_bargle.json" in files
    assert "evergreen.tree" not in files


@pytest.mark.xfail(strict=True)
def test_collect_on_file_outside_working_directory_raises():
    with change_working_directory(os.path.join(_SAMPLES_PATH, "nested_directory")):
        with pytest.raises(Exception):
            misc.collect("evergreen.tree")


def test_get_formatters_finds_all_formatters(formatters):
    types = {type(f) for f in formatters}
    assert json_fmt.JsonFormatter in types


@pytest.mark.parametrize("relpath", _BAD_SAMPELS)
def test_check_fails_bad_samples(relpath, formatters):
    assert misc.check(os.path.join(_SAMPLES_PATH, relpath), formatters, False)


@pytest.mark.parametrize("relpath", _GOOD_SAMPLES)
def test_check_passes_good_samples(relpath, formatters):
    assert not misc.check(os.path.join(_SAMPLES_PATH, relpath), formatters, False)


@pytest.mark.parametrize("relpath", _OTHER_SAMPLES)
def test_check_raises_on_other_samples(relpath, formatters):
    with pytest.raises(LookupError):
        misc.check(os.path.join(_SAMPLES_PATH, relpath), formatters, False)
