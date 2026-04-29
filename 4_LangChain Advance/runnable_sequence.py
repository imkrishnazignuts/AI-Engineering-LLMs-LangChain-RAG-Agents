from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=1
)

poem_prompt= PromptTemplate(
    input_variables=['topic'],
    template="Create 4 line poem on the topic {topic}"
)

translate_prompt = PromptTemplate(
    input_variables=["poem"],
    template="translate it into spanish : {poem}"
)

output = StrOutputParser()
chain = poem_prompt | llm | (lambda x : {"poem":x} ) | translate_prompt | llm | output

print(chain.invoke({'topic':"star"}))



# Chain them: prompt → llm → prompt → llm
chain = (
    poem_prompt 
    | llm 
    | (lambda x: {"poem": x})  # Pass output to next step
    | translate_prompt 
    | llm
)

result = chain.invoke({"topic": "sunset"})
print(result)