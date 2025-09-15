"""Adapter: wrap a legacy API to the interface we expect."""

# Client expects an object with .area()
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def area(self):
        return self.w * self.h

# Legacy library
class LegacyBox:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def compute_area(self):
        return self.width * self.height

class LegacyBoxAdapter(Rectangle):
    def __init__(self, legacy_box):
        self.legacy_box = legacy_box
    def area(self):
        return self.legacy_box.compute_area()

def demo():
    print("\n[Adapter]")
    r = Rectangle(3, 4)
    legacy = LegacyBox(5, 6)
    adapted = LegacyBoxAdapter(legacy)
    print("Rectangle area:", r.area())
    print("Adapted legacy area:", adapted.area())

if __name__ == "__main__":
    demo()
