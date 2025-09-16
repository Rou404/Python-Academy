
# Run me with: python tests_movie.py
import os, csv, tempfile, unittest, shutil
from datetime import date

from movie_analytics import MovieAnalytics

DATA = [
    # date, view_id, user, title, genre, minutes, rating
    ("2024-06-01", "v1001", "amy",  "Inception",      "sci-fi",    148, 5.0),
    ("2024-06-02", "v1002", "ben",  "Spirited Away",  "animation", 125, 4.5),
    ("2024-06-03", "v1003", "amy",  "Inception",      "sci-fi",    148, 4.0),
    ("2024-06-10", "v1004", "cara", "Amélie",         "drama",     122, 4.0),
    ("2024-06-15", "v1005", "dan",  "Inside Out",     "Animation", 102, 4.5),
    ("2024-07-01", "v1006", "amy",  "Interstellar",   "sci-fi",    169, 5.0),
    ("2024-07-05", "v1007", "ben",  "Inside Out",     "animation", 102, 4.0),
    ("2024-07-10", "v1008", "cara", "Inception",      "sci-fi",    148, 5.0),
    ("2024-07-20", "v1009", "dan",  "Amélie",         "drama",     122, 3.5),
]

TOTAL_MINUTES = 1186
JUNE_MINUTES = 645
JULY_MINUTES = 541

class MovieAnalyticsTests(unittest.TestCase):
    def setUp(self):
        # create a temp directory with a CSV
        self.tmpdir = tempfile.mkdtemp(prefix="movies_dbg_")
        self.csv_path = os.path.join(self.tmpdir, "watch_log.csv")
        with open(self.csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date","view_id","user","title","genre","minutes","rating"])
            for row in DATA:
                w.writerow(row)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def make_ma(self):
        return MovieAnalytics(self.csv_path)

    def test_01_total_views(self):
        ma = self.make_ma()
        self.assertEqual(ma.total_views(), len(DATA))

    def test_02_total_minutes(self):
        ma = self.make_ma()
        self.assertEqual(ma.total_minutes(), TOTAL_MINUTES)

    def test_03_average_rating(self):
        ma = self.make_ma()
        self.assertAlmostEqual(ma.average_rating(), sum(r[-1] for r in DATA)/len(DATA), places=6)

    def test_04_minutes_by_user_with_cache(self):
        ma = self.make_ma()
        self.assertEqual(ma.minutes_by_user("amy"), 148+148+169)
        # cache should update after new view
        ma.add_view("2024-07-21", "v2000", "amy", "Short", "shorts", 90, 4.0)
        self.assertEqual(ma.minutes_by_user("amy"), 148+148+169+90)

    def test_05_minutes_by_genre_case_insensitive(self):
        ma = self.make_ma()
        self.assertEqual(ma.minutes_by_genre("animation"), 125+102+102)
        self.assertEqual(ma.minutes_by_genre("DRAMA"), 122+122)
        self.assertEqual(ma.minutes_by_genre("sci-fi"), 148+148+169+148)

    def test_06_top_titles(self):
        ma = self.make_ma()
        top2 = ma.top_titles(2)
        self.assertEqual(top2, ["Inception", "Amélie"])

    def test_07_average_minutes_per_entry(self):
        ma = self.make_ma()
        self.assertAlmostEqual(ma.average_minutes_per_entry(), TOTAL_MINUTES/len(DATA), places=6)

    def test_08_filter_by_date_range_inclusive(self):
        ma = self.make_ma()
        start = date(2024,6,3)
        end = date(2024,7,5)
        subset = ma.filter_by_date_range(start, end)
        # dates included: 06-03, 06-10, 06-15, 07-01, 07-05 -> 5 entries totalling 643 minutes
        self.assertEqual(len(subset), 5)
        self.assertEqual(sum(r["minutes"] for r in subset), 643)

    def test_09_moving_average_window(self):
        ma = self.make_ma()
        ma_series = ma.moving_average_minutes(window=3)
        # length should be N - window + 1 = 7
        self.assertEqual(len(ma_series), 7)
        self.assertAlmostEqual(ma_series[0], (148+125+148)/3.0, places=6)
        self.assertAlmostEqual(ma_series[-1], (169+148+122)/3.0, places=6)

    def test_10_monthly_minutes(self):
        ma = self.make_ma()
        self.assertEqual(ma.monthly_minutes(2024,6), JUNE_MINUTES)
        self.assertEqual(ma.monthly_minutes(2024,7), JULY_MINUTES)

    def test_11_anomalies(self):
        ma = self.make_ma()
        anomalies = ma.anomalies()
        # only the 169-minute view should be an anomaly (mean + 1.5*std cutoff)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["view_id"], "v1006")

if __name__ == "__main__":
    unittest.main(verbosity=2)
