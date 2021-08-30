from uctypes import *

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
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno = t.value.count('\n')

def t_error(t):
    # print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build lexer
import ply.lex as lex

start = 'program'
lexer = lex.lex()

# Global-scope declarations
declarations = {}

# Empty production rule
def p_epsilon(p):
    'epsilon :'
    pass

def p_program(p):
    'program : LBRACE declarations statements RBRACE'
    p[0] = [p[2], p[3]]

# Declarations
def p_declarations(p):
    '''declarations : declaration SEMICOLON declarations
                    | epsilon'''
    pass

def p_declaration(p):
    '''declaration : var_declaration
                   | array_var_declaration
                   | record_var_declaration'''
    pass

def p_var_declaration(p):
    '''var_declaration : INT IDENTIFIER'''
    p[0] = UCVariable(p[1], p[2])
    declarations[p[2]] = p[0]
    print(p[0])

def p_fst_var_declaration(p):
    '''fst_var_declaration : INT FST'''
    p[0] = UCVariable(p[1], p[2])
    print(p[0])

def p_snd_var_declaration(p):
    '''snd_var_declaration : INT SND'''
    p[0] = UCVariable(p[1], p[2])
    print(p[0])

def p_array_var_declaration(p):
    '''array_var_declaration : INT LBRACKET LITERAL RBRACKET IDENTIFIER'''
    p[0] = UCArray(p[1], p[5], int(p[3])) 
    declarations[p[5]] = p[0]
    print(p[0])

def p_record_var_declaration(p):
    '''record_var_declaration : LBRACE fst_var_declaration SEMICOLON snd_var_declaration RBRACE IDENTIFIER'''
    fst = p[2]
    snd = p[4]
    p[0] = UCRecord('record', p[6], {'fst': fst, 'snd': snd})
    declarations[p[6]] = p[0]
    print(p[0])

# Statements
def p_statements(p):
    '''statements : statement SEMICOLON statements
                  | epsilon'''
    pass

                #  | if_statement
                #  | if_else_statement
                #  | while_statement
                #  | call_statement
def p_statement(p):
    '''statement : assignment_statement
    '''
    pass

def p_assignment_statement(p):
    '''assignment_statement : lvalue EQQ rvalue'''
    p[1].value = p[3]
    p[0] = p[1]

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
    p[0] = declarations[p[1]].value['fst']

def p_snd_lvalue(p):
    '''snd_lvalue : IDENTIFIER DOT SND'''
    p[0] = declarations[p[1]].value['snd']

def p_arr_var_lvalue(p):
    '''arr_var_lvalue : IDENTIFIER LBRACKET LITERAL RBRACKET'''
    p[0] = declarations[p[1]].value[int(p[3])]

def p_rvalue(p):
    '''rvalue : LITERAL'''
    p[0] = int(p[1])

def p_error(t):
    print("Syntax error at '%s'" % t)

# Build parser
import ply.yacc as yacc

parser = yacc.yacc()

with open('test.txt', 'r') as f:
    src = f.read()
    parser.parse(src)

    for decl in declarations.values():
        print(decl)
