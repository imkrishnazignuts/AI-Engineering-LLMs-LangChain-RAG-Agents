from langchain_core.prompts import ChatPromptTemplate
from fastapi import APIRouter,HTTPException
from .rag_pipeline import llm
from langchain_core.output_parsers import JsonOutputParser

router = APIRouter(
    prefix='/ai',
    tags=['ai related']
)

prompt = ChatPromptTemplate.from_template("""
You are an expert HR recruiter, copywriter, and job posting optimizer.

Your task is to improve the given job description.

Input Job Description:
{job_description}

Improve the job description by focusing on:

1. Clarity
- Make the text easy to understand
- Remove confusion
- Improve sentence structure

2. Grammar
- Fix grammar mistakes
- Correct punctuation
- Improve readability

3. Professionalism
- Use professional business language
- Make it attractive for candidates
- Maintain company reputation

4. SEO Keyword Richness
- Add relevant hiring keywords naturally
- Include role-related technical keywords
- Improve search visibility on job boards

Generate output in these 3 improvement modes:

1. Short and Crisp
- Concise version
- Direct and clear

2. Detailed and Formal
- Full professional version
- Structured and polished

3. Marketing Oriented
- Highly engaging version
- Attractive and persuasive for candidates

Return ONLY valid JSON in this format:

{{
  "short_and_crisp": "...",
  "detailed_and_formal": "...",
  "marketing_oriented": "..."
}}
""")

@router.post('/improve-description')
def improve_description(desc:str):
    if not desc:
        return HTTPException(status_code=404,detail="description is empty")
    chain = prompt | llm | JsonOutputParser()
    result = chain.invoke({
        "job_description":desc
    })
    return result


