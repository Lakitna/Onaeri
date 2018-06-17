import pytest
from ..Onaeri.lookup import Lookup
from ..Onaeri.lamp import Lamp
from ..Onaeri.timekeeper import TimeKeeper

"""
It's hard to make automatic testers for Lookup. Visual inspection of the
generated lookup table works better and is therefore the preferred method.
"""


class Test_Settings:
    alarmTime = (5, 0)
    sleepTime = (23, 0)
    autoPowerOff = True
    autoPowerOn = True
    alarmOffset = 30
    windDownTime = 30

    morningSlopeDuration = 60
    eveningSlopeDuration = 120
    deviationDuration = 30


@pytest.fixture
def config():
    return Test_Settings()


@pytest.fixture
def lookup(config):
    tk = TimeKeeper(minpertimecode=1)
    return Lookup(config, timekeeper=tk, totaldatapoints=24 * 60)


def test_init(lookup, config):
    assert type(lookup.lamp) is Lamp
    assert type(lookup.time) is TimeKeeper
    assert lookup.config == config
    assert lookup._sleepTime == config.sleepTime[0] * 60
    assert lookup._alarmTime == config.alarmTime[0] * 60


get_from_table_mode_test_cases = (
    ("comment", "input", "expected_mode", "expected_period"),
    [
        (
            "darkMode midnight",
            0,
            "dark", "night"
        ),
        (
            "darkMode winddown night",
            config().sleepTime[0] * 60 + 1,
            "dark", "night"
        ),
        (
            "darkMode winddown evening",
            config().sleepTime[0] * 60 - config().windDownTime + 1,
            "dark", "evening"
        ),
        (
            "alert winddown evening",
            config().sleepTime[0] * 60 - config().windDownTime,
            "alert", "evening"
        ),
        (
            "noMode evening",
            config().sleepTime[0] * 60 - config().windDownTime - 1,
            None, "evening"
        ),
    ]
)


@pytest.mark.parametrize(*get_from_table_mode_test_cases)
def test_get_from_table_mode(comment, input, expected_mode, expected_period):
    look = lookup(config())
    assert look.table(input).mode == expected_mode
    assert look.get_period(input) == expected_period


current_period_test_cases = (
    ("comment", "timecode", "expected"),
    [
        ("midnight", 0, "night"),
        ("midday", 720, "day"),
        ("alarm", config().alarmTime[0] * 60, "morning"),
        ("bedtime", config().sleepTime[0] * 60, "evening"),
    ]
)


@pytest.mark.parametrize(*current_period_test_cases)
def test_current_period(comment, timecode, expected):
    look = lookup(config())
    assert look.get_period(timecode) == expected


def test_all_periods(lookup):
    for i in range(0, lookup.totalDataPoints + 1):
        assert len(lookup.get_period(i)) > 0
    assert lookup.get_period(lookup.totalDataPoints + 1) is None
    assert lookup.get_period(-1) is None


def test_buildAnatomy_continuity(lookup):
    result = lookup._buildAnatomy()

    assert result['morning'][0][0] == result['night'][-1][1]
    assert result['day'][0][0] == result['morning'][-1][1]
    assert result['evening'][0][0] == result['day'][-1][1]
    assert result['night'][0][0] == result['evening'][-1][1]
    assert result['night'][-1][0] == 0
    assert result['night'][0][1] == lookup.totalDataPoints


def test_buildTable(lookup):
    data = {
        'day': 1,
        'night': 2,
        'morning': (3, 3),
        'evening': (4, 4)
    }

    result = lookup._buildTable(data)

    expected_order = (2, 3, 1, 4, 2)
    lengths = [0] * len(expected_order)
    index = 0
    for val in result:
        a = False
        if val == expected_order[index]:
            a = True
        else:
            index += 1
            if val == expected_order[index]:
                a = True
        assert a
        lengths[index] += 1

    assert lengths[1] == lookup.config.morningSlopeDuration
    assert lengths[3] == lookup.config.eveningSlopeDuration
    assert sum(lengths) == lookup.totalDataPoints
