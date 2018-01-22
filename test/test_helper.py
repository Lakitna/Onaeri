from ..Onaeri import helper
from ..Onaeri import settings


def test_scale():
    assert helper.scale(50, (0, 100), (0, 1000)) == 500
    assert helper.scale(94, (0, 500), (0, 13)) == 2
    assert helper.scale(94, (0, 500), (0, 13), 1) == 2.4
    assert helper.scale(94, (0, 500), (0, 13), 3) == 2.444
    assert type(helper.scale(100, (0, 500), (0, 20), 1)) is int


def test_sequenceResize():
    data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert helper.sequenceResize(data, 1) == [0]
    assert helper.sequenceResize(data, 10) == data
    assert helper.sequenceResize(data, 20) == [
        0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9
    ]
    assert helper.sequenceResize(data, 15) == [
        0, 1, 1, 2, 3, 3, 4, 4, 5, 6, 6, 7, 8, 8, 9
    ]


def test_limitTo():
    assert helper.limitTo(1000, (0, 500)) == 500
    assert helper.limitTo(13, (0, 500)) == 13
    assert helper.limitTo(10, (100, 500)) == 100


def test_inRange():
    assert helper.inRange(50, (0, 100)) is True
    assert helper.inRange(100, (0, 100)) is True
    assert helper.inRange(0, (0, 100)) is True
    assert helper.inRange(101, (0, 100)) is False
    assert helper.inRange(-3, (0, 100)) is False

    rnge = [(0, 9), (11, 20)]
    assert helper.inRange(5, rnge) is True
    assert helper.inRange(15, rnge) is True
    assert helper.inRange(10, rnge) is False
    assert helper.inRange(20, rnge) is True
    assert helper.inRange(9, rnge) is True
    assert helper.inRange(21, rnge) is False


def test_timecodeRange():
    store = settings.Global.totalDataPoints
    settings.Global.totalDataPoints = 100
    assert helper.timecodeRange(10, 20) == [(10, 20)]
    assert helper.timecodeRange(90, 20) == [(90, 100), (0, 20)]
    assert helper.timecodeRange(-10, 20) == [(90, 100), (0, 20)]
    assert helper.timecodeRange(-10, -5) == [(90, 95)]
    assert helper.timecodeRange(0, 100) == [(0, 100)]
    assert helper.timecodeRange(5, 110) == [(5, 10)]

    # Reset it for future tests
    settings.Global.totalDataPoints = store


def test_timecodeWrap():
    store = settings.Global.totalDataPoints
    settings.Global.totalDataPoints = 100

    assert helper.timecodeWrap(50) == 50
    assert helper.timecodeWrap(-5) == 95
    assert helper.timecodeWrap(105) == 5
    assert helper.timecodeWrap(0) == 0
    assert helper.timecodeWrap(100) == 100

    # Reset it for future tests
    settings.Global.totalDataPoints = store
