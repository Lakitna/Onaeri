import pytest
from ..Onaeri import helper
from ..Onaeri import settings

scale_test_cases = (
    ("comment", "test_input", "expected_result"),
    [
        ("valid", [94, (0, 500), (0, 13)], 2),
        ("valid_single_decimal", [94, (0, 500), (0, 13), 1], 2.4),
        ("valid_tripple_decimal", [94, (0, 500), (0, 13), 3], 2.444),
        ("none", [None, (), ()], None),
    ]
)


@pytest.mark.parametrize(*scale_test_cases)
def test_scale(comment, test_input, expected_result):
    assert helper.scale(*test_input) == expected_result


sequence_resize_test_cases = (
    ("comment", "test_input", "expected_result"),
    [
        (
            "too small",
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1],
            [0]
        ),
        (
            "shrink",
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 4],
            [0, 3, 6, 9]
        ),
        (
            "keep",
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 10],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        ),
        (
            "double",
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 20],
            [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
        ),
        (
            "expand",
            [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 15],
            [0, 1, 1, 2, 3, 3, 4, 4, 5, 6, 6, 7, 8, 8, 9]
        ),
    ]
)


@pytest.mark.parametrize(*sequence_resize_test_cases)
def test_sequenceResize(comment, test_input, expected_result):
    assert helper.sequenceResize(*test_input) == expected_result


limit_to_test_cases = (
    ("comment", "test_input", "expected_result"),
    [
        ("upper limit", [1000, (0, 500)], 500),
        ("lower limit", [10, (100, 500)], 100),
        ("negative lower limit", [-100, (-10, 500)], -10),
        ("inrange", [13, (0, 500)], 13),
        ("none", [None, (0, 500)], None),
    ]
)


@pytest.mark.parametrize(*limit_to_test_cases)
def test_limitTo(comment, test_input, expected_result):
    assert helper.limitTo(*test_input) == expected_result


timecode_range_test_cases = (
    ("comment", "test_input", "expected_result"),
    [
        ("basic", [10, 20], [(10, 20)]),
        ("compound range", [90, 20], [(90, 100), (0, 20)]),
        ("negative range left", [-10, 20], [(90, 100), (0, 20)]),
        ("negative range both", [-10, -5], [(90, 95)]),
        ("edges", [0, 100], [(0, 100)]),
        ("overflow", [5, 110], [(5, 10)]),
        ("edgecase", [100, 1], [(0, 1)]),
    ]
)


@pytest.mark.parametrize(*timecode_range_test_cases)
def test_timecodeRange(comment, test_input, expected_result):
    assert helper.timecodeRange(*test_input, rngeMax=100) == expected_result


inrange_test_cases = (
    ("comment", "test_input", "expected_result"),
    [
        ("none",
            [None, (0, 100)], False),
        ("wrong range",
            [50, [(0, 10, 20)]], False),

        ("basic",
            [5, (0, 100)], True),
        ("upper edge in",
            [100, (0, 100)], True),
        ("upper edge out",
            [101, (0, 100)], False),
        ("lower edge in",
            [0, (0, 100)], True),
        ("lower edge out",
            [-1, (0, 100)], False),

        ("compound basic first range",
            [5, [(0, 9), (11, 20)]], True),
        ("compound basic second range",
            [15, [(0, 9), (11, 20)]], True),
        ("compound basic between",
            [10, [(0, 9), (11, 20)]], False),
        ("compound upper edge in",
            [20, [(0, 9), (11, 20)]], True),
        ("compound upper edge out",
            [21, [(0, 9), (11, 20)]], False),
        ("compound lower edge in",
            [0, [(0, 9), (11, 20)]], True),
        ("compound lower edge out",
            [-1, [(0, 9), (11, 20)]], False),
    ]
)


@pytest.mark.parametrize(*inrange_test_cases)
def test_inRange(comment, test_input, expected_result):
    assert helper.inRange(*test_input) == expected_result


timecode_wrap_test_cases = (
    ("comment", "test_input", "expected_result"),
    [
        ("nowrap", [50], 50),
        ("bottom wrap", [-5], 95),
        ("top wrap", [105], 5),
        ("bottom edge", [0], 0),
        ("top edge", [100], 100),
    ]
)


@pytest.mark.parametrize(*timecode_wrap_test_cases)
def test_timecodeWrap(comment, test_input, expected_result):
    assert helper.timecodeWrap(*test_input, rngeMax=100) == expected_result
