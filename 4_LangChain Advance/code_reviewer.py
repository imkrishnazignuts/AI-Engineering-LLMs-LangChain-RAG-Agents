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

Return your review in the following structured format:

1. Summary of Code Quality
- Overall quality of the code
- Strengths
- Areas needing improvement

2. Potential Bugs
- Logical errors
- Edge cases not handled
- Possible runtime issues
- Wrong assumptions in code

3. Performance Improvement Suggestions
- Slow operations
- Unnecessary loops
- Repeated database/API calls
- Memory usage improvements
- Better algorithms if needed

4. Security Considerations
- Input validation issues
- SQL injection risks
- XSS risks
- Authentication/authorization concerns
- Sensitive data exposure
- Hardcoded secrets

5. Readability Suggestions
- Naming improvements
- Code structure
- Function size
- Reusability
- Comments/docstrings
- Formatting/style issues

6. Fix Examples (High Level)
- Suggest better approach
- Refactor ideas
- Best practices to apply

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

code = input("Enter code in single line: ")
result = chain.invoke({"code":code})

print(result)