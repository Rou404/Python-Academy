"""Decorator: add behavior without modifying the wrapped object."""

class Notifier:
    def send(self, user, message):
        return "Notify " + user + ": " + message

class NotifierDecorator(Notifier):
    def __init__(self, wrapped):
        self.wrapped = wrapped

class TimestampNotifier(NotifierDecorator):
    def send(self, user, message):
        from datetime import datetime
        base = self.wrapped.send(user, message)
        return datetime.now().isoformat(timespec="seconds") + " | " + base

class ShoutNotifier(NotifierDecorator):
    def send(self, user, message):
        base = self.wrapped.send(user, message)
        return base.upper()

def demo():
    print("\n[Decorator]")
    base = Notifier()
    with_time = TimestampNotifier(base)
    shouting = ShoutNotifier(with_time)
    print("Decorator chain:", shouting.send("alice", "hello"))

if __name__ == "__main__":
    demo()
