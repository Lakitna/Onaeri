import pytest
from ..Onaeri.lamp import Lamp


set_get_test_cases = (
    ("variable", "comment", "test_input", "expected_result", "_assert"),
    [
        ("brightness", "valid int", 10, 10, True),
        ("brightness", "invalid int", 10, 11, False),
        ("brightness", "invalid int range", -1, -1, False),
        ("brightness", "invalid str", 'string', 'string', False),
        ("brightness", "none", None, None, True),

        ("color", "valid int", 20, 20, True),
        ("color", "invalid int", 20, 21, False),
        ("color", "invalid int range", -1, -1, False),
        ("color", "invalid str", 'string', 'string', False),
        ("color", "none", None, None, True),

        ("power", "valid bool", False, False, True),
        # ("power", "valid bool", True, True, True),
        ("power", "none", None, None, True),
        ("power", "invalid bool", True, False, False),
        ("power", "invalid str", 'string', 'string', False),

        ("mode", "valid int", 30, 30, True),
        ("mode", "valid str", 'randomString', 'randomString', True),
        ("mode", "none", None, None, True),

        ("name", "valid int", 30, 30, True),
        ("name", "valid str", 'randomString', 'randomString', True),
        ("name", "none", None, None, True),
    ]
)


@pytest.mark.parametrize(*set_get_test_cases)
def test_lamp_value_setting(variable, comment,
                            test_input, expected_result, _assert):
    lamp = Lamp()
    setattr(lamp, variable, test_input)
    assert _assert is (getattr(lamp, variable) == expected_result)


def test_init_empty():
    lamp = Lamp()
    assert lamp.brightness is None
    assert lamp.color is None
    assert lamp.power is None
    assert lamp.name is None
    assert lamp.mode is None


def test_init_filled():
    lamp = Lamp(100, 90, True, "testName", "testMode")
    assert lamp.brightness == 100
    assert lamp.color == 90
    assert lamp.power is True
    assert lamp.name == "testName"
    assert lamp.mode == "testMode"


def test_magic_call():
    lamp = Lamp(100, 90, True, "testName", "testMode")
    assert type(lamp()) is dict  # Correct type
    assert len(lamp()) == 8  # Correct length
    assert lamp()['brightness'] == 100  # Correctly callable


magic_eq_test_cases = (
    ("comment", "_assert", "test_input_a", "test_input_b"),
    [
        (
            "equal", True,
            [100, 90, True, "testName", "testMode"],
            [100, 90, True, "testName", "testMode"]
        ),
        (
            "inequal_brightness", False,
            [100, 90, True, "testName", "testMode"],
            [50, 90, True, "testName", "testMode"]
        ),
        (
            "inequal_color", False,
            [100, 90, True, "testName", "testMode"],
            [100, 100, True, "testName", "testMode"]
        ),
        (
            "inequal_power", False,
            [100, 90, True, "testName", "testMode"],
            [100, 90, False, "testName", "testMode"]
        ),
        (
            "inequal_name", True,
            [100, 90, True, "testName", "testMode"],
            [100, 90, True, "anotherName", "testMode"]
        ),
        (
            "inequal_mode", True,
            [100, 90, True, "testName", "testMode"],
            [100, 90, True, "testName", "anotherMode"]
        )
    ]
)


@pytest.mark.parametrize(*magic_eq_test_cases)
def test_magic_eq(comment, _assert,
                  test_input_a, test_input_b):
    a = Lamp(*test_input_a)
    b = Lamp(*test_input_b)
    assert _assert is (a == b)


def test_copy():
    a = Lamp(100, 90, True)
    b = Lamp()
    assert not b == a
    b.copy(a)
    assert b == a


def test_isempty_true():
    lamp = Lamp()
    assert lamp.isEmpty() is True


def test_isempty_false():
    lamp = Lamp(100, 90, True)
    assert lamp.isEmpty() is False


def test_isempty_subset():
    lamp = Lamp(100, 90, True)
    assert lamp.isEmpty(['mode', 'name']) is True
    assert lamp.isEmpty(['mode']) is True


def test_empty():
    lamp = Lamp(100, 50, False)
    assert lamp.isEmpty() is False
    lamp.empty()
    assert lamp.isEmpty() is True
    lamp = Lamp(100, 90, True)
    assert lamp.isEmpty() is False
    lamp.empty()
    assert lamp.isEmpty() is True
    lamp = Lamp(100, None, None)
    assert lamp.isEmpty(['color', 'power']) is True
    assert lamp.isEmpty(['brightness', 'color']) is False
