import requests 
response = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={"latitude": 19.07, "longitude": 72.87, "current_weather": True}  # Mumbai
)

print(response.status_code)
print(response.json())