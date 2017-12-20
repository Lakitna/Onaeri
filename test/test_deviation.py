from .. import cycle
from .. import settings
from ..settings import Template as testSettings
from ..lamp import Lamp


def test_change():
    data = Lamp(50, 50, True)
    change = Lamp(100, 50, True)
    anatomy = {'morning': [(0, 10)],
               'day': [(10, 20)],
               'evening': [(20, 30)],
               'night': [(30, 40)]}
    settings.dynamic._reset("Template One")
    d = cycle.Deviation("Template One", anatomy, testSettings)
    d.change(data, change, 20)
    assert d.active is True
    assert d.setValues == {'brightness': 50, 'color': 0}
    assert d.values == {'brightness': 50, 'color': 0}

    data = Lamp(50, 50, True)
    change = Lamp(55, 49, True)
    d = cycle.Deviation("Template One", anatomy, testSettings)
    d.change(data, change, 20)
    assert d.active is False
    assert d.setValues == {'brightness': 5, 'color': -1}
    assert d.values == {'brightness': 0, 'color': 0}


def test_apply():
    data = Lamp(50, 50, True)
    change = Lamp(100, 50, True)
    anatomy = {'morning': [(0, 10)],
               'day': [(10, 20)],
               'evening': [(20, 30)],
               'night': [(30, 40)]}
    settings.dynamic._reset("Template One")
    d = cycle.Deviation("Template One", anatomy, testSettings)
    d.change(data, change, 20)

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
