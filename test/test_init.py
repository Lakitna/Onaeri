from .. import Onaeri
from ..lamp import Lamp
from .. import settings


def test_init():
    devices = [
            Lamp(100, 50, True, name="Template One"),
            Lamp(80, 50, True, name="Template Two"),
            Lamp(50, 50, True, name="Template Three"),
            Lamp(30, 50, True, name="Template Four"),
        ]
    settings.cycles = ["Template"]
    o = Onaeri(devices)
    assert len(o.cycles) == len(settings.cycles)
    assert len(o.devices) == len(devices)


def test_tick(capsys):
    devices = [
            Lamp(100, 50, True, name="Template One"),
            Lamp(80, 50, True, name="Template Two"),
            Lamp(50, 50, True, name="Template Three"),
            Lamp(30, 50, True, name="Template Four"),
        ]
    settings.cycles = ["Template"]
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