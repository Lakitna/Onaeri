from ..observer import Observer
from ..lamp import Lamp
import pytest


def test_init():
    o = Observer("test")
    assert o.data == Lamp()
    assert o._cycleName == "test"


def test_look(capsys):
    o = Observer("test")

    inp = Lamp(100, 50, True)
    o.look(inp)
    assert o.data == inp
    assert o.update == False

    inp = Lamp(70, 50, True)
    o.look(inp)
    assert o.data == inp
    assert o.update == True

    inp = Lamp(70, 50, True)
    o.look(inp)
    assert o.update == False
    assert o.turnedOn == False
    assert o.turnedOff == False

    inp = Lamp(70, 50, False)
    o.look(inp)
    assert o.update == True
    assert o.turnedOn == False
    assert o.turnedOff == True

    inp = Lamp(70, 50, True)
    o.look(inp)
    assert o.update == True
    assert o.turnedOn == True
    assert o.turnedOff == False
