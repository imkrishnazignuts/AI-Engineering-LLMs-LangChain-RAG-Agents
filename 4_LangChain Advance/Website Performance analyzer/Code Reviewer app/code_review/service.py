from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

prompt = PromptTemplate.from_template(
    """
You are a Senior Software Engineer and Expert Code Reviewer with strong experience in backend and frontend development.

Your task is to review the given code like a professional senior developer during a pull request review.

Analyze the code carefully and provide practical, honest, and useful feedback.

Code:
{code}

Return your review in valid JSON format with these keys only:

summary_of_code_quality
potential_bugs
performance_improvement_suggestions
security_considerations
readability_suggestions
fix_examples_high_level

Rules:
- Be constructive and professional
- Do not insult the code
- Explain clearly in simple words
- If code is good, mention that too
- If no issue found, explicitly say "No major issue found"
- Focus on real-world production standards
"""
)

parser = JsonOutputParser()

chain = prompt | llm | parser


def review_code_service(code: str):
    """
    Sends code to the LangChain + Ollama reviewer chain
    and returns structured JSON output.
    """
    return chain.invoke({"code": code})