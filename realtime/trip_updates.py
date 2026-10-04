import requests
import pandas as pd
from datetime import datetime, timezone
from google.transit import gtfs_realtime_pb2


# ============================================================
# 1. FILE LOCATIONS
# ============================================================

ROUTES_FILE = "./google_transit/routes.txt"
TRIPS_FILE = "./google_transit/trips.txt"
STOP_TIMES_FILE = "./google_transit/stop_times.txt"
STOPS_FILE = "./google_transit/stops.txt"

REALTIME_URL = (
    "https://gtfs.adelaidemetro.com.au/v1/realtime/trip_updates"
)


# ============================================================
# 2. LOAD STATIC GTFS
# ============================================================

print("Loading static GTFS data...")

routes = pd.read_csv(ROUTES_FILE)
trips = pd.read_csv(TRIPS_FILE)
stop_times = pd.read_csv(STOP_TIMES_FILE)
stops = pd.read_csv(STOPS_FILE)

print(f"Routes loaded: {len(routes):,}")
print(f"Trips loaded: {len(trips):,}")
print(f"Stop times loaded: {len(stop_times):,}")
print(f"Stops loaded: {len(stops):,}")


# ============================================================
# 3. DOWNLOAD GTFS-REALTIME TRIP UPDATES
# ============================================================

print("\nDownloading trip updates...")

response = requests.get(
    REALTIME_URL,
    timeout=30
)

if response.status_code != 200:

    print(
        "Failed to download trip updates."
    )

    print(
        "HTTP status:",
        response.status_code
    )

    exit()


print(
    "Trip updates downloaded successfully."
)

print(
    "Data size:",
    len(response.content),
    "bytes"
)


# ============================================================
# 4. PARSE GTFS-REALTIME FEED
# ============================================================

feed = gtfs_realtime_pb2.FeedMessage()

feed.ParseFromString(
    response.content
)

print(
    "Trip updates found:",
    len(feed.entity)
)


# ============================================================
# 5. PROCESS TRIP UPDATES
# ============================================================

trip_count = 0

stop_update_count = 0


