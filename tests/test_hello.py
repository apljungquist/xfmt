import pytest
from sprig import hello


@pytest.mark.parametrize('lang', ['en', 'se'])
def test_supported_lang_prints(lang):
    assert hello.greet(lang)


def test_unsupported_lang_raises():
    with pytest.raises(ValueError):
        hello.greet('es')
