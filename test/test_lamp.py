from .. import lamp
import pytest


def test_set_get():
    l = lamp.Lamp()
    l.brightness = 10
    assert l.brightness == 10
    l.color = 20
    assert l.color == 20
    l.power = True
    assert l.power == True
    l.mode = 'hello'
    assert l.mode == 'hello'
    l.name = 'world'
    assert l.name == 'world'


def test_init():
    l = lamp.Lamp()
    assert l.brightness is None
    assert l.color is None
    assert l.power is None
    assert l.name is None
    assert l.mode is None

    l = lamp.Lamp(100, 90, True, "testName", "testMode")
    assert l.brightness == 100
    assert l.color == 90
    assert l.power is True
    assert l.name == "testName"
    assert l.mode == "testMode"


def test_call():
    l = lamp.Lamp(100, 90, True, "testName", "testMode")
    assert type(l()) is dict
    assert l()['brightness'] == 100


def test_eq():
    a = lamp.Lamp(100, 90, True, "testName", "testMode")
    b = lamp.Lamp(100, 90, True, "testName", "testMode")
    assert a == b
    b = lamp.Lamp(100, 95, True, "testName", "testMode")
    assert not a == b
    b = lamp.Lamp(50, 90, True, "testName", "testMode")
    assert not a == b
    b = lamp.Lamp(100, 90, False, "testName", "testMode")
    assert not a == b
    b = lamp.Lamp(100, 90, True, "Name", "Mode")
    assert a == b


def test_copy():
    a = lamp.Lamp(100, 90, True)
    b = lamp.Lamp()
    b.copy(a)
    assert b == a
    b = lamp.Lamp(20, 89, False)
    b.copy(a)
    assert b == a


def test_empty():
    l = lamp.Lamp(100, 50, False)
    assert l.isEmpty() is False
    l.empty()
    assert l.isEmpty() is True
    l = lamp.Lamp(100, None, None)
    assert l.isEmpty(['color', 'power']) is True
    assert l.isEmpty(['brightness', 'color']) is False
