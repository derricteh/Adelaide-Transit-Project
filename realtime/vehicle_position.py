import requests
import pandas as pd
from google.transit import gtfs_realtime_pb2


# ============================================================
# 1. FILE LOCATIONS
# ============================================================

ROUTES_FILE = "./google_transit/routes.txt"
TRIPS_FILE = "./google_transit/trips.txt"
STOP_TIMES_FILE = "./google_transit/stop_times.txt"
STOPS_FILE = "./google_transit/stops.txt"

REALTIME_URL = (
    "https://gtfs.adelaidemetro.com.au/v1/realtime/vehicle_positions"
)


# ============================================================
# 2. LOAD STATIC GTFS DATA
# ============================================================

print("Loading static GTFS data...")

routes = pd.read_csv(ROUTES_FILE)
trips = pd.read_csv(TRIPS_FILE)
stop_times = pd.read_csv(STOP_TIMES_FILE)
stops = pd.read_csv(STOPS_FILE)

print(f"Loaded {len(routes):,} routes")
print(f"Loaded {len(trips):,} trips")
print(f"Loaded {len(stop_times):,} stop-time records")
print(f"Loaded {len(stops):,} stops")


# ============================================================
# 3. DOWNLOAD GTFS-REALTIME VEHICLE POSITIONS
# ============================================================

print("\nDownloading realtime vehicle positions...")

response = requests.get(
    REALTIME_URL,
    timeout=30
)

if response.status_code != 200:
    print("Failed to download realtime data.")
    print("HTTP status:", response.status_code)
    exit()

print("Realtime data downloaded successfully.")
print("Data size:", len(response.content), "bytes")


# ============================================================
# 4. PARSE GTFS-REALTIME DATA
# ============================================================

feed = gtfs_realtime_pb2.FeedMessage()

feed.ParseFromString(response.content)

print(
    "Realtime vehicles found:",
    len(feed.entity)
)


# ============================================================
# 5. PROCESS EACH VEHICLE
# ============================================================

vehicle_count = 0

for entity in feed.entity:

    # Skip entities that don't contain vehicle information
    if not entity.HasField("vehicle"):
        continue

    vehicle = entity.vehicle

    vehicle_count += 1

    # --------------------------------------------------------
    # REALTIME INFORMATION
    # --------------------------------------------------------

    vehicle_id = vehicle.vehicle.id
    trip_id = vehicle.trip.trip_id
    route_id = vehicle.trip.route_id

    latitude = vehicle.position.latitude
    longitude = vehicle.position.longitude

    speed = vehicle.position.speed
    bearing = vehicle.position.bearing


    # ========================================================
    # 6. FIND ROUTE
    # ========================================================

    route = routes[
        routes["route_id"].astype(str)
        == str(route_id)
    ]


    # ========================================================
    # 7. FIND TRIP
    # ========================================================

    trip = trips[
        trips["trip_id"].astype(str)
        == str(trip_id)
    ]


    # ========================================================
    # 8. FIND SCHEDULED STOP TIMES FOR THIS TRIP
    # ========================================================

    trip_stop_times = stop_times[
        stop_times["trip_id"].astype(str)
        == str(trip_id)
    ].copy()


    # ========================================================
    # 9. JOIN STOP TIMES WITH STOP INFORMATION
    # ========================================================

    if not trip_stop_times.empty:

        trip_stop_times = trip_stop_times.merge(
            stops[
                [
                    "stop_id",
                    "stop_name",
                    "stop_lat",
                    "stop_lon"
                ]
            ],
            on="stop_id",
            how="left"
        )

        # Make sure stops are in the correct order
        if "stop_sequence" in trip_stop_times.columns:

            trip_stop_times = trip_stop_times.sort_values(
                "stop_sequence"
            )


    # ========================================================
    # 10. PRINT VEHICLE INFORMATION
    # ========================================================

    print("\n" + "=" * 70)

    print("VEHICLE")
    print("-" * 70)

    print("Vehicle ID:", vehicle_id)

    print("Trip ID:", trip_id)

    print("Realtime Route ID:", route_id)


    # ========================================================
    # 11. PRINT ROUTE INFORMATION
    # ========================================================

    print("\nROUTE")
    print("-" * 70)

    if not route.empty:

        route_info = route.iloc[0]

        print(
            "Route:",
            route_info.get(
                "route_short_name",
                "Unknown"
            )
        )

        print(
            "Route Name:",
            route_info.get(
                "route_long_name",
                "Unknown"
            )
        )

    else:

        print(
            "Route: Not found in static GTFS"
        )


    # ========================================================
    # 12. PRINT TRIP INFORMATION
    # ========================================================

    print("\nTRIP")
    print("-" * 70)

    if not trip.empty:

        trip_info = trip.iloc[0]

        print(
            "Direction:",
            trip_info.get(
                "direction_id",
                "Unknown"
            )
        )

        print(
            "Trip Headsign:",
            trip_info.get(
                "trip_headsign",
                "Unknown"
            )
        )

    else:

        print(
            "Trip: Not found in static GTFS"
        )


    # ========================================================
    # 13. PRINT LIVE LOCATION
    # ========================================================

    print("\nLIVE LOCATION")
    print("-" * 70)

    print(
        "Latitude:",
        latitude
    )

    print(
        "Longitude:",
        longitude
    )

    print(
        "Speed:",
        speed
    )

    print(
        "Bearing:",
        bearing
    )


    # ========================================================
    # 14. PRINT SCHEDULED STOPS
    # ========================================================

    print("\nSCHEDULED STOPS")
    print("-" * 70)

    if not trip_stop_times.empty:

        print(
            "Number of stops:",
            len(trip_stop_times)
        )

        # Show first 10 stops
        display_stops = trip_stop_times.head(10)

        for _, stop in display_stops.iterrows():

            print(
                f"{stop['stop_sequence']:>3} | "
                f"{stop['stop_name']} | "
                f"Arrival: {stop['arrival_time']} | "
                f"Departure: {stop['departure_time']}"
            )

        if len(trip_stop_times) > 10:

            print(
                f"... and "
                f"{len(trip_stop_times) - 10} more stops"
            )

    else:

        print(
            "No scheduled stops found for this trip."
        )


# ============================================================
# 15. SUMMARY
# ============================================================

print("\n" + "=" * 70)

print("Finished.")

print(
    "Vehicles processed:",
    vehicle_count
)