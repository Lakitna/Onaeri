from ..observer import Observer
from ..lamp import Lamp


def test_init():
    o = Observer("test")
    assert o.data == Lamp()
    assert o._cycleName == "test"


def test_look(capsys):
    o = Observer("test")

    inp = Lamp(100, 50, True)
    o.look(inp)
    assert o.data == inp
    assert o.update is False

    inp = Lamp(70, 50, True)
    o.look(inp)
    assert o.data == inp
    assert o.update is True

    inp = Lamp(70, 50, True)
    o.look(inp)
    assert o.update is False
    assert o.turnedOn is False
    assert o.turnedOff is False

    inp = Lamp(70, 50, False)
    o.look(inp)
    assert o.update is True
    assert o.turnedOn is False
    assert o.turnedOff is True

    inp = Lamp(70, 50, True)
    o.look(inp)
    assert o.update is True
    assert o.turnedOn is True
    assert o.turnedOff is False
