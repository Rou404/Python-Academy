"""Observer: publish/subscribe event."""

class Event:
    def __init__(self):
        self._observers = []
    def subscribe(self, fn):
        self._observers.append(fn)
    def unsubscribe(self, fn):
        self._observers.remove(fn)
    def emit(self, *args, **kwargs):
        for fn in list(self._observers):
            fn(*args, **kwargs)

def demo():
    print("\n[Observer]")
    on_save = Event()

    def logger(payload):
        print("LOG:", payload)
    def metrics(payload):
        print("METRICS len:", len(str(payload)))

    on_save.subscribe(logger)
    on_save.subscribe(metrics)
    on_save.emit({"status": "ok", "items": 3})

if __name__ == "__main__":
    demo()
