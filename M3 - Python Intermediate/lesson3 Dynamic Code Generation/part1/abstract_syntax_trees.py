# ==========================================
# AST FUNDAMENTALS — theory_and_exercises.py
# ==========================================
#
# Core ideas:
# 1) Parse source code into a tree:         ast.parse(src)
# 2) Inspect the tree (read-only):          ast.dump / ast.walk / NodeVisitor
# 3) Make tiny edits (write):               NodeTransformer (return new/edited nodes)
# 4) Put line numbers back, then run:       ast.fix_missing_locations + compile + exec
#
# Why do this?
# - Automated refactors (rename functions, add/remove calls)
# - Instrumentation (insert logging/timing)
# - Code analysis/checks and small source-to-source rewrites
#
#
# First functions you should know:
# - ast.parse(text)                  -> AST
# - ast.dump(node, indent=4)         -> pretty string of the tree
# - ast.walk(node)                   -> iterate all nodes
# - isinstance(node, ast.<Type>)     -> check the node kind
# - class MyVisitor(ast.NodeVisitor): override visit_<Type>
# - class MyTx(ast.NodeTransformer):  override visit_<Type>, return node/new node/None
# - ast.fix_missing_locations(tree)  -> fill lineno/col_offset after edits
# - compile(tree, filename, mode)    -> code object ("exec" or "eval")
# - exec(code, namespace)            -> run it
#

import ast
import textwrap


# ----------------------------
# Helpers for demos and tests
# ----------------------------
def parse_and_dump(src: str):
    """Parse Python source and print a readable AST."""
    tree = ast.parse(src)
    print(ast.dump(tree, indent=4))
    return tree

def run_code_from_tree(tree, ns=None):
    """Compile and exec a tree; return its namespace dict."""
    ast.fix_missing_locations(tree)
    code = compile(tree, filename="<ast>", mode="exec")
    ns = {} if ns is None else ns
    exec(code, ns)
    return ns


# ---------------------------------------------
# 1) READ-ONLY INSPECTION (NodeVisitor example)
# ---------------------------------------------
class NameCollector(ast.NodeVisitor):
    """Collect simple names used in the code (variables & refs)."""
    def __init__(self):
        self.names = []

    def visit_Name(self, node):
        self.names.append(node.id)
        self.generic_visit(node)


# ----------------------------------------------------
# 2) TINY TRANSFORMS (NodeTransformer)
# ----------------------------------------------------
class UppercaseStrings(ast.NodeTransformer):
    """Turn every string literal into UPPERCASE (tiny, safe demo)."""
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(node.value.upper()), node)
        return node

class RenameVar(ast.NodeTransformer):
    """Rename a variable from old -> new (both loads & stores)."""
    def __init__(self, old, new):
        self.old, self.new = old, new

    def visit_Name(self, node):
        if node.id == self.old:
            # Keep the same context (Load/Store)
            return ast.copy_location(ast.Name(self.new, ctx=node.ctx), node)
        return node


# ------------------------
# Mini-demos for the class
# ------------------------
def demo_dump():
    print("\n=== DEMO: ast.dump on tiny function ===")
    src = "def add(a, b):\n    return a + b\n"
    parse_and_dump(src)

def demo_visitor():
    print("\n=== DEMO: NameCollector ===")
    src = textwrap.dedent("""
        x = 1
        def f(y):
            z = x + y
            return z
    """)
    tree = ast.parse(src)
    nc = NameCollector()
    nc.visit(tree)
    print("Names seen:", nc.names)   # e.g. ['x', 'f', 'y', 'z', 'x', 'y', 'z']

def demo_transform_and_run():
    print("\n=== DEMO: UppercaseStrings + run ===")
    src = "def greet():\n    return 'Hello, world!'\n"
    tree = ast.parse(src)
    new_tree = UppercaseStrings().visit(tree)
    ns = run_code_from_tree(new_tree)
    print(ns["greet"]())  # 'HELLO, WORLD!'

    print("\n=== DEMO: RenameVar + run ===")
    src2 = textwrap.dedent("""
        x = 10
        def twice(x):
            return x * 2
        y = x + twice(3)
    """)
    tree2 = ast.parse(src2)
    tree2 = RenameVar("x", "value").visit(tree2)
    ns2 = run_code_from_tree(tree2)
    # After transform, top-level 'value' exists, not 'x'
    print("Globals:", [k for k in ns2 if not k.startswith("__")])  # ['value', 'twice', 'y']
    print("value =", ns2["value"], "y =", ns2["y"])                 # value = 10 y = 16


