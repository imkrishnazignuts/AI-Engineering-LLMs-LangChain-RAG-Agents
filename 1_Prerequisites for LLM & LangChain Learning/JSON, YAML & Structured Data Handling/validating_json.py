import json

json_data= '{"name":"krishna","age":20}'

try:
    data = json.loads(json_data)
    print(data)
except json.JSONDecodeError:
    print("not a valid json")