from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.6
)

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Act like an AI assistant, but only answer if the topic is within "
        "Django, Python, AWS, Machine Learning, or technical communication. like java c++ or anything which is part of technology "
        "you can talk about things related to Technology"        
        "Also include one extra key-value pair called confidence with value "
        "high, medium, or low."
        "add this extra confidence key to last in response"
        "Strictly check for user input should be technical"
        "if out of technical just say sorry in response"
    ),
    HumanMessagePromptTemplate.from_template("{user_query}")
])


output = StrOutputParser()

chain = prompt | llm | output

print("## TECHNICAL DISCUUSION CHATBOT")
print("Chat started to leave type bye, exit, quit ")


while True:
    user_query = input("you: ")
    
    if user_query.lower() in ["bye" , "exit" , "quit"]:
        break
    
    if user_query.strip() == "":
        continue
    
    response = ""
    print("generating",end="")
    for chunk in chain.stream({"user_query": user_query}):
        response +=chunk
        print(".", end="", flush=True)

    print("\n") 
    print("Assistant: ", end="", flush=True)
    print(response)
    print("\n") 
    
print("chat ended!")