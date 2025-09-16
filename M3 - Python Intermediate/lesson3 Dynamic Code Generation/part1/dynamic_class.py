# ================= DYNAMIC CLASS CREATION =================
# Python lets you create classes *at runtime*. The built-in `type` is actually the
# class *factory*. When you write:
#
#     class Pet:
#         pass
#
# Python roughly does the equivalent of:
#
#     Pet = type("Pet", (object,), {})
#
# The 3-arg form is: type(name, bases, namespace)
#   - name:     the class name (string)
#   - bases:    a tuple of base classes (e.g., (object,))
#   - namespace: a dict mapping attribute names -> objects (methods, attributes, etc.)
#
# Why do this?
# - Generate classes based on configuration or input (e.g., CSV headers -> fields)
# - Avoid repetitive boilerplate
# - Metaprogramming: build small utilities like simple enums, record types, etc.
#
# A common pattern is to write a *factory function* that returns a new class:
#
#     def make_something(...):
#         namespace = {...}           # methods/attributes to attach
#         return type("Something", (object,), namespace)
# ==============================================================================


# ---------- EXAMPLE 1 (A tiny one-off class with a method) ----------
# Goal: build a simple class with a greet() instance method.
def _pet_greet(self):
    return f"Hello, I'm a {self.__class__.__name__}!"

Pet = type("Pet", (object,), {"greet": _pet_greet})

# Example:
# >>> p = Pet()
# >>> p.greet()
# "Hello, I'm a Pet!"


# ---------- EXAMPLE 2 (A super simple enum-like class) ----------
# Goal: create a class with constant attributes from a list of names.
def make_enum(name, members):
    """
    Create a class like:
        Color.RED, Color.GREEN, ...
    where each attribute's value is its own string name.
    """
    namespace = {m: m for m in members}
    return type(name, (object,), namespace)

# Example:
# >>> Color = make_enum("Color", ["RED", "GREEN", "BLUE"])
# >>> Color.RED, Color.BLUE
# ('RED', 'BLUE')

# ---------- C) DYNAMIC CLASS CREATION (Your example, kept) ----------
def make_record_class(name, field_names):
    """Return a simple record class with given fields."""
    def __init__(self, *vals):
        for fname, val in zip(field_names, vals):
            setattr(self, fname, val)
    namespace = {"__init__": __init__}
    return type(name, (object,), namespace)

# ---------- PRACTICE EXERCISES ----------
# EXERCISE 1: Make a dynamic Box class
# Write a function `make_box_class()` that returns a class named "Box"
# with:
#   - __init__(self, width, height): sets self.width and self.height
#   - area(self): returns width * height
#   - perimeter(self): returns 2 * (width + height)
#
# Hints:
# - Define the three functions locally (inside make_box_class) and pass them in
#   the namespace dict to type().
# - Example usage (expected):
#     Box = make_box_class()
#     b = Box(3, 4)
#     b.area() -> 12
#     b.perimeter() -> 14

# TODO: implement this
def make_box_class():
    # def __init__(self, width, height): ...
    # def area(self): ...
    # def perimeter(self): ...
    namespace = {
        # "__init__": __init__,
        # "area": area,
        # "perimeter": perimeter,
    }
    return type("Box", (object,), namespace)


# EXERCISE 2: Tagged class factory
# Write `make_tagged_class(name, tag)` that returns a class with:
#   - a class attribute TAG = tag
#   - an instance method describe(self) returning f"{self.__class__.__name__}(TAG={self.TAG})"
#
# Example usage (expected):
#   Animal = make_tagged_class("Animal", "mammal")
#   a = Animal()
#   a.describe() -> "Animal(TAG=mammal)"

# TODO: implement this
def make_tagged_class(name, tag):
    # def describe(self): ...
    namespace = {
        # "TAG": tag,
        # "describe": describe,
    }
    return type(name, (object,), namespace)


if __name__ == "__main__":
    # Quick demo of the examples:
    # Your record factory
    Person = make_record_class("Person", ["name", "age"])
    alice = Person("Alice", 30)
    print(alice.name, alice.age)  # Alice 30

    # One-off class via type()
    p = Pet()
    print(p.greet())  # Hello, I'm a Pet!

    # Enum-like class
    Color = make_enum("Color", ["RED", "GREEN", "BLUE"])
    print(Color.RED, Color.BLUE)  # RED BLUE