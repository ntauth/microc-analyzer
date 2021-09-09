"""TODO: Use lexer from lang.lex"""
import ply.lex as lex

from lang.types import *
from lang.ops import *


reserved = {
    # Control
    'if':    'IF',
    'else':  'ELSE',
    'while': 'WHILE',

    # Built-in types
    'int': 'INT',

    # Built-in functions
    'read':  'READ',
    'write': 'WRITE',

    # Constants
    'true':  'TRUE',
    'false': 'FALSE',

    # Reserved identifiers
    'fst':   'FST',
    'snd':   'SND',
}

operators = (
    'DOT',
    'LBRACKET', 'RBRACKET',
    # op_a
    'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',
    # op_r
    'LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQ', 'EQQ',
    # op_b
    'AND', 'OR', 'NOT',
)

t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_DOT = r'\.'

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'%'

t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_EQ = r'=='
t_NEQ = r'!='
t_EQQ = r':='

t_AND = r'&'
t_OR = r'\|'
t_NOT = r'!'

tokens = (
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'SEMICOLON',
    'IDENTIFIER',
    'NUM_LITERAL',
) + tuple(reserved.values()) + operators

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_COMMA = r','
t_SEMICOLON = r';'
t_NUM_LITERAL = r'[0-9]+'


def t_IDENTIFIER(t):
    r'[_a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# Ignored chars
t_ignore = " \t\x0c"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_comment(t):
    r'/{2,}[^\n\r]*'
    pass

# Helper functions
def find_column(input, t):
    line_start = input.rfind('\n', 0, t.lexpos) + 1
    return (t.lexpos - line_start) + 1


start = 'program'
lexer = lex.lex()


precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('right', 'NOT'),
)

# Declarations and identifiers
declarations = {}
identifiers = {}

# Empty production rule
def p_epsilon(p):
    'epsilon :'
    pass


def p_program(p):
    '''program : block program
               | epsilon'''
    if len(p) > 2:
        p[0] = p[2]
        p[0].add_child(p[1])
    else:
        p[0] = UCProgram()


def p_block(p):
    '''block : LBRACE declarations statements RBRACE'''
    p[2].children.reverse()
    p[3].children.reverse()
    p[0] = UCBlock(p[2], p[3])


def p_nested_block(p):
    '''nested_block : LBRACE statements RBRACE'''
    p[2].children.reverse()
    p[0] = UCNestedBlock(p[2])

# Declarations
def p_declarations(p):
    '''declarations : declaration SEMICOLON declarations
                    | epsilon'''
    if len(p) > 2:
        p[0] = p[3]
        p[0].add_child(p[1])
    else:
        p[0] = UCDeclarations()


def p_declaration(p):
    '''declaration : var_declaration
                   | array_var_declaration
                   | record_var_declaration'''
    p[0] = p[1]
    p[0].lineno = p.lineno(1)


def p_var_declaration(p):
    '''var_declaration : INT IDENTIFIER
                       | INT FST
                       | INT SND'''
    p[0] = UCVariable(p[1], UCIdentifier(p[2]))

    if p[2] in declarations:
        raise NameError('cannot redeclare `{}`'.format(p[2]))

    declarations[p[2]] = p[0]


def p_record_field_declaration(p):
    '''record_field_declaration : INT FST
                                | INT SND'''
    p[0] = UCField(p[1], UCIdentifier(p[2]))


def p_array_var_declaration(p):
    '''array_var_declaration : INT LBRACKET NUM_LITERAL RBRACKET IDENTIFIER'''
    p[0] = UCArray(p[1], UCIdentifier(p[5]), UCNumberLiteral(p[3]))

    if p[5] in declarations:
        raise NameError('cannot redeclare `{}`'.format(p[5]))

    declarations[p[5]] = p[0]


def p_record_var_declaration(p):
    '''record_var_declaration : LBRACE record_field_declaration SEMICOLON record_field_declaration RBRACE IDENTIFIER'''
    p[0] = UCRecord('record', UCIdentifier(p[6]), [p[2], p[4]])

    if p[6] in declarations:
        raise NameError('cannot redeclare `{}`'.format(p[6]))

    declarations[p[6]] = p[0]

