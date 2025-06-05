import pytest
from unittest.mock import patch, mock_open

from led_command_parser import LEDCommandParser


@pytest.fixture
def parser():
    return LEDCommandParser(filename='dummy.json', NUM_LEDS=10)


def test_init_sets_attributes():
    parser = LEDCommandParser(filename='file.json', NUM_LEDS=42)
    assert parser.filename == 'file.json'
    assert parser.NUM_LEDS == 42
    assert parser.start_time == 0
    assert parser.schedule == {}


@pytest.mark.parametrize("led_ids,expected", [
    (["1"], [1]),
    (["2", "3"], [2, 3]),
    (["1*5"], [1, 2, 3, 4, 5]),
    (["*"], list(range(1, 10))),
    (["1*3", "5"], [1, 2, 3, 5]),
])
def test_expand_led_ids(parser, led_ids, expected):
    assert parser._expand_led_ids(led_ids) == expected


@pytest.mark.parametrize("cmd,expected", [
    ('instant', 0),
    ('fast_fade', 250),
    ('slow_fade', 1000),
    ('unknown', 0),
])
def test_parse_cmd_type(parser, cmd, expected, capsys):
    result = parser._parse_cmd_type(cmd)
    assert result == expected
    if cmd == 'unknown':
        captured = capsys.readouterr()
        assert "Unknown command type" in captured.out


def test_process_led_patch(parser):
    patch = [
        {'led_ids': ['1*4'], 'hsv': [0, 100, 100], 'type': 'fast_fade'},
        {'led_ids': ['7', '9'], 'hsv': [120, 100, 50]}
    ]
    result = parser._process_led_patch(patch)
    assert result == [
        {'led_ids': [1, 2, 3, 4], 'hsv': [0, 100, 100], 'delay': 250},
        {'led_ids': [7, 9], 'hsv': [120, 100, 50], 'delay': 0}
    ]


def test_parse(parser):
    fake_json = {
        'start': 123,
        'data': {
            '0': [
                {'led_ids': ['1'], 'hsv': [0, 0, 0], 'type': 'instant'}
            ],
            '10': [
                {'led_ids': ['2*7'], 'hsv': [120, 100, 100], 'type': 'slow_fade'}
            ]
        }
    }
    m = mock_open(read_data='{}')
    with patch('led_command_parser.json.load', return_value=fake_json), \
         patch('builtins.open', m):
        start_time, parsed = parser.parse()
        assert start_time == 123
        assert parsed == {
            0: [{'led_ids': [1], 'hsv': [0, 0, 0], 'delay': 0}],
            10: [{'led_ids': [2, 3, 4, 5, 6, 7], 'hsv': [120, 100, 100], 'delay': 1000}]
        }
