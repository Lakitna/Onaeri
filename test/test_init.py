from .. import Onaeri
from ..lamp import Lamp
from .. import settings


def test_init():
    features = {'dim': True, 'temp': True, 'color': False}
    devices = [
        Lamp(100, 50, True, name="Template One", features=features),
        Lamp(80, 50, True, name="Template Two", features=features),
        Lamp(50, 50, True, name="Template Three", features=features),
        Lamp(30, 50, True, name="Template Four", features=features),
    ]
    settings.cycles = ["Template"]
    settings.dynamic._reset("Template One")
    settings.dynamic._reset("Template Two")
    settings.dynamic._reset("Template Three")
    settings.dynamic._reset("Template Four")

    o = Onaeri(devices)
    assert len(o.cycles) == len(settings.cycles)
    assert len(o.devices) == len(devices)


def test_tick(capsys):
    features = {'dim': True, 'temp': True, 'color': False}
    devices = [
        Lamp(100, 50, True, name="Template One", features=features),
        Lamp(80, 50, True, name="Template Two", features=features),
        Lamp(50, 50, True, name="Template Three", features=features),
        Lamp(30, 50, True, name="Template Four", features=features),
    ]
    settings.cycles = ["Template"]
    settings.dynamic._reset("Template One")
    settings.dynamic._reset("Template Two")
    settings.dynamic._reset("Template Three")
    settings.dynamic._reset("Template Four")

    o = Onaeri(devices)

    o.tick(devices)
    o.tick(devices)
    assert o.update is False
    o.tick(None)
    assert o.update is False

    devices = [
        Lamp(10, 85, True, name="Template One"),
        Lamp(5, 8, True, name="Template Two"),
        Lamp(7, 6, False, name="Template Three"),
        Lamp(9, 4, True, name="Template Four"),
    ]
    o.tick(devices)
    assert o.update is True
