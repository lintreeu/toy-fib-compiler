import re

# 在 TOKEN_SPECS 中，越前面者優先匹配。
TOKEN_SPECS = [
    ('DEF', r'def'),
    ('IF', r'if'),
    ('ELSE', r'else'),
    ('WHILE', r'while'),
    ('RETURN', r'return'),
    ('NUMBER', r'\d+'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OPERATOR', r'(<=|>=|==|!=|[+\-*/<>=])'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
]

# 在 TOKEN_SPECS 裡的 tuple 順序會影響詞法分析的結果。這個式子會把所有的 token 規則用 |（OR）組合成一條大的 複合正則表達式，然後用 re.finditer() 從左到右逐條比對。
TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECS) #(?P<群組名稱>正則表達式)用名字來取得群組內容


"""
(?P<DEF>def)|(?P<IF>if)|(?P<RETURN>return)|(?P<NUMBER>\d+)|(?P<IDENTIFIER>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<OPERATOR>[\+\-\*/<=])|(?P<LPAREN>\()|(?P<RPAREN>\))|(?P<NEWLINE>\n)|(?P<SKIP>[ \t]+)
"""
print(TOKEN_REGEX)

class Lexer():
    def __init__(self, source_code):
        self.tokens = self.tokenize(source_code)
    
    def tokenize(self, code):
        tokens = []
        for match in re.finditer(TOKEN_REGEX, code):
            print(match)
            kind = match.lastgroup
            value = match.group()
            if kind in ('SKIP', 'NEWLINE'):
                continue
            if kind == 'NUMBER':
                value = int(value)

            tokens.append((kind, value))
        return tokens

    