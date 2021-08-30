# from ply.lex import TOKEN

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
declarations = []

# Empty production rule
def p_epsilon(p):
    'epsilon :'
    pass

def p_program(p):
    'program : LBRACE declarations RBRACE'
    p[0] = [p[2], p[3]]

def p_declarations(p):
    '''declarations : declaration declarations
                    | epsilon'''
    pass

def p_declaration(p):
    '''declaration : var_declaration SEMICOLON
                   | array_var_declaration SEMICOLON
                   | record_var_declaration SEMICOLON'''
    pass

def p_var_declaration(p):
    '''var_declaration : INT IDENTIFIER'''
    p[0] = (p[1], p[2])

def p_fst_var_declaration(p):
    '''fst_var_declaration : INT FST'''
    p[0] = (p[1], p[2])

def p_snd_var_declaration(p):
    '''snd_var_declaration : INT SND'''
    p[0] = (p[1], p[2])

def p_array_var_declaration(p):
    '''array_var_declaration : INT LBRACKET LITERAL RBRACKET IDENTIFIER'''
    p[0] = (p[1], p[5], p[3])

def p_record_var_declaration(p):
    '''record_var_declaration : LBRACE fst_var_declaration SEMICOLON snd_var_declaration RBRACE IDENTIFIER'''
    pass

def p_error(t):
    print("Syntax error at '%s'" % t)

# Build parser
import ply.yacc as yacc

parser = yacc.yacc()

with open('test.txt', 'r') as f:
    src = f.read()
    parser.parse(src)

