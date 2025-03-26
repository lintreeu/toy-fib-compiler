from llvmlite import ir
from ast_nodes import (
    Number, Variable, BinaryOp, FunctionCall,
    Return, IfStatement, WhileStatement, Block, FunctionDef
)

def generate_ir(ast_list):
    module = ir.Module(name="my_module")

    for func_node in ast_list:
        if isinstance(func_node, FunctionDef):
            codegen_function(func_node, module)
        else:
            raise NotImplementedError("Top-level node must be FunctionDef.")
    return module

def codegen_function(func_def, module):
    int32 = ir.IntType(32)
    param_types = [int32 for _ in func_def.params]
    func_type = ir.FunctionType(int32, param_types)
    function = ir.Function(module, func_type, name=func_def.name)

    entry_block = function.append_basic_block('entry')
    builder = ir.IRBuilder(entry_block)

    var_map = {}
    for i, p in enumerate(func_def.params):
        var_map[p] = function.args[i]

    codegen_block(func_def.body, builder, var_map, function)

    if not builder.block.is_terminated:
        builder.ret(ir.Constant(int32, 0))

    return function

def codegen_block(block_node, builder, var_map, function):
    for stmt in block_node.statements:
        codegen_statement(stmt, builder, var_map, function)

def codegen_statement(stmt, builder, var_map, function):
    if isinstance(stmt, Return):
        val = codegen_expr(stmt.value, builder, var_map, function)
        builder.ret(val)
    elif isinstance(stmt, IfStatement):
        codegen_if(stmt, builder, var_map, function)
    elif isinstance(stmt, WhileStatement):
        codegen_while(stmt, builder, var_map, function)
    elif isinstance(stmt, Block):
        codegen_block(stmt, builder, var_map, function)
    else:
        codegen_expr(stmt, builder, var_map, function)

def codegen_if(if_node, builder, var_map, function):
    cond_val = codegen_expr(if_node.condition, builder, var_map, function)

    if cond_val.type == ir.IntType(32):
        zero = ir.Constant(ir.IntType(32), 0)
        cond_val = builder.icmp_signed('!=', cond_val, zero)

    then_bb = function.append_basic_block('then')
    else_bb = function.append_basic_block('else')
    merge_bb = function.append_basic_block('endif')

    builder.cbranch(cond_val, then_bb, else_bb)

    # then block
    builder.position_at_end(then_bb)
    codegen_block(if_node.then_block, builder, var_map, function)
    if not builder.block.is_terminated:
        builder.branch(merge_bb)

    builder.position_at_end(else_bb)
    if if_node.else_block:
        codegen_block(if_node.else_block, builder, var_map, function)
    if not builder.block.is_terminated:
        builder.branch(merge_bb)

    builder.position_at_end(merge_bb)

def codegen_while(while_node, builder, var_map, function):
    cond_bb = function.append_basic_block('while_cond')
    body_bb = function.append_basic_block('while_body')
    end_bb = function.append_basic_block('while_end')

    builder.branch(cond_bb)

    builder.position_at_end(cond_bb)
    cond_val = codegen_expr(while_node.condition, builder, var_map, function)
    if cond_val.type == ir.IntType(32):
        zero = ir.Constant(ir.IntType(32), 0)
        cond_val = builder.icmp_signed('!=', cond_val, zero)
    builder.cbranch(cond_val, body_bb, end_bb)

    builder.position_at_end(body_bb)
    codegen_block(while_node.body, builder, var_map, function)
    if not builder.block.is_terminated:
        builder.branch(cond_bb)

    builder.position_at_end(end_bb)

def codegen_expr(expr, builder, var_map, function):
    int32 = ir.IntType(32)

    if isinstance(expr, Number):
        return ir.Constant(int32, expr.value)

    elif isinstance(expr, Variable):
        return var_map[expr.name]

    elif isinstance(expr, BinaryOp):
        lhs = codegen_expr(expr.left, builder, var_map, function)
        rhs = codegen_expr(expr.right, builder, var_map, function)
        if expr.op == '+':
            return builder.add(lhs, rhs)
        elif expr.op == '-':
            return builder.sub(lhs, rhs)
        elif expr.op == '*':
            return builder.mul(lhs, rhs)
        elif expr.op == '/':
            return builder.sdiv(lhs, rhs)
        elif expr.op in ('<','<=','>','>=','==','!='):
            cmp = builder.icmp_signed(expr.op, lhs, rhs)
            return cmp
        else:
            raise NotImplementedError(f"Unknown op {expr.op}")

    elif isinstance(expr, FunctionCall):
        callee = function.module.get_global(expr.callee)
        args_ir = [codegen_expr(a, builder, var_map, function) for a in expr.args]
        return builder.call(callee, args_ir)

    else:
        raise NotImplementedError(f"Unknown expr node: {type(expr)}")
