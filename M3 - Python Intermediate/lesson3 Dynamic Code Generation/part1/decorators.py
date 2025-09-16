# ===================== WHAT ARE DECORATORS? =====================
# In Python, a *decorator* is just a function that takes another function (or class)
# and returns a modified (or wrapped) version of it — without you changing the original code.
#
# You apply a decorator with the @ syntax:
#
#     @my_decorator
#     def do_stuff(...):
#         ...
#
# which is equivalent to:
#
#     def do_stuff(...):
#         ...
#     do_stuff = my_decorator(do_stuff)
#
# Why use them?
# - Add behavior like logging, timing, access checks, caching, etc.
# - Keep your function/class code clean and focused on its core job.
#
# There are two common kinds:
# 1) Function decorators: take a function, return a new function.
# 2) Class decorators: take a class, return a new class (often the same class after tweaking it).
#
# Tip: use functools.wraps on wrapper functions to preserve the original function’s
# name and docstring (helpful for debugging and docs).
# ===============================================================

import functools

# ---------- function decorator ----------
# Goal: a very simple decorator that announces before running a function.
def announce(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"Running {fn.__name__}...")
        return fn(*args, **kwargs)
    return wrapper

@announce
def greet(name):
    return f"Hello, {name}!"

# Example:
# >>> greet("Ana")

# Running greet...
# 'Hello, Ana!'


# ---------- class decorator ----------
# Goal: add a small helper method to any class: .greet()
def add_greet_method(cls):
    def greet(self):
        return f"Hello from {self.__class__.__name__}!"
    cls.greet = greet
    return cls

@add_greet_method
class Box:
    def __init__(self, width, height):
        self.width = width
        self.height = height

# Example:
# >>> b = Box(2, 3)
# >>> b.greet()

# 'Hello from Box!'

# ---------- FUNCTION DECORATORS ----------
def log_calls(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"[LOG] {fn.__name__} called with {args=} {kwargs=}")
        return fn(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    return a + b

# ---------- CLASS DECORATOR ----------
def auto_repr(cls):
    """Adds __repr__ implementation reflecting __dict__."""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@auto_repr
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


# ---------- PRACTICE EXERCISES ----------
# EXERCISE 1: Function decorator
# Write a decorator called `uppercase_result` that:
# - Calls the original function
# - If the function returns a string, convert it to uppercase before returning it
# Starter + expected behavior are below.

# TODO: implement this
def uppercase_result(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # TODO: call fn, capture result
        # TODO: if result is a str, make it uppercase
        # TODO: return the (maybe modified) result
        pass  # <-- replace this with your implementation
    return wrapper

@uppercase_result
def say_hello(name):
    return f"Hello, {name}!"

# Expected:
# >>> say_hello("world")
# 'HELLO, WORLD!'


# EXERCISE 2: Class decorator
# Write a class decorator called `add_to_dict` that adds a `to_dict(self)` method
# to any class. The method should return a *new* dict with the instance attributes.
#
# Hints:
# - You can read attributes from self.__dict__
# - Return a *copy* (e.g., dict(self.__dict__)) so callers can’t mutate the internals accidentally.

# TODO: implement this
def add_to_dict(cls):
    # TODO: define a to_dict(self) method that returns a copy of self.__dict__
    # TODO: attach it to cls, then return cls
    return cls  # <-- replace this with your implementation

@add_to_dict
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

# Expected:
# >>> s = Student("Mara", 10)
# >>> s.to_dict()
# {'name': 'Mara', 'grade': 10}


if __name__ == "__main__":
    # Tiny demo to show the original examples working:
    print(add(2, 3))        # Logs the call, then prints 5
    p = Point(1, 4)
    print(p)                # Point(x=1, y=4)
    print(greet("Ana"))     # Running greet... then returns greeting
    b = Box(2, 3)
    print(b.greet())        # Hello from Box!
