from ..lookup import Lookup
from ..settings import Template as testSettings

"""
It's hard to make automatic testers for Lookup. Visual inspection of the
generated lookup table works better and is therefore the preferred method.
"""


def test_init():
    look = Lookup(testSettings)
    assert look.config == testSettings
    assert type(look.brightness) is list
    assert type(look.color) is list
    assert type(look.anatomy) is dict


def test_buildAnatomy(capsys):
    look = Lookup(testSettings)
    result = look._buildAnatomy()

    assert result['morning'][0][0] == result['night'][-1][1]
    assert result['day'][0][0] == result['morning'][-1][1]
    assert result['evening'][0][0] == result['day'][-1][1]
    assert result['night'][0][0] == result['evening'][-1][1]


def test_buildTable():
    data = {
        'day': 1,
        'night': 2,
        'morning': (3, 3),
        'evening': (4, 4)
    }

    testSettings.morningSlopeDuration = 60
    testSettings.eveningSlopeDuration = 60
    look = Lookup(testSettings)
    result = look._buildTable(data)

    expected_order = (2, 3, 1, 4, 2)
    index = 0
    for val in result:
        a = False
        if val == expected_order[index]:
            a = True
        else:
            index += 1
            if val == expected_order[index]:
                a = True
        assert a
