from ast_nodes import (
    ASTNode, Number, Variable, BinaryOp, FunctionCall,
    Return, IfStatement, WhileStatement, Block, FunctionDef
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None

    def next_token(self):
        tok = self.peek()
        self.current += 1
        return tok

    def eat(self, token_type):
        if self.peek() and self.peek()[0] == token_type:
            self.current += 1
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.peek()}")

    def parse(self):
        """可能含有多個函式定義"""
        functions = []
        while self.peek():
            functions.append(self.parse_function())
        return functions

    # ---------------------
    # 解析函式定義
    # def fib(n) { ... }
    # ---------------------
    def parse_function(self):
        self.eat('DEF')
        func_name_tok = self.next_token()
        if func_name_tok[0] != 'IDENTIFIER':
            raise SyntaxError(f"Function name expected, got {func_name_tok}")
        func_name = func_name_tok[1]

        self.eat('LPAREN')
        params = []
        # 多參數逗號分隔
        if self.peek() and self.peek()[0] == 'IDENTIFIER':
            params.append(self.next_token()[1])
            while self.peek() and self.peek()[0] == 'COMMA':
                self.eat('COMMA')
                p = self.next_token()
                if p[0] != 'IDENTIFIER':
                    raise SyntaxError("Param must be IDENTIFIER")
                params.append(p[1])
        self.eat('RPAREN')

        # 解析函式本體 -> Block
        block_body = self.parse_block()

        return FunctionDef(func_name, params, block_body)

    # ---------------------
    # 解析區塊 { statements }
    # ---------------------
    def parse_block(self):
        self.eat('LBRACE')
        stmts = []
        while self.peek() and self.peek()[0] != 'RBRACE':
            stmts.append(self.parse_statement())
        self.eat('RBRACE')
        return Block(stmts)

    # ---------------------
    # statement = if / while / return / expressionStmt
    # ---------------------
    def parse_statement(self):
        tok = self.peek()
        if not tok:
            return None
        if tok[0] == 'IF':
            return self.parse_if()
        elif tok[0] == 'WHILE':
            return self.parse_while()
        elif tok[0] == 'RETURN':
            return self.parse_return()
        else:
            # expression statement
            expr = self.parse_expression()
            # 可支援分號
            if self.peek() and self.peek()[0] == 'SEMICOLON':
                self.eat('SEMICOLON')
            return expr  # 直接以 expr 節點當作 statement

    # ---------------------
    # if expr { ... } else { ... }
    # ---------------------
    def parse_if(self):
        self.eat('IF')
        cond = self.parse_expression()
        then_block = self.parse_block()

        else_block = None
        if self.peek() and self.peek()[0] == 'ELSE':
            self.eat('ELSE')
            else_block = self.parse_block()

        return IfStatement(cond, then_block, else_block)

    # ---------------------
    # while expr { ... }
    # ---------------------
    def parse_while(self):
        self.eat('WHILE')
        cond = self.parse_expression()
        body_block = self.parse_block()
        return WhileStatement(cond, body_block)

    # ---------------------
    # return expr
    # ---------------------
    def parse_return(self):
        self.eat('RETURN')
        value = self.parse_expression()
        # 如果有分號，就吃掉
        if self.peek() and self.peek()[0] == 'SEMICOLON':
            self.eat('SEMICOLON')
        return Return(value)

    # ---------------------
    # expression: 最高層(暫時只處理比較 + 加減乘除)
    # ---------------------
    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        left = self.parse_comparison()
        while True:
            tok = self.peek()
            if tok and tok[0] == 'OPERATOR' and tok[1] in ('==','!='):
                op = self.next_token()[1]
                right = self.parse_comparison()
                left = BinaryOp(left, op, right)
            else:
                break
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while True:
            tok = self.peek()
            if tok and tok[0] == 'OPERATOR' and tok[1] in ('<','<=','>','>='):
                op = self.next_token()[1]
                right = self.parse_term()
                left = BinaryOp(left, op, right)
            else:
                break
        return left

    def parse_term(self):
        left = self.parse_factor()
        while True:
            tok = self.peek()
            if tok and tok[0] == 'OPERATOR' and tok[1] in ('+','-'):
                op = self.next_token()[1]
                right = self.parse_factor()
                left = BinaryOp(left, op, right)
            else:
                break
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while True:
            tok = self.peek()
            if tok and tok[0] == 'OPERATOR' and tok[1] in ('*','/'):
                op = self.next_token()[1]
                right = self.parse_unary()
                left = BinaryOp(left, op, right)
            else:
                break
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok and tok[0] == 'OPERATOR' and tok[1] in ('+','-'):
            op = self.next_token()[1]
            node = self.parse_unary()
            # 一元運算子 => 0 - expr
            from ast_nodes import Number
            return BinaryOp(Number(0), op, node)
        else:
            return self.parse_primary()

    # ---------------------
    # parse_primary: 數字 / 變數 / 函式呼叫 / (expr)
    # ---------------------
    def parse_primary(self):
        tok = self.peek()
        if not tok:
            raise SyntaxError("Unexpected end of input in primary")

        if tok[0] == 'NUMBER':
            self.next_token()
            return Number(tok[1])

        elif tok[0] == 'IDENTIFIER':
            self.next_token()
            ident_name = tok[1]
            # 檢查是否函式呼叫
            if self.peek() and self.peek()[0] == 'LPAREN':
                # 函式呼叫
                self.eat('LPAREN')
                args = []
                if self.peek() and self.peek()[0] != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.peek() and self.peek()[0] == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.parse_expression())
                self.eat('RPAREN')
                return FunctionCall(ident_name, args)
            else:
                # 純變數
                return Variable(ident_name)

        elif tok[0] == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            return expr

        else:
            raise SyntaxError(f"Unexpected token {tok} in primary")
