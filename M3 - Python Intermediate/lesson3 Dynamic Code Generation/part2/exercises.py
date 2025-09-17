# ==========================================================
# A1, A2 (Decorators) • B1, B2 (Dynamic Class Creation)
# C1, C2 (AST Transforms)
# ==========================================================

# --------------------------
# A) DECORATORS
# --------------------------

import functools
import time

# ---------- A1 — Core: @timed ----------
# Goal: write a function decorator that measures wall-clock runtime and prints it.
# Print format: [TIMED] <fn_name> took <ms> ms
def timed(fn):
    """Prints: [TIMED] <fn_name> took <ms> ms"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # start time
        # call the function
        # end time
        # print elapsed in milliseconds (rounded)
        # return the original result
        ...
    return wrapper

# self-check
@timed
def slow_add(a, b):
    time.sleep(0.05)
    return a + b


# ---------- A2 — Bonus: @memoize ----------
# Goal: simple memoization for pure functions with positional args only.
def memoize(fn):
    """Caches results by args tuple. Ignore kwargs for this exercise."""
    cache = {}
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # if kwargs present, just call through (or treat as cache miss)
        # else: check cache, compute+store if missing
        ...
    return wrapper

# self-check
@memoize
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)


# --------------------------
# B) DYNAMIC CLASS CREATION
# --------------------------

# ---------- B1 — Core: make_struct ----------
# Goal: write a factory that returns a class with:
# __init__, __repr__, to_dict, and __eq__ over listed fields.
def make_struct(name, fields):
    """
    Example:
        Person = make_struct("Person", ["name", "age"])
        p = Person("Ana", 20)
        repr(p) -> "Person(name='Ana', age=20)"
        p.to_dict() -> {'name': 'Ana', 'age': 20}
        p == Person("Ana", 20) -> True
    """
    # define __init__, __repr__, to_dict, __eq__
    # add them to namespace, then return type(name, (object,), namespace)
    ...
    # return type(name, (object,), namespace)


# ---------- B2 — Bonus: make_validated_record ----------
# Goal: factory with per-field validators. Raise ValueError if invalid.
def make_validated_record(name, schema):
    """
    schema: dict of field_name -> validator(value) -> bool
    Example:
        User = make_validated_record("User", {
            "name": lambda s: isinstance(s, str) and s,
            "age":  lambda n: isinstance(n, int) and n >= 0,
        })
        u = User("Ana", 20)   # ok
        User("", 20)          # ValueError
    """
    fields = list(schema.keys())

    def __init__(self, *vals):
        # check arity equals len(fields)
        # validate each value via schema[fname](val), raise ValueError on False
        # set attributes
        ...
    def __repr__(self):
        # nice-to-have representation like User(name='Ana', age=20)
        ...
    namespace = {
        # "__func__": func,
        # "__func2__": func2,
    }
    return type(name, (object,), namespace)


# --------------------------
# C) AST TRANSFORMS
# --------------------------

import ast
import textwrap

# ---------- C1 — Core: RenameVarTransformer ----------
# Goal: rename all variable identifiers from `old` to `new` (not attributes/strings).
class RenameVarTransformer(ast.NodeTransformer):
    def __init__(self, old, new):
        self.old, self.new = old, new

    def visit_Name(self, node):
        # TODO: if node.id == self.old, return a Name(self.new, same ctx)
        # else return node
        return node

    # Optional: avoid touching attributes like obj.old
    def visit_Attribute(self, node):
        # Ensure we DON'T rename attribute names (node.attr)
        self.generic_visit(node)
        return node


# ---------- C2 — Bonus: InlineConstantsTransformer ----------
# Goal: collect module-level ALL-CAPS constants with literal values and inline them where referenced.
# Scope constraints (for simplicity):
# - Only inline names defined at module top level like PI = 3.14 or GREETING = "hi".
# - Only inline numeric or string literals (and bool if you want).
class InlineConstantsTransformer(ast.NodeTransformer):
    def __init__(self):
        self.consts = {}  # name -> ast.Constant

    def visit_Module(self, node):
        # TODO: first pass: collect uppercase assigns with Constant values at top level
        # e.g., for each ast.Assign in node.body:
        #   if all targets are ast.Name UPPERCASE and value is ast.Constant(int/float/str/bool):
        #       record in self.consts[name] = value
        # Then, run generic_visit(node) to transform inner Names.
        ...
        return node

    def visit_Name(self, node):
        # If this is a Load of a known constant, replace with a copy of Constant
        # else return node
        return node


# ==========================================================
# SELF-CHECKS (run after you fill in the TODOs)
# ==========================================================

if __name__ == "__main__":
    print("\n=== A1: @timed ===")
    try:
        print("slow_add(2, 3) ->", slow_add(2, 3))
    except Exception as e:
        print("A1 not complete yet:", e)

    print("\n=== A2: @memoize ===")
    try:
        print("fib(10) ->", fib(10))     # 55
        print("fib(35) ->", fib(35))     # should be fast
    except Exception as e:
        print("A2 not complete yet:", e)

    print("\n=== B1: make_struct ===")
    try:
        Person = make_struct("Person", ["name", "age"])
        a = Person("Ana", 20)
        b = Person("Ana", 20)
        c = Person("Ana", 21)
        print(a)                 # Person(name='Ana', age=20)
        print(a.to_dict())       # {'name': 'Ana', 'age': 20}
        print(a == b, a == c)    # True False
    except Exception as e:
        print("B1 not complete yet:", e)

    print("\n=== B2: make_validated_record ===")
    try:
        User = make_validated_record("User", {
            "name": lambda s: isinstance(s, str) and bool(s),
            "age":  lambda n: isinstance(n, int) and n >= 0,
        })
        print(User("Ana", 20))
        try:
            User("", 20)
        except ValueError as ve:
            print("Caught expected ValueError:", ve)
    except Exception as e:
        print("B2 not complete yet:", e)

    print("\n=== C1: RenameVarTransformer ===")
    try:
        src = textwrap.dedent("""
            x = 10
            def twice(x):
                return x * 2
            y = x + twice(3)
        """)
        tree = ast.parse(src)
        new_tree = RenameVarTransformer("x", "value").visit(tree)
        ast.fix_missing_locations(new_tree)
        code = compile(new_tree, "<ast>", "exec")
        ns = {}
        exec(code, ns)
        print("Globals:", [k for k in ns if not k.startswith("__")])  # should include value, twice, y
        print("value =", ns["value"], "y =", ns["y"])
    except Exception as e:
        print("C1 not complete yet:", e)

    print("\n=== C2: InlineConstantsTransformer ===")
    try:
        src = """
PI = 3.14159
HELLO = "hi"
def area(r):
    return PI * r * r
def greet():
    return HELLO + "!"
"""
        tree = ast.parse(src)
        new_tree = InlineConstantsTransformer().visit(tree)
        ast.fix_missing_locations(new_tree)
        code = compile(new_tree, "<ast>", "exec")
        ns = {}
        exec(code, ns)
        print("area(2) ->", ns)   # should compute numerically with inlined PI
        print("greet() ->", ns["greet"]())   # "hi!"
    except Exception as e:
        print("C2 not complete yet:", e)
