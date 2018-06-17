import pytest
import os
from ..Onaeri import data


def test_data_exposed_to_namespace():
    module = data.__dict__

    for key in data.required:
        assert key in list(module.keys())


def test_retrieve_file_names():
    test_folder = os.path.dirname(os.path.abspath(__file__))

    test_files = data.retrieve_file_names(test_folder)

    file_names = [f['name'] for f in test_files]
    assert len(file_names) > 0
    assert __name__.split(".")[-1] in file_names


valid_file_test_cases = (
    ("comment", "input", "expected"),
    [
        (
            "Happy non-required",
            {'name': 'test', 'extention': 'json', 'path': 'data/test.json'},
            True
        ),
        (
            "No path",
            {'name': 'test', 'extention': 'json', 'path': ''},
            False
        ),
        (
            "No name",
            {'name': '', 'extention': 'json', 'path': 'data/.json'},
            False
        ),
        (
            "No extention",
            {'name': 'test', 'extention': '', 'path': 'data/test.json'},
            False
        ),
        (
            "Wrong extention",
            {'name': 'test', 'extention': 'py', 'path': 'data/test.py'},
            False
        ),
    ]
)


@pytest.mark.parametrize(*valid_file_test_cases)
def test_valid_file(comment, input, expected):
    assert data.valid_file(input) == expected


def test_valid_file_happy_required():
    required = ['test']
    input = {'name': 'test', 'extention': 'json', 'path': 'data/test.json'}
    assert data.valid_file(input, required=required) is True


def test_valid_file_required_list_emptied():
    required = ['test', 'someString', 'anotherString']

    input = {'name': 'test', 'extention': 'json', 'path': 'data/test.json'}
    assert data.valid_file(input, required=required)
    input = {
        'name': 'someString',
        'extention': 'json',
        'path': 'data/someString.json'
    }
    assert data.valid_file(input, required=required)

    assert len(required) == 1
    assert 'anotherString' in required


@pytest.mark.skip(reason="Requires file operations")
def test_expose_json_file_to_namespace():
    pass


validate_required_data_test_cases = (
    ("comment", "input", "expected"),
    [
        ("Happy", [], True),
        ("Sad", ["val"], False)
    ]
)


@pytest.mark.parametrize(*validate_required_data_test_cases)
def test_validate_required_data(comment, input, expected):
    assert data.validate_required_data(input) == expected
