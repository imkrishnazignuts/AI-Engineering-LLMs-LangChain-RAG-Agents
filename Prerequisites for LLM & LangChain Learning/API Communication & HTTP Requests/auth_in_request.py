import requests 


response = requests.get("api_url",
                        headers={"Authorization" : f"Bearer {TOKEN}"})

print(response.status_code)
print(response.json())
    