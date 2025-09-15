"""
Exercise 1 — Guess the Design Pattern (5 scenarios)
Run this file and, for each scenario (A–E), write down which pattern you think it shows.
Patterns to choose from (not exhaustive): Proxy, Singleton, Builder, Adapter, Decorator

Tip: Read the small scenario description comments, run, observe the output, and guess.
"""

# ---------- Scenario A ----------
class _Config:
    def __init__(self):
        self.theme = "dark"

config = _Config()

def scenario_a():
    print("\n[Scenario A]")
    a = config
    b = config
    print("Same object used twice?", a is b)
    print("Theme:", a.theme, "| id(a) == id(b)?", id(a) == id(b))


# ---------- Scenario B ----------
class MailComposer:
    def __init__(self):
        self._subject = None
        self._hero = None
        self._cta = None
        self._footer = None

    def subject(self, text):
        self._subject = text
        return self

    def hero(self, text):
        self._hero = text
        return self

    def cta(self, text):
        self._cta = text
        return self

    def footer(self, text):
        self._footer = text
        return self

    def build(self):
        lines = []
        if self._subject: lines.append("SUBJECT: " + self._subject)
        if self._hero:    lines.append("[HERO] " + self._hero)
        if self._cta:     lines.append("[CTA] " + self._cta)
        if self._footer:  lines.append(self._footer)
        return "\n".join(lines)

def scenario_b():
    print("\n[Scenario B]")
    email = (
        MailComposer()
        .subject("Welcome!")
        .hero("Big summer sale")
        .cta("Shop now")
        .footer("Unsubscribe link")
        .build()
    )
    print(email)


# ---------- Scenario C ----------
# Client works with objects that provide .area()
class Rectangle:
    def __init__(self, w, h):
        self.w = w; self.h = h
    def area(self):
        return self.w * self.h

# Third-party shape with a different API
class LegacyBox:
    def __init__(self, width, height):
        self.width = width; self.height = height
    def compute_area(self):
        return self.width * self.height

# Wrapper that makes LegacyBox look like what our client expects
class BoxAsRect(Rectangle):
    def __init__(self, legacy):
        self.legacy = legacy
    def area(self):
        return self.legacy.compute_area()

def scenario_c():
    print("\n[Scenario C]")
    r = Rectangle(3, 4)
    legacy = LegacyBox(5, 6)
    wrapped = BoxAsRect(legacy)
    print("Rectangle area:", r.area())
    print("Wrapped legacy area:", wrapped.area())


# ---------- Scenario D: ----------
class Notifier:
    def send(self, user, message):
        return f"Notify {user}: {message}"

class WithTimestamp:
    def __init__(self, wrapped):
        self.wrapped = wrapped
    def send(self, user, message):
        from datetime import datetime
        base = self.wrapped.send(user, message)
        return f"{datetime.now().isoformat(timespec='seconds')} | {base}"

class Shout:
    def __init__(self, wrapped):
        self.wrapped = wrapped
    def send(self, user, message):
        base = self.wrapped.send(user, message)
        return base.upper()

def scenario_d():
    print("\n[Scenario D]")
    base = Notifier()
    chain = Shout(WithTimestamp(base))
    print(chain.send("alice", "hello"))


# ---------- Scenario E: ----------
class RealImage:
    def __init__(self, path):
        # pretend this is expensive I/O
        print(f"(loading high-res image from {path})")
        self.path = path
        self._pixels = "<binary data>"
    def show(self):
        return f"Showing {self.path} ({len(self._pixels)} bytes)"

class LazyImage:
    def __init__(self, path, allowed=True):
        self.path = path
        self.allowed = allowed
        self._real = None  # not created yet
    def show(self):
        if not self.allowed:
            return "Access denied: upgrade required"
        if self._real is None:
            # delay creation until actually needed
            self._real = RealImage(self.path)
        return self._real.show()

def scenario_e():
    print("\n[Scenario E]")
    pic = LazyImage("photo.png", allowed=True)
    print("First view:", pic.show())  # triggers load
    print("Second view:", pic.show()) # now fast (already loaded)
    restricted = LazyImage("premium.png", allowed=False)
    print("Restricted:", restricted.show())


if __name__ == "__main__":
    scenario_a()
    scenario_b()
    scenario_c()
    scenario_d()
    scenario_e()
    print("\nWrite down which pattern each scenario (A–E) represents.")
