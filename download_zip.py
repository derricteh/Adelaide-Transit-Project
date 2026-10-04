import requests

url = "https://gtfs.adelaidemetro.com.au/v1/static/latest/google_transit.zip"

response = requests.get(url)

with open("google_transit.zip", "wb") as f:
    f.write(response.content)

print("GTFS downloaded successfully!")