from uctypes import *
from ucops import *

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
    # op_a
    'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',
    # op_r
    'LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQ', 'EQQ',
    # op_b
    'AND', 'OR', # 'NOT',
)

t_PLUS  = r'\+'
t_MINUS = r'-'
t_MULT  = r'\*'
t_DIV   = r'/'
t_MOD   = r'%'

t_LT  = r'<'
t_GT  = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_EQ  = r'=='
t_NEQ = r'!='
t_EQQ = r':='

t_AND = r'&'
t_OR  = r'\|'
# t_NOT = '!'

tokens = (
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'DOT',
    'SEMICOLON',
    'IDENTIFIER',
    'LITERAL',
) + tuple(reserved.values()) + operators

t_LPAREN       = r'\('
t_RPAREN       = r'\)'
t_LBRACE       = r'{'
t_RBRACE       = r'}'
t_LBRACKET     = r'\['
t_RBRACKET     = r'\]'
t_DOT          = r'\.'
t_SEMICOLON    = r';'
t_LITERAL      = r'[0-9]+'

def t_IDENTIFIER(t):
    r'[_a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# Ignored chars
t_ignore = " \t\x0c"

def t_newline(t):
    r'\n+'
    t.lexer.lineno = t.value.count('\n')

def t_error(t):
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_comment(t):
    r'/{2,}.*'
    pass

# Build lexer
import ply.lex as lex

start = 'program'
lexer = lex.lex()

# Declarations and identifiers
declarations = {}
identifiers  = {}

# Empty production rule
def p_epsilon(p):
    'epsilon :'
    pass

def p_program(p):
    'program : LBRACE declarations statements RBRACE'
    p[2].children.reverse()
    p[3].children.reverse()
    p[0] = UCBlock(p[2], p[3])

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

def p_var_declaration(p):
    '''var_declaration : INT IDENTIFIER
                       | INT FST
                       | INT SND'''
    p[0] = UCVariable(p[1], UCIdentifier(p[2]))
    declarations[p[2]] = p[0]

def p_record_field_declaration(p):
    '''record_field_declaration : INT FST
                                | INT SND'''
    p[0] = UCField(p[1], UCIdentifier(p[2]))

# TODO: Obsolete
# def p_fst_var_declaration(p):
#     '''fst_var_declaration : INT FST'''
#     p[0] = UCVariable(p[1], UCIdentifier(p[2]))

# def p_snd_var_declaration(p):
#     '''snd_var_declaration : INT SND'''
#     p[0] = UCVariable(p[1], UCIdentifier(p[2]))

def p_array_var_declaration(p):
    '''array_var_declaration : INT LBRACKET LITERAL RBRACKET IDENTIFIER'''
    p[0] = UCArray(p[1], UCIdentifier(p[5]), UCNumberLiteral(p[3])) 
    declarations[p[5]] = p[0]

def p_record_var_declaration(p):
    '''record_var_declaration : LBRACE record_field_declaration SEMICOLON record_field_declaration RBRACE IDENTIFIER'''
    p[0] = UCRecord('record', p[6], [p[2], p[4]])
    declarations[p[6]] = p[0]

# Statements
def p_statements(p):
    '''statements : statement SEMICOLON statements
                  | epsilon'''
    if len(p) > 2:
        p[0] = p[3]
        p[0].add_child(p[1])
    else:
        p[0] = UCStatements()

                #  | if_statement
                #  | if_else_statement
                #  | while_statement
                #  | call_statement
def p_statement(p):
    '''statement : assignment_statement
    '''
    p[0] = p[1]

def p_assignment_statement(p):
    '''assignment_statement : lvalue EQQ rvalue
                            | lvalue EQQ lvalue'''
    # p[1].value = p[3]
    # p[0] = p[1]
    p[0] = UCEqq(p[1], p[3])

# Expressions
def p_lvalue(p):
    '''lvalue : id_lvalue
              | fst_lvalue
              | snd_lvalue
              | arr_var_lvalue'''
    p[0] = p[1]

def p_id_lvalue(p):
    '''id_lvalue : IDENTIFIER'''
    p[0] = declarations[p[1]]

def p_fst_lvalue(p):
    '''fst_lvalue : IDENTIFIER DOT FST'''
    # p[0] = declarations[p[1]].value['fst']
    p[0] = UCRecordDeref(declarations[p[1]], UCIdentifier(p[3]))

def p_snd_lvalue(p):
    '''snd_lvalue : IDENTIFIER DOT SND'''
    # p[0] = declarations[p[1]].value['snd']
    p[0] = UCRecordDeref(declarations[p[1]], UCIdentifier(p[3]))

def p_arr_var_lvalue(p):
    '''arr_var_lvalue : IDENTIFIER LBRACKET LITERAL RBRACKET'''
    # p[0] = declarations[p[1]].value[int(p[3])]
    p[0] = UCArrayDeref(declarations[p[1]], UCNumberLiteral(p[3]))

def p_rvalue(p):
    '''rvalue : literal_rvalue
              | op_a_expr_rvalue'''
    p[0] = p[1]

def p_literal_rvalue(p):
    '''literal_rvalue : LITERAL'''
    p[0] = UCNumberLiteral(p[1])

# TODO: Logical expressions

def p_op_a_expr_rvalue(p):
    '''op_a_expr_rvalue : lvalue op_a lvalue
                        | lvalue op_a rvalue
                        | rvalue op_a lvalue
                        | rvalue op_a rvalue'''
    p[0] = p[2](p[1], p[3])

def p_op_a(p):
    '''op_a : op_a_add
            | op_a_sub
            | op_a_mul
            | op_a_div
            | op_a_mod'''
    p[0] = p[1]

def p_op_a_add(p):
    '''op_a_add : PLUS'''
    p[0] = UCAdd

def p_op_a_sub(p):
    '''op_a_sub : MINUS'''
    p[0] = UCSub

def p_op_a_mul(p):
    '''op_a_mul : MULT'''
    p[0] = UCMul

def p_op_a_div(p):
    '''op_a_div : DIV'''
    p[0] = UCDiv

def p_op_a_mod(p):
    '''op_a_mod : MOD'''
    p[0] = UCMod

def p_error(t):
    print("Syntax error at '%s'" % t)

# Build parser
import ply.yacc as yacc

parser = yacc.yacc()

with open('test.txt', 'r') as f:
    src = f.read()
    ast = parser.parse(src)

    UCASTUtils.dfs_visit(ast)
