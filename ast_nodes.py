from anytree import Node

class ASTNode:
    def to_anytree_node(self, parent=None):
        return Node(self.__class__.__name__, parent=parent)

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"

    def to_anytree_node(self, parent=None):
        return Node(repr(self), parent=parent)

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"

    def to_anytree_node(self, parent=None):
        return Node(repr(self), parent=parent)

class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.op})"

    def to_anytree_node(self, parent=None):
        node = Node(repr(self), parent=parent)
        self.left.to_anytree_node(parent=node)
        self.right.to_anytree_node(parent=node)
        return node

class FunctionCall(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee   # string
        self.args = args       # list of ASTNode

    def __repr__(self):
        return f"FunctionCall({self.callee})"

    def to_anytree_node(self, parent=None):
        node = Node(repr(self), parent=parent)
        for arg in self.args:
            arg.to_anytree_node(parent=node)
        return node

class Return(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Return"

    def to_anytree_node(self, parent=None):
        node = Node(repr(self), parent=parent)
        self.value.to_anytree_node(node)
        return node

class IfStatement(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __repr__(self):
        return "IfStatement"

    def to_anytree_node(self, parent=None):
        node = Node("IfStatement", parent=parent)
        cond_node = Node("condition", parent=node)
        self.condition.to_anytree_node(cond_node)

        then_node = Node("then_block", parent=node)
        self.then_block.to_anytree_node(then_node)

        if self.else_block:
            else_node = Node("else_block", parent=node)
            self.else_block.to_anytree_node(else_node)

        return node

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return "WhileStatement"

    def to_anytree_node(self, parent=None):
        node = Node("WhileStatement", parent=parent)
        cond_node = Node("condition", parent=node)
        self.condition.to_anytree_node(cond_node)

        body_node = Node("body", parent=node)
        self.body.to_anytree_node(body_node)

        return node

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements  # list of ASTNode

    def __repr__(self):
        return "Block"

    def to_anytree_node(self, parent=None):
        node = Node("Block", parent=parent)
        for stmt in self.statements:
            stmt.to_anytree_node(parent=node)
        return node

class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of str
        self.body = body      # Block

    def __repr__(self):
        return f"FunctionDef({self.name})"

    def to_anytree_node(self, parent=None):
        node = Node(repr(self), parent=parent)
        p_node = Node("params", parent=node)
        for p in self.params:
            Node(f"{p}", parent=p_node)

        b_node = Node("body", parent=node)
        self.body.to_anytree_node(b_node)
        return node
