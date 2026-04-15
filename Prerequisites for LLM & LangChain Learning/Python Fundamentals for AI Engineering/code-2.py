text = """name:krishna,age:20,city:"bhavnagar"
name:unknown,age:21,city:"gandhinagar" 
name:known,age:22,city:"ahemdabad" 
        """
peoples = []
for line in text.strip().split("\n"):
    parts = line.split(",")    
    person = {}

    for part in parts:
        key,value = part.split(":")
        person[key] = value
    peoples.append(person)
print(peoples)