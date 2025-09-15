"""Exercise 1 (Strategy + Factory)
Refactor the naive exporter so new formats can be added without
modifying export(). Keep the naive version for comparison.
"""

import json, csv, io

# NAIVE IMPLEMENTATION (start here)
def export(data, fmt):
    if fmt == "json":
        return json.dumps(data)
    elif fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()
    else:
        raise ValueError("unknown format")

# TODO:
#   1) Create exporter classes (JsonExport, CsvExport, ...), each with .export(data) -> str
#   2) Write make_exporter(fmt) -> exporter object
#   3) Re-implement export(data, fmt) to use the factory + strategies
#   4) Add a new format: 'xml' or 'yaml' (your choice) to prove Open/Closed
#   5) (Nice to have) Add a small demo comparing naive vs refactored

if __name__ == "__main__":
    sample = [{"name": "alice", "age": 30}, {"name": "bob", "age": 25}]
    print("[Naive JSON]\n", export(sample, "json"))
    print("\n[Naive CSV]\n", export(sample, "csv"))
    print("\nNow implement the Strategy + Factory version (see TODO).")
