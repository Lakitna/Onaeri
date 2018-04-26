import pytest
from ..Onaeri.timekeeper import TimeKeeper


@pytest.fixture
def timekeeper():
    return TimeKeeper()


def test_tick(timekeeper):
    timekeeper._minPerTimeCode = 1
    timekeeper.latestCode = 0
    timekeeper.runtime = 0

    timekeeper.tick()
    assert timekeeper.update is True
    assert timekeeper.runtime == 1

    timekeeper.tick()
    assert timekeeper.update is False
    assert timekeeper.runtime == 1


make_code_test_cases = (
    ("comment", "minPerTimeCode", "kwargs", "expected"),
    [
        ("basic hour", .1, {'h': 1}, 600),
        ("basic hour minute", .1, {'h': 1, 'm': 14}, 740),
        ("basic minute second", .1, {'s': 10, 'm': 14}, 141),

        ("complex hour", .123, {'h': 1}, 487),
        ("complex hour minute", .123, {'h': 1, 'm': 14}, 601),
        ("complex minute second", .123, {'s': 10, 'm': 14}, 115),

        ("syntactical hour tuple", .1, {'h': (1)}, 600),
        ("syntactical hour/minute tuple", .1, {'h': (1, 14)}, 740),
        ("syntactical hour/minute/second tuple", .1, {'h': (1, 14, 10)}, 741),
    ]
)


@pytest.mark.parametrize(*make_code_test_cases)
def test_make_code(comment, minPerTimeCode, kwargs, expected):
    timekeeper = TimeKeeper()
    timekeeper._minPerTimeCode = minPerTimeCode
    assert timekeeper.code(**kwargs) == expected
    assert timekeeper.latestCode == expected


def test_make_code_dry(timekeeper):
    timekeeper._minPerTimeCode = 1
    timekeeper.code(1)
    assert timekeeper.code(2, dry=True) == 120
    assert timekeeper.latestCode == 60


def test_timestamp_simple(timekeeper):
    timekeeper._minPerTimeCode = 1
    timekeeper.code(h=12, m=30, s=10)
    assert timekeeper.timestamp == "12:30:00"


def test_timestamp_with_seconds(timekeeper):
    timekeeper._minPerTimeCode = .123
    print(timekeeper.code(h=12, m=1, s=30))
    assert timekeeper.timestamp == "12:01:23"
