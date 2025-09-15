"""Singleton (pythonic): module-level instance."""

class _Settings:
    def __init__(self):
        self.theme = "dark"

# Export one shared instance
settings = _Settings()

def demo():
    print("\n[Singleton]")
    print("Same object?", settings is settings)
    print("Theme:", settings.theme)

if __name__ == "__main__":
    demo()