# Statements
def p_statements(p):
    '''statements : statement statements
                  | statement'''
    if len(p) > 2:
        p[0] = p[2]
        p[0].add_child(p[1])
    else:
        p[0] = UCStatements()
        p[0].add_child(p[1])

def p_statement(p):
    '''statement : assignment_statement SEMICOLON
                 | if_statement
                 | if_else_statement
                 | while_statement
                 | call_statement SEMICOLON'''
    p[0] = p[1]
    p[0].lineno = p.lineno(1)


def p_assignment_statement(p):
    '''assignment_statement : lvalue EQQ a_expression'''
    # TODO: Check that assignment is semantically correct
    p[0] = UCAssignment(p[1], p[3])


def p_if_statement(p):
    '''if_statement : IF LPAREN b_expression RPAREN nested_block'''
    p[0] = UCIf(p[3], p[5])


def p_if_else_statement(p):
    '''if_else_statement : IF LPAREN b_expression RPAREN nested_block ELSE nested_block'''
    p[0] = UCIfElse(p[3], p[5], p[7])


def p_while_statement(p):
    '''while_statement : WHILE LPAREN b_expression RPAREN nested_block'''
    p[0] = UCWhile(p[3], p[5])


def p_call_statement(p):
    '''call_statement : READ l_expression
                      | WRITE a_expression'''
    p[0] = UCCall(UCBuiltinIdentifier(p[1]), p[2:])

# Expressions
def p_lvalue(p):
    '''lvalue : id_lvalue
              | fst_lvalue
              | snd_lvalue
              | arr_var_lvalue'''
    p[0] = p[1]


def p_id_lvalue(p):
    '''id_lvalue : IDENTIFIER'''
    p[0] = declarations[p[1]].id


def p_fst_lvalue(p):
    '''fst_lvalue : IDENTIFIER DOT FST'''
    # p[0] = declarations[p[1]].value['fst']
    p[0] = UCRecordDeref(declarations[p[1]].id, UCIdentifier(p[3]))


def p_snd_lvalue(p):
    '''snd_lvalue : IDENTIFIER DOT SND'''
    # p[0] = declarations[p[1]].value['snd']
    p[0] = UCRecordDeref(declarations[p[1]].id, UCIdentifier(p[3]))


def p_arr_var_lvalue(p):
    '''arr_var_lvalue : IDENTIFIER LBRACKET a_expression RBRACKET
    '''
    # p[0] = declarations[p[1]].value[int(p[3])]
    p[0] = UCArrayDeref(declarations[p[1]].id, p[3])


def p_a_rvalue(p):
    '''rvalue : number_literal
              | record_initializer_list'''
    p[0] = p[1]


def p_number_literal(p):
    '''number_literal : NUM_LITERAL'''
    p[0] = UCNumberLiteral(p[1])


def p_bool_literal(p):
    '''bool_literal : TRUE
                    | FALSE'''
    p[0] = UCBoolLiteral(p[1])


def p_record_initializer_list(p):
    '''record_initializer_list : LPAREN lvalue COMMA lvalue RPAREN
                               | LPAREN lvalue COMMA rvalue RPAREN
                               | LPAREN rvalue COMMA lvalue RPAREN
                               | LPAREN rvalue COMMA rvalue RPAREN'''
    p[0] = UCRecordInitializerList([p[2], p[4]])


