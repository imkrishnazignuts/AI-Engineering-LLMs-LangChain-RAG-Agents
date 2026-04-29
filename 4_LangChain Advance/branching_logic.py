from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=1
)

technical_prompt = PromptTemplate(
    input_variables=["question"],
    template="Explain {question} in technical terms"
)

simple_prompt = PromptTemplate(
    input_variables=["question"],
    template="Explain {question} in simple terms to 5 year old baby"
)

output = StrOutputParser()
def route_for_question(input_dict):
    question = input_dict["question"].lower()
    if question in ['api','ai','llm','python','django','fastapi','json']:
        return 'technical'
    else: 
        return 'simple'

branch= RunnableBranch(
    (lambda x : route_for_question(x) == 'technical',technical_prompt | llm | output),
    (lambda x:route_for_question(x) == 'simple',simple_prompt | llm | output),
    simple_prompt | llm | output
)

result = branch.invoke({'question':'cat'})
print(result)