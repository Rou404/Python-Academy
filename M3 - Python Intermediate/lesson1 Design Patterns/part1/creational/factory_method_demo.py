"""Factory Method: create objects based on a key."""

class ImageFilter:
    def apply(self, path):
        raise NotImplementedError

class Blur(ImageFilter):
    def apply(self, path):
        return "[Blur] " + path

class Sharpen(ImageFilter):
    def apply(self, path):
        return "[Sharpen] " + path

def make_filter(name):
    mapping = {
        "blur": Blur,
        "sharpen": Sharpen,
    }
    try:
        return mapping[name]()
    except KeyError:
        raise ValueError("Unknown filter: " + repr(name))

def demo():
    print("\n[Factory Method]")
    f = make_filter("blur")
    print("Factory ->", f.apply("cat.jpg"))

if __name__ == "__main__":
    demo()
