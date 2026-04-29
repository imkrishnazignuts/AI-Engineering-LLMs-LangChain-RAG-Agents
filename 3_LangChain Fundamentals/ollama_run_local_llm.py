from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.4
)


prompt = PromptTemplate(
    input_variables=['cuisine'],
    template="I want to make a restaurant for a {cuisine} food. suggest me a unique name for that restaurant give me only one"
)

parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({
    "cuisine": "indian"
})

print(result)