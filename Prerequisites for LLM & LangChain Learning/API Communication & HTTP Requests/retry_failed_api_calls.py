import requests 
import time

def retry_get(url):
    for i in range(1,4):
        try:
            print("Getting Data")
            response = requests.get(url,params={"latitude": 19.07, "longitude": 72.87, "current_weather": True})
            response.raise_for_status()
            print(response.json())
            break
        except requests.exceptions.RequestException:
            print("api called failed")
            print("wait for 5 Seconds....")
            time.sleep(5)
    if i==3:
        print("Api call failed")

print("exiting")

retry_get("https://api.open-meteo.com/v1/forecast")
