"""Strategy: swap algorithms at runtime."""

class BubbleSort:
    def sort(self, data):
        arr = list(data)
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class BuiltinSort:
    def sort(self, data):
        return sorted(data)

class Sorter:
    def __init__(self, strategy):
        self.strategy = strategy
    def sort(self, data):
        return self.strategy.sort(data)

def demo():
    print("\n[Strategy]")
    nums = [5, 3, 9, 1]
    s1 = Sorter(BubbleSort())
    s2 = Sorter(BuiltinSort())
    print("BubbleSort:", s1.sort(nums))
    print("BuiltinSort:", s2.sort(nums))

if __name__ == "__main__":
    demo()
