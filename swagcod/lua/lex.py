from enum import Enum

from swagcod.token import *
from swagcod.parselib import *


def lex(input):
    return parse_all(accept_tokens(), input)

@parser
def accept_tokens(input):
    return accept_many(accept_tokens())(input)

@parser
def accept_token(input):
    return accept_choice([
        accept_block_comment_start(),
        accept_line_comment_start(),
        accept_many1_whitespace(),
        accept_int_lit(),
        accept_string_lit(),
        accept_keyword_local,
        accept_left_brace(),
        accept_right_brace(),
        accept_left_bracket(),
        accept_right_bracket(),
        accept_ident(),
    ])(input)

@parser
def accept_line_comment(input):
    _, input = accept_specific_multi('--')(input)
    _, input = accept_many(accept_condition(lambda c: c != '\n'))(input)
    _, input = accept_specific('\n')(input)
    return LTNothing(), input

@parser
def accept_block_comment(input):
    _, input = accept_specific_multi('--[[')(input)
    _, input = accept_many(accept_input_condition(lambda s: not s.startswith('--]]')))(input)
    _, input = accept_specific_multi('--]]')(input)

@parser
def accept_many1_whitespace(input):
    return rewrite(
        LTNothing(),
        accept_many1(accept_condition(lambda c: c.isspace()))(input),
    )

@parser
def accept_int_lit(input):
    return rewrite_fn(
        lambda lst: LTIntLit(int(''.join(lst))),
        accept_many1(accept_condition(lambda c: c.isdigit())),
    )

@parser
def accept_ident(input):
    first_char, input = accept_condition(lambda c: c.isalpha() or c == '_'))(input)
    remainder, input = rewrite_fn(
        ''.join
        accept_many1(accept_condition(lambda c: c.isalnum() or c == '_'))(input)
    return LTIdent(first_char + remainder), input

@parser
def accept_string_lit(input):
    _, input = accept_specific('"')(input)
    string_lit, input = rewrite_fn(''.join, accept_many(accept_condition(lambda c: c != '\n')))(input)
    _, input = accept_specific('"')(input)
    return LTStringLit(string_lit)

accept_keyword_local = rewrite(LTKWLocal(), accept_specific_multi('local'))
accept_left_brace = rewrite(LTLeftBrace(), accept_specific('{'))
accept_right_brace = rewrite(LTRightBrace(), accept_specific('}'))
accept_left_bracket = rewrite(LTLeftBracket(), accept_specific('['))
accept_right_bracket = rewrite(LTRightBracket(), accept_specific(']'))
    
