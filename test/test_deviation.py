from .. import cycle
from ..settings import Template as testSettings
from ..lamp import Lamp


def test_settings():
    assert type(testSettings.userAlarmTime) is tuple


def test_init():
    d = cycle.Deviation(testSettings)
    assert d.duration == testSettings.deviationDuration


def test_change():
    data = Lamp(50, 50, True)
    change = Lamp(100, 50, True)
    d = cycle.Deviation(testSettings)
    d.change(data, change)
    assert d.active is True
    assert d.setValues == {'brightness': 50, 'color': 0}
    assert d.values == {'brightness': 50, 'color': 0}

    data = Lamp(50, 50, True)
    change = Lamp(55, 49, True)
    d = cycle.Deviation(testSettings)
    d.change(data, change)
    assert d.active is False
    assert d.setValues == {'brightness': 5, 'color': -1}
    assert d.values == {'brightness': 0, 'color': 0}


def test_apply():
    data = Lamp(50, 50, True)
    change = Lamp(100, 50, True)
    d = cycle.Deviation(testSettings)
    d.change(data, change)

    for i in range(testSettings.deviationDuration):
        assert d.counter == i
        new = Lamp(50, 50, True)
        result = d.apply(new)
        if i == testSettings.deviationDuration:
            assert d.active is False
            assert d.values == {'brightness': 0, 'color': 0}
            assert d.setValues == {'brightness': 0, 'color': 0}
            assert result.brightness in range(50, 55)
            assert result.color == 50
