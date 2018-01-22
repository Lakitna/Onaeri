from ..Onaeri.lamp import Lamp


def test_set_get():
    lamp = Lamp()
    lamp.brightness = 10
    assert lamp.brightness == 10
    lamp.color = 20
    assert lamp.color == 20
    lamp.power = True
    assert lamp.power is True
    lamp.mode = 'hello'
    assert lamp.mode == 'hello'
    lamp.name = 'world'
    assert lamp.name == 'world'


def test_init():
    lamp = Lamp()
    assert lamp.brightness is None
    assert lamp.color is None
    assert lamp.power is None
    assert lamp.name is None
    assert lamp.mode is None

    lamp = Lamp(100, 90, True, "testName", "testMode")
    assert lamp.brightness == 100
    assert lamp.color == 90
    assert lamp.power is True
    assert lamp.name == "testName"
    assert lamp.mode == "testMode"


def test_call():
    lamp = Lamp(100, 90, True, "testName", "testMode")
    assert type(lamp()) is dict
    assert lamp()['brightness'] == 100


def test_eq():
    a = Lamp(100, 90, True, "testName", "testMode")
    b = Lamp(100, 90, True, "testName", "testMode")
    assert a == b
    b = Lamp(100, 95, True, "testName", "testMode")
    assert not a == b
    b = Lamp(50, 90, True, "testName", "testMode")
    assert not a == b
    b = Lamp(100, 90, False, "testName", "testMode")
    assert not a == b
    b = Lamp(100, 90, True, "Name", "Mode")
    assert a == b


def test_copy():
    a = Lamp(100, 90, True)
    b = Lamp()
    b.copy(a)
    assert b == a
    b = Lamp(20, 89, False)
    b.copy(a)
    assert b == a


def test_empty():
    lamp = Lamp(100, 50, False)
    assert lamp.isEmpty() is False
    lamp.empty()
    assert lamp.isEmpty() is True
    lamp = Lamp(100, None, None)
    assert lamp.isEmpty(['color', 'power']) is True
    assert lamp.isEmpty(['brightness', 'color']) is False
