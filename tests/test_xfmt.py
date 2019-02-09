"""
This is for pytest to find and stop being upset not finding any tests.

>>> 'Happy?'[:-1]
'Happy'
"""
# pylint: disable=C0111,W0621
import os

import pytest  # type: ignore
from xfmt import main

_BAD_SAMPELS = [
    'mumbo_jumbo.json',
    'nested_directory/argle_bargle.json',
]
_GOOD_SAMPLES = [
    'spruce.json',
]
_OTHER_SAMPLES = [
    'nesbitt.sh',
]
_SAMPLES_PATH = os.path.normpath(os.path.join(__file__, '..', 'samples'))


@pytest.fixture()
def checkers():
    yield main.get_checkers()


def test_collect_finds_all_samples():
    # Sort to ignore order of paths
    # Use lists, instead of say sets, to pay attention to number of occurrences
    expected = sorted(_BAD_SAMPELS + _GOOD_SAMPLES + _OTHER_SAMPLES)
    actual = sorted(main.collect(_SAMPLES_PATH))

    assert actual == expected


@pytest.mark.parametrize('relpath', _BAD_SAMPELS)
def test_check_fails_bad_samples(relpath, checkers):
    assert main.check(os.path.join(_SAMPLES_PATH, relpath), checkers)


@pytest.mark.parametrize('relpath', _GOOD_SAMPLES)
def test_check_passes_good_samples(relpath, checkers):
    assert not main.check(os.path.join(_SAMPLES_PATH, relpath), checkers)


@pytest.mark.parametrize('relpath', _OTHER_SAMPLES)
def test_check_raises_on_other_samples(relpath, checkers):
    with pytest.raises(LookupError):
        main.check(os.path.join(_SAMPLES_PATH, relpath), checkers)
