from ..lookup import Lookup
from ..settings import Template as testSettings

"""
It's hard to make automatic testers for Lookup. Visual inspection of the
generated lookup table works better and is therefore the preferred method.
"""


def test_init():
    l = Lookup(testSettings)
    assert l.config == testSettings
    assert type(l.brightness) is list
    assert type(l.color) is list


def test_buildTable(capsys):
    data = {
        'day': 1,
        'night': 2,
        'morning': (3, 3),
        'evening': (4, 4)
    }

    testSettings.morningSlopeDuration = 60
    testSettings.eveningSlopeDuration = 60
    l = Lookup(testSettings)
    result = l._buildTable(data)

    with capsys.disabled():
        expected_order = (2, 3, 1, 4, 2)
        index = 0
        for val in result:
            # print(val, index)
            a = False
            if val == expected_order[index]:
                a = True
            else:
                index += 1
                if val == expected_order[index]:
                    a = True
            assert a
