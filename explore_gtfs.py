import pandas as pd
from pathlib import Path

GTFS_DIR = Path("google_transit")

files = [
    "agency.txt",
    "routes.txt",
    "trips.txt",
    "stops.txt",
    "stop_times.txt",
    "shapes.txt",
    "calendar.txt",
    "calendar_dates.txt",
    "transfers.txt",
    "booking_rules.txt",
    "feed_info.txt"
]

for filename in files:
    path = GTFS_DIR / filename

    try:
        df = pd.read_csv(path)

        print("\n" + "=" * 60)
        print(filename)
        print("=" * 60)

        print("Rows:", len(df))
        print("Columns:", list(df.columns))
        print("\nFirst 3 rows:")
        print(df.head(3))

    except Exception as e:
        print(f"Error reading {filename}: {e}")