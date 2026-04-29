from fastapi import APIRouter,Depends,HTTPException
from fastapi import UploadFile,File
from auth import get_current_user
from pypdf import PdfReader
from io import BytesIO
from langchain_core.prompts import ChatPromptTemplate
from .rag_pipeline import llm,vectorstore
from langchain_core.output_parsers import JsonOutputParser

router = APIRouter(
    prefix='/ai',
    tags=['ai related']
)

prompt = ChatPromptTemplate.from_template("""
You are an expert AI Job Recommendation Assistant.

Your task is to analyze the candidate resume and recommend the most suitable jobs only from the provided job database context.

IMPORTANT RULES:
1. Use ONLY the provided jobs context.
2. Do not create fake jobs.
3. Match based on:
   - Skills
   - Experience
   - Education
   - Projects
   - Tools / Technologies
   - Location preference if available
4. If some skills are missing, mention them.
5. Rank jobs from best match to lowest match.
6. Keep response practical and short.
7. Return ONLY valid JSON.
8. No markdown.
9. No explanation outside JSON.

Resume:
{resume}

Jobs Database Context:
{context}

Return JSON in this format:

{{
  "candidate_summary": {{
    "primary_skills": [],
    "experience_level": "",
    "recommended_domain": ""
  }},
  "recommended_jobs": [
    {{
      "rank": 1,
      "job_title": "",
      "match_score": 0,
      "reason": "",
      "missing_skills": [],
      "location": "",
      "salary_range": ""
    }}
  ],
  "final_advice": ""
}}
""")



@router.post('/recommend')
async def recommend_job(resume:UploadFile=File(...),user:dict=Depends(get_current_user)):
    if not user:
        return HTTPException(status_code=403,detail="Unauthenticated user found")
    pdf_byte = await resume.read()
    
    if not pdf_byte:
        return HTTPException(status_code=404,detail="No content found in file")
    
    reader = PdfReader(BytesIO(pdf_byte))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    docs = vectorstore.similarity_search(text,k=15)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    chain = prompt | llm | JsonOutputParser()

    answer = chain.invoke({
        "resume":text,
        "context":context
    })

    return answer