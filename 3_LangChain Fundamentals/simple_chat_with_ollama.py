from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser 

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.6
)

prompt = PromptTemplate(
    input_variables=['game_name'],
    template="give me details about {game_name} in 2 lines"
)

output = StrOutputParser()

chain = prompt | llm | output


game_name = input("Enter any game name: ")
result = chain.invoke({"game_name":game_name})

print(result)