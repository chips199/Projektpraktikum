import pytest

def inc(x):
    return x + 1


def test_answer():
    pytest.assert inc(3) == 4
