# Run me with: python tests.py
import os, csv, tempfile, unittest, shutil
from datetime import date

from sales_analytics import SalesAnalytics

DATA = [
    # date, order_id, customer, product, category, quantity, unit_price
    ("2024-03-01", "1001", "alice", "coffee",   "beverages", 2, 3.50),
    ("2024-03-02", "1002", "bob",   "tea",      "beverages", 1, 2.50),
    ("2024-03-03", "1003", "alice", "sandwich", "food",      1, 5.00),
    ("2024-03-15", "1004", "carol", "coffee",   "beverages", 3, 3.50),
    ("2024-03-20", "1005", "dan",   "salad",    "food",      1, 7.00),
    ("2024-04-01", "1006", "alice", "coffee",   "beverages", 1, 3.50),
    ("2024-04-05", "1007", "bob",   "sandwich", "food",      2, 5.00),
    ("2024-04-10", "1008", "carol", "cake",     "dessert",   1, 4.00),
    ("2024-04-20", "1009", "dan",   "coffee",   "beverages", 4, 3.50),
    ("2024-05-01", "1010", "alice", "tea",      "beverages", 2, 2.50),
    ("2024-05-07", "1011", "bob",   "salad",    "food",      3, 7.00),
    ("2024-05-15", "1012", "carol", "sandwich", "food",      1, 5.00),
]

# Expected totals
TOTAL_REVENUE = 94.5
MARCH_TOTAL = 32.0
APRIL_TOTAL = 31.5
MAY_TOTAL = 31.0

class SalesAnalyticsTests(unittest.TestCase):
    def setUp(self):
        # create a temp directory with a CSV
        self.tmpdir = tempfile.mkdtemp(prefix="sales_dbg_")
        self.csv_path = os.path.join(self.tmpdir, "sales.csv")
        with open(self.csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date","order_id","customer","product","category","quantity","unit_price"])
            for row in DATA:
                w.writerow(row)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def make_sa(self):
        return SalesAnalytics(self.csv_path)

    def test_01_total_orders(self):
        sa = self.make_sa()
        self.assertEqual(sa.total_orders(), len(DATA))

    def test_02_total_revenue(self):
        sa = self.make_sa()
        self.assertAlmostEqual(sa.total_revenue(), TOTAL_REVENUE, places=4)

    def test_03_revenue_by_customer(self):
        sa = self.make_sa()
        self.assertAlmostEqual(sa.revenue_by_customer("alice"), 20.5, places=4)
        # cache should update after new transaction
        sa.add_transaction("2024-05-20", "2000", "alice", "coffee", "beverages", 1, 3.50)
        self.assertAlmostEqual(sa.revenue_by_customer("alice"), 24.0, places=4)

    def test_04_revenue_by_category(self):
        sa = self.make_sa()
        self.assertAlmostEqual(sa.revenue_by_category("beverages"), 42.5, places=4)
        self.assertAlmostEqual(sa.revenue_by_category("food"), 48.0, places=4)
        self.assertAlmostEqual(sa.revenue_by_category("dessert"), 4.0, places=4)

    def test_05_top_products(self):
        sa = self.make_sa()
        top2 = sa.top_products(2)
        self.assertEqual(top2, ["coffee", "salad"])

    def test_06_average_order_value(self):
        sa = self.make_sa()
        self.assertAlmostEqual(sa.average_order_value(), TOTAL_REVENUE/len(DATA), places=6)

    def test_07_filter_by_date_range_inclusive(self):
        sa = self.make_sa()
        start = date(2024,3,3)
        end = date(2024,4,5)
        subset = sa.filter_by_date_range(start, end)
        # dates included: 03-03, 03-15, 03-20, 04-01, 04-05 -> 5 orders totalling 36.0
        self.assertEqual(len(subset), 5)
        self.assertAlmostEqual(sum(r["amount"] for r in subset), 36.0, places=4)

    def test_08_moving_average_window(self):
        sa = self.make_sa()
        ma = sa.moving_average_daily(window=3)
        # length should be N - window + 1 = 10
        self.assertEqual(len(ma), 10)
        self.assertAlmostEqual(ma[0], (7.0+2.5+5.0)/3.0, places=6)
        self.assertAlmostEqual(ma[-1], (5.0+21.0+5.0)/3.0, places=6)

    def test_09_revenue_by_month(self):
        sa = self.make_sa()
        self.assertAlmostEqual(sa.revenue_by_month(2024,3), MARCH_TOTAL, places=4)
        self.assertAlmostEqual(sa.revenue_by_month(2024,4), APRIL_TOTAL, places=4)
        self.assertAlmostEqual(sa.revenue_by_month(2024,5), MAY_TOTAL, places=4)

    def test_10_anomalies(self):
        sa = self.make_sa()
        anomalies = sa.anomalies()
        # only the 21.0 order should be an anomaly (mean + 2*std cutoff)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["order_id"], "1011")

    def test_11_external_mutation_should_not_break(self):
        sa = self.make_sa()
        rows = sa.get_rows()
        rows.pop()  # modify the returned list
        # original object should be unaffected if implemented safely
        self.assertEqual(sa.total_orders(), len(DATA))

if __name__ == "__main__":
    unittest.main(verbosity=2)
