import pytest
from ..Onaeri.observer import Observer
from ..Onaeri.lamp import Lamp


@pytest.fixture
def observer():
    return Observer("test")


def test_init(observer):
    assert observer.data == Lamp()
    assert observer._cycleName == "test"


look_test_cases = (
    ("comment", "observer", "input", "expected"),
    [
        (
            "basic without update", observer(),
            [Lamp(100, 30, True)],
            {'data': Lamp(100, 30, True), 'update': False}
        ),
        (
            "none", observer(),
            [Lamp(100, 30, True), None],
            {'data': Lamp(100, 30, True), 'update': False}
        ),
        (
            "basic with update", observer(),
            [Lamp(100, 30, True), Lamp(70, 50, True)],
            {'data': Lamp(70, 50, True), 'update': True}
        ),
        (
            "update flag resets", observer(),
            [Lamp(100, 30, True), Lamp(70, 50, True), Lamp(70, 50, True)],
            {'data': Lamp(70, 50, True), 'update': False}
        ),
        (
            "power off", observer(),
            [Lamp(70, 50, True), Lamp(70, 50, False)],
            {'update': True, 'turnedOn': False, 'turnedOff': True}
        ),
        (
            "power on", observer(),
            [Lamp(70, 50, False), Lamp(70, 50, True)],
            {'update': True, 'turnedOn': True, 'turnedOff': False}
        ),
    ]
)


@pytest.mark.parametrize(*look_test_cases)
def test_lamp_value_setting(comment, observer, input, expected):
    for step in input:
        observer.look(step)

    for key, val in expected.items():
        assert getattr(observer, key) == val


def test_legal_change(observer):
    observer.look(Lamp(100, 50, True))  # init
    observer.look(Lamp(50, 50, True))  # Trigger update
    assert observer.update is True

    observer.legalChange
    observer.look(Lamp(10, 50, True))
    assert observer.update is False
