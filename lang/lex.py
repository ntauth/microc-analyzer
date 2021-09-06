import ply.lex as lex


class UCLex:
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

    def t_IDENTIFIER(self, t):
        r'[_a-zA-Z][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'IDENTIFIER')
        return t

    # Ignored chars
    t_ignore = " \t\x0c"

    def t_newline(self, t):
        r'[\n|\r\n]+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        t.lexer.skip(1)
        return t

    def t_comment(self, t):
        r'/{2,}[^\n\r]*'
        pass
    
    def build(self, **kwargs):
         self.lexer = lex.lex(module=self, **kwargs)

tokens = UCLex.tokens