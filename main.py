import sys
from lexer import Lexer
from parser import Parser
from codegen import generate_ir
from llvmlite import binding
import ctypes

from anytree import RenderTree

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [filename]")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    # 1. 詞法分析
    lexer = Lexer(source)
    tokens = lexer.tokens

    # 2. 語法分析
    parser = Parser(tokens)
    ast_roots = parser.parse()  # 可能包含多個函式定義

    # 3. (可選) 可視化 AST
    print("\n=== AST Visual ===")
    for root in ast_roots:
        tree_node = root.to_anytree_node()
        for pre, _, node in RenderTree(tree_node):
            print(f"{pre}{node.name}")
        print()

    # 4. 產生 LLVM IR
    module = generate_ir(ast_roots)
    print("\n=== Generated LLVM IR ===")
    print(module)

    # 5. 使用 llvmlite JIT 執行
    print("\n=== Running JIT ===")
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    backing_mod = binding.parse_assembly(str(module))
    backing_mod.verify()

    engine = binding.create_mcjit_compiler(backing_mod, target_machine)
    engine.finalize_object()

    # 自動尋找名為 'main' 的函式，執行
    main_ptr = engine.get_function_address("main")
    if main_ptr == 0:
        print("No 'main' function found.")
        return

    cfunc = ctypes.CFUNCTYPE(ctypes.c_int32)(main_ptr)
    result = cfunc()
    print(f"Program returned: {result}")


if __name__ == "__main__":
    main()
