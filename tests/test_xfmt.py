"""
This is for pytest to find and stop being upset not finding any tests.

>>> 'Happy?'[:-1]
'Happy'
"""
import glob
import os

from xfmt import main, misc


def test_samples_bad():
    samples_dirpath = misc.resource_abspath(os.path.join('tests', 'samples', 'bad'))
    good, bad = main.check_all(samples_dirpath)
    assert not good
    assert bad  # Test the test; if glob yields nothing the below would pass
    for filepath in glob.iglob(os.path.join(samples_dirpath, '*')):
        assert filepath in bad


def test_samples_good():
    samples_dirpath = misc.resource_abspath(os.path.join('tests', 'samples', 'good'))
    good, bad = main.check_all(samples_dirpath)
    assert not bad
    assert good  # Test the test; if glob yields nothing the below would pass
    for filepath in glob.iglob(os.path.join(samples_dirpath, '*')):
        assert filepath in good
