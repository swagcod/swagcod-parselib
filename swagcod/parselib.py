class ParseNoApply(Exception):
    def __init__(self, remaining_input):
        self.remaining_input = remaining_input

class ParseError(Exception):
    pass

class ParseBacktrackError(ParseError):
    pass

class ParseConsumeError(ParseError):
    pass

# Turn a function into a parser.
#
# This wraps a parsing function (input -> output, remaining inputs) by ensuring that
# if a ParseNoApply is thrown and input was consumed, then we switch to a ParseError.
#
# The parsing function becomes "wrapped" and only takes one input (so to call it,
# it looks like parser(args)(input). Two layers of functions for extra fun.
def parser(func):
    def f(*args, **kwargs):
        def g(state, input):
            try:
                return func(state, input, *args, **kwargs)
            except ParseNoApply as err:
                if input != err.remaining_input:
                    raise ParseBacktrackError
                else:
                    raise
        return g
    return f

# Like parser, but allow backtracking by default. If you have a parser made with
# parser and want it to bactrack, see 'attempt'.
def backtrack_parser(func):
    def f(*args, **kwargs):
        def g(state, input):
            return func(state, input, *args, **kwargs)
        return g
    return f

# Make a 'parser behave like a 'backtrack_parser'
def attempt(parser):
    def g(state, input):
        try:
            return parser(state, input)
        except ParseBacktrackError:
            raise ParseNoApply(input)
    return g

def parse_some(parser, input, state=None):
    result, state, input = parser(state, input)
    return result

def parse_all(parser, input, state=None):
    result, state, input = parser(state, input)
    if input:
        raise ParseConsumeError
    return result

# Parser that accepts the first element, assuming it exists.
@parser
def accept_any(state, input):
    if not input:
        raise ParseNoApply(input)

    return input[0], state, input[1:]

# Parser that accepts the first element if it matches a condition lambda.
@parser
def accept_condition(state, input, condition):
    result, state, new_input = accept_any()(state, input)

    if not condition(result):
        raise ParseNoApply(input)

    else:
        return result, state, new_input

@parser
def accept_specific(state, input, specific):
    return accept_condition(lambda result: result == specific)(state, input)

@backtrack_parser
def accept_specific_multi(state, input, specific_multi):
    results = []
    for specific in specific_multi:
        result, state, input = accept_specific(specific)(state, input)
        results.append(result)

    return results, state, input

# Parser that accepts the first element if it is of a given type.
@parser
def accept_type(state, input, type):
    return accept_condition(lambda result: isinstance(result, type))(state, input)

# Parser that accepts as many of input as possible.
@parser
def accept_many(state, input, parser):
    results = []
    while input:
        try:
            result, state, new_input = parser(state, input)
            if new_input == input:
                raise RuntimeError('many loop')
            input = new_input
            results.append(result)
        except ParseNoApply:
            break

    return results, state, input

@parser
def accept_many1(state, input, parser):
    result, state, input = parser(state, input)
    results, state, input = accept_many(parser)(state, input)
    results.append(result)
    return results, state, input

@parser
def accept_choice(state, input, parser_list):
    for parser in parser_list:
        try:
            return parser(state, input)
        except ParseNoApply:
            pass

    raise ParseNoApply(input)
