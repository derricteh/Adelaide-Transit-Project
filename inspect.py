import pandas as pd

routes = pd.read_csv("google_transit/routes.txt")
trips = pd.read_csv("google_transit/trips.txt")

vehicle = entity.vehicle

route_id = vehicle.trip.route_id
trip_id = vehicle.trip.trip_id