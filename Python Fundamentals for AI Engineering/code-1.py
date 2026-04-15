# Parse a JSON file and extract specific values.

import json 

with open("data.json",'r+') as file:
    data = json.load(file)

for person in data:
    print(person["name"])
