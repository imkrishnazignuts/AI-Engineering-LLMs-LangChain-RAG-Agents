

with open("input.txt","r+") as file:
    data = file.read()
    prompt = f"""you are an ai assistant analyze the input and give me the answer for this \n{data} """
    print(prompt)