def p_l_expression(p):
    '''l_expression : l_expression_unpacked
                    | LPAREN l_expression_unpacked RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

    p[0].lineno = p.lineno(0)


def p_l_expression_unpacked(p):
    '''l_expression_unpacked : lvalue'''
    p[0] = p[1]


def p_a_expression(p):
    '''a_expression : a_expression_unpacked
                    | l_expression
                    | LPAREN a_expression_unpacked RPAREN'''
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = p[1]

    p[0].lineno = p.lineno(0)


def p_a_expression_unpacked(p):
    '''a_expression_unpacked : rvalue 
                             | a_expression PLUS a_expression
                             | a_expression MINUS a_expression
                             | a_expression MULT a_expression
                             | a_expression DIV a_expression
                             | a_expression MOD a_expression'''
    if len(p) > 2:
        if p[2] == '+':
            p[0] = UCAdd(p[1], p[3])
        elif p[2] == '-':
            p[0] = UCSub(p[1], p[3])
        elif p[2] == '*':
            p[0] = UCMul(p[1], p[3])
        elif p[2] == '/':
            p[0] = UCDiv(p[1], p[3])
        elif p[2] == '%':
            p[0] = UCMod(p[1], p[3])
        else:
            assert False
    else:
        p[0] = p[1]


def p_b_expression(p):
    '''b_expression : b_expression_unpacked
                    | LPAREN b_expression_unpacked RPAREN'''
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = p[1]

    p[0].lineno = p.lineno(0)


def p_b_expression_unpacked(p):
    '''b_expression_unpacked : bool_literal
                             | a_expression LT a_expression
                             | a_expression GT a_expression
                             | a_expression LTE a_expression
                             | a_expression GTE a_expression
                             | a_expression EQ a_expression
                             | a_expression NEQ a_expression
                             | b_expression AND b_expression
                             | b_expression OR b_expression
                             | NOT b_expression'''
    if len(p) > 3:
        if p[2] == '&':
            p[0] = UCAnd(p[1], p[3])
        elif p[2] == '|':
            p[0] = UCOr(p[1], p[3])
        elif p[2] == '<':
            p[0] = UCLt(p[1], p[3])
        elif p[2] == '>':
            p[0] = UCGt(p[1], p[3])
        elif p[2] == '<=':
            p[0] = UCLte(p[1], p[3])
        elif p[2] == '>=':
            p[0] = UCGte(p[1], p[3])
        elif p[2] == '==':
            p[0] = UCEq(p[1], p[3])
        elif p[2] == '!=':
            p[0] = UCNeq(p[1], p[3])
        else:
            assert False
    elif len(p) > 2:
        p[0] = UCNot(p[2])
    else:
        p[0] = p[1]

# TODO: Obsolete
# def p_op_a(p):
#     '''op_a : op_a_add
#             | op_a_sub
#             | op_a_mul
#             | op_a_div
#             | op_a_mod'''
#     p[0] = p[1]


# def p_op_a_add(p):
#     '''op_a_add : PLUS'''
#     p[0] = UCAdd


# def p_op_a_sub(p):
#     '''op_a_sub : MINUS'''
#     p[0] = UCSub


# def p_op_a_mul(p):
#     '''op_a_mul : MULT'''
#     p[0] = UCMul


# def p_op_a_div(p):
#     '''op_a_div : DIV'''
#     p[0] = UCDiv


# def p_op_a_mod(p):
#     '''op_a_mod : MOD'''
#     p[0] = UCMod

# Relational operators
# def p_op_r(p):
#     '''op_r : op_r_lt
#             | op_r_lte
#             | op_r_gt
#             | op_r_gte
#             | op_r_eq
#             | op_r_neq'''
#     p[0] = p[1]


# def p_op_r_lt(p):
#     '''op_r_lt : LT'''
#     p[0] = UCLt


# def p_op_r_lte(p):
#     '''op_r_lte : LTE'''
#     p[0] = UCLte


# def p_op_r_gt(p):
#     '''op_r_gt : GT'''
#     p[0] = UCGt


# def p_op_r_gte(p):
#     '''op_r_gte : GTE'''
#     p[0] = UCGte


# def p_op_r_eq(p):
#     '''op_r_eq : EQ'''
#     p[0] = UCEq


# def p_op_r_neq(p):
#     '''op_r_neq : NEQ'''
#     p[0] = UCNeq

# Boolean operators
# def p_op_b(p):
#     '''op_b : op_b_and
#             | op_b_or
#             | op_b_not'''
#     p[0] = p[1]


# def p_op_b_and(p):
#     '''op_b_and : AND'''
#     p[0] = UCAnd


# def p_op_b_or(p):
#     '''op_b_or : OR'''
#     p[0] = UCOr


# def p_op_b_not(p):
#     '''op_b_not : NOT'''
#     p[0] = UCNot


def p_error(t):
    global src
    print("Syntax error at '%s' - Line %d, Column %d" %
          (t.value, lexer.lineno, find_column(src, t)))


def parse(uc_src):
    import networkx as nx
    import ply.yacc as yacc

    global src

    parser = yacc.yacc()

    src = uc_src
    ast = parser.parse(src, tracking=True)

    return ast