for entity in feed.entity:

    # --------------------------------------------------------
    # Make sure this entity contains a trip update
    # --------------------------------------------------------

    if not entity.HasField("trip_update"):
        continue


    trip_update = entity.trip_update

    trip_count += 1


    # ========================================================
    # 6. GET TRIP INFORMATION
    # ========================================================

    trip_id = trip_update.trip.trip_id

    route_id = trip_update.trip.route_id


    # ========================================================
    # 7. FIND ROUTE
    # ========================================================

    route = routes[
        routes["route_id"].astype(str)
        == str(route_id)
    ]


    # ========================================================
    # 8. FIND TRIP
    # ========================================================

    trip = trips[
        trips["trip_id"].astype(str)
        == str(trip_id)
    ]


    # ========================================================
    # 9. PRINT TRIP INFORMATION
    # ========================================================

    print("\n" + "=" * 70)

    print("TRIP UPDATE")
    print("-" * 70)

    print(
        "Trip ID:",
        trip_id
    )

    print(
        "Route ID:",
        route_id
    )


    # ========================================================
    # 10. PRINT ROUTE INFORMATION
    # ========================================================

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
            "Route: Not found"
        )


    # ========================================================
    # 11. PRINT TRIP INFORMATION
    # ========================================================

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
            "Headsign:",
            trip_info.get(
                "trip_headsign",
                "Unknown"
            )
        )

    else:

        print(
            "Trip: Not found"
        )


    # ========================================================
    # 12. PROCESS STOP UPDATES
    # ========================================================

    print("\nSTOP UPDATES")
    print("-" * 70)


    for stop_update in trip_update.stop_time_update:

        stop_update_count += 1


        # ----------------------------------------------------
        # Get stop ID
        # ----------------------------------------------------

        stop_id = stop_update.stop_id


        # ----------------------------------------------------
        # Find stop in static GTFS
        # ----------------------------------------------------

        stop = stops[
            stops["stop_id"].astype(str)
            == str(stop_id)
        ]


        if not stop.empty:

            stop_info = stop.iloc[0]

            stop_name = stop_info.get(
                "stop_name",
                "Unknown"
            )

        else:

            stop_name = "Unknown"


        # ----------------------------------------------------
        # Get static schedule
        # ----------------------------------------------------

        scheduled = stop_times[
            (stop_times["trip_id"].astype(str) == str(trip_id))
            &
            (stop_times["stop_id"].astype(str) == str(stop_id))
        ]


        # ----------------------------------------------------
        # Get arrival information
        # ----------------------------------------------------

        predicted_arrival = None
        arrival_delay = None


        if stop_update.HasField("arrival"):

            if stop_update.arrival.HasField(
                "time"
            ):

                predicted_arrival = (
                    stop_update.arrival.time
                )

            if stop_update.arrival.HasField(
                "delay"
            ):

                arrival_delay = (
                    stop_update.arrival.delay
                )


        # ----------------------------------------------------
        # Get departure information
        # ----------------------------------------------------

        predicted_departure = None
        departure_delay = None


        if stop_update.HasField("departure"):

            if stop_update.departure.HasField(
                "time"
            ):

                predicted_departure = (
                    stop_update.departure.time
                )

            if stop_update.departure.HasField(
                "delay"
            ):

                departure_delay = (
                    stop_update.departure.delay
                )


        # ====================================================
        # PRINT STOP INFORMATION
        # ====================================================

        print(
            f"\nStop ID: {stop_id}"
        )

        print(
            f"Stop Name: {stop_name}"
        )


        # ----------------------------------------------------
        # Scheduled arrival
        # ----------------------------------------------------

        if not scheduled.empty:

            scheduled_info = scheduled.iloc[0]

            scheduled_arrival = (
                scheduled_info.get(
                    "arrival_time",
                    "Unknown"
                )
            )

            scheduled_departure = (
                scheduled_info.get(
                    "departure_time",
                    "Unknown"
                )
            )

            print(
                "Scheduled arrival:",
                scheduled_arrival
            )

            print(
                "Scheduled departure:",
                scheduled_departure
            )

        else:

            print(
                "Scheduled time: Not found"
            )


        # ----------------------------------------------------
        # Predicted arrival
        # ----------------------------------------------------

        if predicted_arrival is not None:

            predicted_datetime = (
                datetime.fromtimestamp(
                    predicted_arrival,
                    tz=timezone.utc
                )
            )

            print(
                "Predicted arrival:",
                predicted_datetime
            )

        else:

            print(
                "Predicted arrival: Not available"
            )


        # ----------------------------------------------------
        # Arrival delay
        # ----------------------------------------------------

        if arrival_delay is not None:

            delay_minutes = (
                arrival_delay / 60
            )

            print(
                f"Arrival delay: "
                f"{delay_minutes:.1f} minutes"
            )

        else:

            print(
                "Arrival delay: Not available"
            )


        # ----------------------------------------------------
        # Predicted departure
        # ----------------------------------------------------

        if predicted_departure is not None:

            predicted_datetime = (
                datetime.fromtimestamp(
                    predicted_departure,
                    tz=timezone.utc
                )
            )

            print(
                "Predicted departure:",
                predicted_datetime
            )


        # ----------------------------------------------------
        # Departure delay
        # ----------------------------------------------------

        if departure_delay is not None:

            delay_minutes = (
                departure_delay / 60
            )

            print(
                f"Departure delay: "
                f"{delay_minutes:.1f} minutes"
            )


# ============================================================
# 13. SUMMARY
# ============================================================

print("\n" + "=" * 70)

print("FINISHED")

print(
    "Trips processed:",
    trip_count
)

print(
    "Stop updates processed:",
    stop_update_count
)