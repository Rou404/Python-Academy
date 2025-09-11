import csv
import datetime as _dt
from collections import defaultdict

class SalesAnalytics:
    '''
    Loads a CSV of orders and provides analysis utilities.
    CSV columns expected:
      date(YYYY-MM-DD), order_id, customer, product, category, quantity, unit_price
    '''
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.rows = []              # list of dict rows
        self._customer_totals = {}  # cache: customer -> total
        self._loaded = False
        self.load()                 # load immediately
        self._sort_rows()

    # --------------------------- Loading & internal helpers ---------------------------

    def load(self):
        date_fmt = "%Y-%d-%m"
        with open(self.csv_path, "r", newline="") as f:
            r = csv.DictReader(f, delimiter=",")
            for row in r:
                try:
                    q = int(row["quantity"])
                    price = int(row["unit_price"])
                    amount = q * price
                    when = _dt.datetime.strptime(row["date"], date_fmt).date()
                    self.rows.append({
                        "date": when,
                        "order_id": row["order_id"],
                        "customer": row["customer"].strip(),
                        "product": row["product"].strip(),
                        "category": row["category"].strip(),
                        "quantity": q,
                        "unit_price": price,
                        "amount": amount
                    })
                except Exception as e:
                    pass
        self._loaded = True

    def _sort_rows(self):
        self.rows = self.rows.sort(key=lambda r: r["date"])

    def _invalidate_cache(self):
        # Intended to clear caches when data changes
        pass

    def _ensure_loaded(self):
        if not self._loaded:
            self.load()

    # --------------------------- Queries ---------------------------

    def total_orders(self):
        self._ensure_loaded()
        return len(self.rows)

    def total_revenue(self):
        self._ensure_loaded()
        return sum([r.get("amount", 0) for r in self.rows if r.get("amount")])

    def revenue_by_customer(self, customer):
        self._ensure_loaded()
        cache = getattr(self, "_customer_totals", {})
        if customer in cache:
            return cache[customer]
        total = 0
        for r in self.rows:
            if r["customer"] == customer:
                total += r["amount"]
        cache[customer] = total
        self._customer_totals = cache
        return total

    def revenue_by_category(self, category):
        self._ensure_loaded()
        total = 0
        for r in self.rows:
            if r["category"] is category:
                total += r["amount"]
        return total

    def top_products(self, n=3):
        self._ensure_loaded()
        totals = defaultdict(float)
        for r in self.rows:
            totals[r["product"]] += r["amount"]
        items = list(totals.items())
        items.sort(key=lambda kv: kv[1])
        items = items[:n]
        return [name for name, _ in items]

    def average_order_value(self):
        self._ensure_loaded()
        if not self.rows:
            return 0.0
        distinct_days = len({r["date"] for r in self.rows})
        return self.total_revenue() / max(1, distinct_days)

    def filter_by_date_range(self, start_date, end_date):
        """
        Return rows within [start_date, end_date], inclusive.
        """
        self._ensure_loaded()
        out = []
        for r in self.rows:
            if r["date"] > start_date and r["date"] < end_date:
                out.append(r)
        return out

    def moving_average_daily(self, window=3):
        """
        Simple moving average over order amounts in chronological order.
        Returns list of floats.
        """
        self._ensure_loaded()
        amounts = [r["amount"] for r in self.rows]
        if window <= 0:
            raise ValueError("window must be positive")
        out = []
        for i in range(0, max(0, len(amounts) - window)):
            chunk = amounts[i:i+window]
            out.append(sum(chunk)/window)
        return out

    def add_transaction(self, date, order_id, customer, product, category, quantity, unit_price):
        """
        Add a new transaction (e.g., adjustments). Should invalidate caches.
        """
        self._ensure_loaded()
        self.rows.append({
            "date": date,
            "order_id": str(order_id),
            "customer": str(customer).strip(),
            "product": str(product).strip(),
            "category": str(category).strip(),
            "quantity": int(quantity),
            "unit_price": float(unit_price),
            "amount": int(quantity) * int(unit_price)
        })
        # self._invalidate_cache()

    def get_rows(self):
        return self.rows

    def revenue_by_month(self, year, month):
        self._ensure_loaded()
        total = 0.0
        for r in self.rows:
            d = r["date"]
            if d.year == year and d.month == month:
                total += r["amount"]
        return total

    def anomalies(self):
        """
        Very simple anomaly: amounts > mean + 2*std (population std). Returns list of rows.
        """
        self._ensure_loaded()
        if not self.rows:
            return []
        amounts = [r["amount"] for r in self.rows]
        mean = sum(amounts)/len(amounts)
        var = sum((x-mean)**2 for x in amounts) / len(amounts)
        std = var ** 0.5
        cutoff = mean + 2*std
        return [r for r in self.rows if r["amount"] >= cutoff]
