from .. import helper


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
        0, 0, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 8, 9
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
