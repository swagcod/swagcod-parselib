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
        def g(input):
            try:
                return func(input, *args, **kwargs)
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
        def g(input):
            return func(input, *args, **kwargs)
        return g
    return f

# Make a 'parser behave like a 'backtrack_parser'
def attempt(parser):
    def g(input):
        try:
            return parser(input)
        except ParseBacktrackError:
            raise ParseNoApply(input)
    return g

def parse_some(parser, input):
    result, input = parser(input)
    return result

def parse_all(parser, input):
    result, input = parser(input)
    if input:
        raise ParseConsumeError
    return result

@parser
def rewrite(input, output, parser):
    _, input = parser(input)
    return output, input

@parser
def rewrite_fn(input, f, parser):
    result, input = parser(input)
    return f(result), input

# Parser that accepts the first element, assuming it exists.
@parser
def accept_any(input):
    if not input:
        raise ParseNoApply(input)

    return input[0], input[1:]

@parser
def accept_input_condition(input, condition):
    if not condition(input):
        raise ParseNoApply(input)
    
    return result, new_input

# Parser that accepts the first element if it matches a condition lambda.
@parser
def accept_condition(input, condition):
    result, new_input = accept_any()(input)

    if not condition(result):
        raise ParseNoApply(input)

    else:
        return result, new_input

@parser
def accept_specific(input, specific):
    return accept_condition(lambda result: result == specific)(input)

@backtrack_parser
def accept_specific_multi(input, specific_multi):
    results = []
    for specific in specific_multi:
        result, input = accept_specific(specific)(input)
        results.append(result)

    return results, input

# Parser that accepts the first element if it is of a given type.
@parser
def accept_type(input, type):
    return accept_condition(lambda result: isinstance(result, type))(input)

# Parser that accepts as many of input as possible.
@parser
def accept_many(input, parser):
    results = []
    while input:
        try:
            result, new_input = parser(input)
            if new_input == input:
                raise RuntimeError('many loop')
            input = new_input
            results.append(result)
        except ParseNoApply:
            break

    return results, input

@parser
def accept_many1(input, parser):
    result, input = parser(input)
    results, input = accept_many(parser)(input)
    results.append(result)
    return results, input

@parser
def accept_choice(input, parser_list):
    for parser in parser_list:
        try:
            return parser(input)
        except ParseNoApply:
            pass

    raise ParseNoApply(input)
