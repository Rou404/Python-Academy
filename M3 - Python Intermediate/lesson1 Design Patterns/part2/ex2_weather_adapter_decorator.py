"""Exercise 2 (Adapter + Decorator)
Wrap a third‑party weather client so your app can call current_celsius(city).
Add a caching decorator so repeated calls for the same city reuse the result.
"""

class ThirdPartyWeather:
    # Simulated client that returns Fahrenheit
    def now_fahrenheit(self, city):
        print("(calling remote API)")
        return 86.0  # pretend result

# TODO:
#   • Write an Adapter with .current_celsius(city)
#       (formula: C = (F - 32) * 5/9)
#   • Write a Decorator "CachedWeather" that wraps a provider and caches per city
#   • Show a demo calling twice for the same city; only first call should print the API line

if __name__ == "__main__":
    print("Implement the Adapter and Decorator, then add a short demo here.")
