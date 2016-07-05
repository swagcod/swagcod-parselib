from swagcod.parselib import *

import pytest

@parser
def two_char_parser(state, input):
    _, state, input = accept_specific('h')(state, input)
    _, state, input = accept_specific('h')(state, input)
    return 'hh', state, input

def test_parse_all():
    with pytest.raises(ParseConsumeError):
        parse_all(accept_any(), 'hh')

def test_backtracking_behavior():

    assert parse_all(two_char_parser(), 'hh') == 'hh'

    with pytest.raises(ParseNoApply):
        parse_all(two_char_parser(), 'gg')

    with pytest.raises(ParseBacktrackError):
        parse_all(two_char_parser(), 'hg')

def test_attempt():
    with pytest.raises(ParseNoApply):
        parse_all(attempt(two_char_parser()), 'hg')
    
def test_accept_any():
    assert parse_all(accept_any(), 'h') == 'h'
    assert parse_some(accept_any(), 'hhh') == 'h'
    with pytest.raises(ParseNoApply):
        parse_all(accept_any(), '')

def test_accept_condition():
    condition = lambda c: c == 'g' or c == 'h'
    parser = accept_condition(condition)
    assert parse_all(parser, 'h') == 'h'
    assert parse_all(parser, 'g') == 'g'
    with pytest.raises(ParseNoApply):
        parse_all(parser, 'f')

def test_accept_specific():
    parser = accept_specific('h')
    assert parse_all(parser, 'h') == 'h'
    with pytest.raises(ParseNoApply):
        parse_all(parser, 'g')

def test_accept_specific_multi():
    parser = accept_specific_multi('hh')
    assert parse_all(parser, 'hh') == ['h', 'h']

    with pytest.raises(ParseNoApply):
        parse_all(parser, 'gg')
    
    # Multi should backtrack by default.
    with pytest.raises(ParseNoApply):
        parse_all(parser, 'hg')

def test_accept_type():
    parser = accept_type(int)
    assert parse_all(parser, [5]) == 5
    with pytest.raises(ParseNoApply):
        parse_all(parser, ['5'])

def test_accept_many():
    parser = accept_many(accept_specific('h'))
    assert parse_all(parser, 'hhh') == ['h', 'h', 'h']
    assert parse_some(parser, 'hhg') == ['h', 'h']
    assert parse_all(parser, '') == []
    assert parse_some(parser, '') == []

def test_accept_many1():
    parser = accept_many1(accept_specific('h'))
    assert parse_all(parser, 'hhh') == ['h', 'h', 'h']
    assert parse_some(parser, 'hhg') == ['h', 'h']

    with pytest.raises(ParseNoApply):
        parse_all(parser, 'g')

    with pytest.raises(ParseNoApply):
        parse_all(parser, '')

def test_choice():
    parser = accept_choice([
        accept_specific('g'),
        accept_specific('h'),
    ])

    assert parse_all(parser, 'h') == 'h'
    assert parse_all(parser, 'g') == 'g'

    with pytest.raises(ParseNoApply):
        parse_all(parser, 'f')
