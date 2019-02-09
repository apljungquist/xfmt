"""
This is for pytest to find and stop being upset not finding any tests.

>>> 'Happy?'[:-1]
'Happy'
"""

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


def test_collect_finds_all_samples():  # pylint: disable=C0111
    # Sort to ignore order of paths
    # Use lists, instead of say sets, to pay attention to number of occurrences
    expected = sorted(_BAD_SAMPELS + _GOOD_SAMPLES + _OTHER_SAMPLES)
    actual = sorted(main.collect(_SAMPLES_PATH))

    assert actual == expected


@pytest.mark.parametrize('relpath', _BAD_SAMPELS)
def test_check_fails_bad_samples(relpath):  # pylint: disable=C0111
    assert main.check(os.path.join(_SAMPLES_PATH, relpath))


@pytest.mark.parametrize('relpath', _GOOD_SAMPLES)
def test_check_passes_good_samples(relpath):  # pylint: disable=C0111
    assert not main.check(os.path.join(_SAMPLES_PATH, relpath))


@pytest.mark.parametrize('relpath', _OTHER_SAMPLES)
def test_check_raises_on_other_samples(relpath):  # pylint: disable=C0111
    with pytest.raises(LookupError):
        main.check(os.path.join(_SAMPLES_PATH, relpath))
