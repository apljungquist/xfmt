import difflib
import json
import sys

JSON_PRETTY_KWARGS = {
    'indent': 4,
    'separators': (',', ': '),
    'sort_keys': True
}


def _fix_json(before: str) -> str:
    data = json.loads(before)
    after = json.dumps(data, **JSON_PRETTY_KWARGS)
    return after


def _check_json(before: str) -> bool:
    after = _fix_json(before)
    sys.stdout.writelines(difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile='actual',
        tofile='expected'
    ))
    return before == after
