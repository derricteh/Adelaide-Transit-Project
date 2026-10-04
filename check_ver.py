import requests

url = "https://gtfs.adelaidemetro.com.au/v1/static/latest/version.txt"

version = requests.get(url).text

print("GTFS version:", version)
# 1703