# ==================
# EXERCISES (Basics)
# ==================
# Keep each exercise small and runnable. All use only:
#   ast.parse, ast.dump, ast.walk, NodeVisitor, NodeTransformer,
#   ast.fix_missing_locations, compile, exec.

# --- EX 1 (Visitor): Count returns -------------------------------------------
# Write a visitor that *counts* how many `return` statements appear in the code.
# Fill the TODOs. Then test on src_ex1.
class ReturnCounter(ast.NodeVisitor):
    def __init__(self):
        self.count = 0

    # TODO: when you visit a Return node, increment self.count
    # def visit_Return(self, node):
    #       ...

def exercise_1():
    src_ex1 = textwrap.dedent("""
        def a(x):
            if x > 0:
                return 1
            return 0

        def b():
            for i in range(3):
                if i == 2:
                    return i
            return -1
    """)
    tree = ast.parse(src_ex1)
    rc = ReturnCounter()
    rc.visit(tree)
    print("[EX1] returns found =", rc.count)  # expect 4


# --- EX 2 (Visitor): List function names + arg counts -------------------------
# Make a visitor that records every function name and how many parameters it has.
# Example output: [('a', 1), ('b', 0)]
class FunctionSigCollector(ast.NodeVisitor):
    def __init__(self):
        self.sigs = []  # list of (func_name, num_args)

    # TODO: implement visit_FunctionDef
    # def visit_FunctionDef(self, node):
    #     ...

def exercise_2():
    src_ex2 = textwrap.dedent("""
        def add(a, b): return a + b
        def ping(): return "pong"
        def mul(a, b, c): return a*b*c
    """)
    tree = ast.parse(src_ex2)
    fc = FunctionSigCollector()
    fc.visit(tree)
    print("[EX2] function signatures =", fc.sigs)  # [('add', 2), ('ping', 0), ('mul', 3)]


# --- EX 3 (Transformer): Remove print(...) statements -------------------------
# Delete any *standalone* print(...) statement.
# Hint: these appear as ast.Expr nodes whose .value is ast.Call to ast.Name('print').
class RemovePrints(ast.NodeTransformer):
    # TODO: override visit_Expr; if it's a print call, return None (delete)
    # def visit_Expr(self, node):
    #     ...
    #     return self.generic_visit(node)
    ...

def exercise_3():
    src_ex3 = textwrap.dedent("""
        def demo():
            print("a")
            x = 1
            print("b", x)
            return x
    """)
    tree = ast.parse(src_ex3)
    new_tree = RemovePrints().visit(tree)
    ns = run_code_from_tree(new_tree)
    print("[EX3] demo() returns:", ns["demo"]())  # expect 1 (and no prints)


# --- EX 4 (Transformer): Add 1 to every integer literal ----------------------
# Replace any integer Constant n with n+1.
# Keep it tiny: only ints; leave other constants as-is.
class PlusOneInts(ast.NodeTransformer):
    # TODO: override visit_Constant; if int, return Constant(value=node.value+1)
    # def visit_Constant(self, node):
    #     ...
    #     return node
    ...

def exercise_4():
    src_ex4 = textwrap.dedent("""
        def f():
            return 40 + 1
        x = 0
    """)
    tree = ast.parse(src_ex4)
    new_tree = PlusOneInts().visit(tree)
    ns = run_code_from_tree(new_tree)
    print("[EX4] f() ->", ns["f"](), "| x ->", ns["x"])  # expect 42 and 1


# -------------
# Run the demos
# -------------
if __name__ == "__main__":
    # quick theory demos (comment out if using live)
    demo_dump()
    demo_visitor()
    demo_transform_and_run()

    # exercises (uncomment as students work through them)
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
