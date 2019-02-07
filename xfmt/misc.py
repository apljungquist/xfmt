"""
Miscellaneous utilities
"""
import os

PROJECT_ABSPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def resource_abspath(relpath):
    """Get the absolute path of some resource within project

    :param relpath: resource path relative to project root
    :return: absolute resource path
    """
    return os.path.join(PROJECT_ABSPATH, relpath)
