from ..Onaeri.timekeeper import TimeKeeper


def test_tick():
    t = TimeKeeper()
    t._minPerTimeCode = 1
    t.latestCode = 0
    assert t.runtime == 0

    t.tick()
    assert t.update is True
    assert t.runtime == 1

    t.tick()
    assert t.update is False
    assert t.runtime == 1


def test_code():
    t = TimeKeeper()
    t._minPerTimeCode = .1
    assert t.code(h=1) == 600
    assert t.code(h=2) == 1200
    assert t.code(m=1) == 10

    t._minPerTimeCode = .123
    assert t.code(h=1) == 487
    assert t.code(h=2) == 975
    assert t.code(m=1) == 8

    t._minPerTimeCode = 2
    assert t.code(h=1) == 30
    assert t.code(h=2) == 60
    assert t.code(m=1) == 0

    for i in range(1, 30):
        t._minPerTimeCode = i / 10
        max = t.code(h=12, m=30)
        assert round(max * t._minPerTimeCode) in range(748, 752)


def test_timestamp():
    t = TimeKeeper()
    t._minPerTimeCode = 1
    t.code(h=12, m=30, s=10)
    assert t.timestamp() == "12:30:00"
    t.code(h=12, m=1, s=30)
    assert t.timestamp() == "12:01:00"
