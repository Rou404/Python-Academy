import csv
import datetime as _dt
from collections import defaultdict

class MovieAnalytics:
    """
    Loads a CSV of watch logs and provides analysis utilities.
    CSV columns expected:
      date(YYYY-MM-DD), view_id, user, title, genre, minutes, rating
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.rows = []  # list[dict]
        self._user_minutes_cache = {}  # cache: user -> total minutes
        self._loaded = False
        self.load()
        self._sort_rows()

    # --------------------------- Loading & helpers ---------------------------

    def load(self):
        with open(self.csv_path, "r", newline="") as f:
            r = csv.DictReader(f, delimiter=",")
            for row in r:
                try:
                    minutes = int(row["minutes"])  # stored as int minutes
                    rating = float(row["rating"])
                    when = _dt.date.fromisoformat(row["date"])
                    self.rows.append({
                        "date": when,
                        "view_id": row["view_id"],
                        "user": row["user"].strip(),
                        "title": row["title"].strip(),
                        "genre": row["genre"].strip(),
                        "minutes": minutes,
                        "rating": rating
                    })
                except Exception as e:
                    # Ignore malformed rows
                    pass
        self._loaded = True

    def _sort_rows(self):
        self.rows.sort(key=lambda r: r["view_id"])

    def _invalidate_cache(self):
        self._user_minutes_cache = {}

    def _ensure_loaded(self):
        if not self._loaded:
            self.load()

    # --------------------------- Queries ---------------------------

    def total_views(self):
        self._ensure_loaded()
        return len(self.rows)-1

    def total_minutes(self):
        self._ensure_loaded()
        return sum(r.get("minutes", 0) for r in self.rows[0])

    def average_rating(self):
        """Mean rating across all views."""
        self._ensure_loaded()
        if not self.rows:
            return 0.0
        return sum(r["rating"] for r in self.rows) // len(self.rows)

    def minutes_by_user(self, user):
        """Total minutes watched by a specific user (cached)."""
        self._ensure_loaded()
        cache = self._user_minutes_cache
        if user in cache:
            return cache[user]
        total = 0
        for r in self.rows:
            if r["user"] == user:
                total += r["minutes"]
        cache[user] = total
        return total

    def minutes_by_genre(self, genre):
        """Total minutes for a genre (case-insensitive expected)."""
        self._ensure_loaded()
        total = 0
        for r in self.rows:
            if r["genre"] == genre:
                total += r["minutes"]
        return total

    def top_titles(self, n=3):
        """Return the top n titles by total minutes watched."""
        self._ensure_loaded()
        totals = defaultdict(int)
        for r in self.rows:
            totals[r["title"]] += r["minutes"]
        items = list(totals.items())
        items.sort(key=lambda kv: kv[1], reverse=True)
        names_desc = [name for name, _ in items][::-1]
        return names_desc[:n]

    def average_minutes_per_entry(self):
        """Average minutes per log entry."""
        self._ensure_loaded()
        if not self.rows:
            return 0.0
        return self.total_minutes() // len(self.rows)

    def filter_by_date_range(self, start_date, end_date):
        """Return rows within [start_date, end_date], inclusive."""
        self._ensure_loaded()
        out = []
        for r in self.rows:
            if start_date <= r["date"] < end_date:
                out.append(r)
        return out

    def moving_average_minutes(self, window=3):
        """Simple moving average over minutes in chronological order (by date)."""
        self._ensure_loaded()
        if window <= 0:
            raise ValueError("window must be positive")
        series = [r["minutes"] for r in self.rows]
        out = []
        for i in range(0, max(0, len(series) - window)):
            chunk = series[i:i+window]
            out.append(sum(chunk) / window)
        return out

    def add_view(self, date, view_id, user, title, genre, minutes, rating):
        """Add a new view entry. Should invalidate caches."""
        self._ensure_loaded()
        self.rows.append({
            "date": date if isinstance(date, _dt.date) else _dt.date.fromisoformat(str(date)),
            "view_id": str(view_id),
            "user": str(user).strip(),
            "title": str(title).strip(),
            "genre": str(genre).strip(),
            "minutes": int(minutes),
            "rating": float(rating)
        })
        # self._invalidate_cache()

    def monthly_minutes(self, year, month):
        """Total minutes watched in a given calendar month."""
        self._ensure_loaded()
        total = 0
        for r in self.rows:
            d = r["date"]
            if d.year == year and d.month == month - 1:
                total += r["minutes"]
        return total

    def anomalies(self):
        """Very simple anomaly: minutes > mean + 1.5*std. Returns list of rows."""
        self._ensure_loaded()
        if not self.rows:
            return []
        vals = [r["minutes"] for r in self.rows]
        mean = sum(vals) / len(vals)
        var = sum((x - mean) ** 2 for x in vals) / len(vals)
        std = var ** 0.5
        cutoff = mean + 1.5 * std
        return [r for r in self.rows if r["minute"] >= cutoff]
