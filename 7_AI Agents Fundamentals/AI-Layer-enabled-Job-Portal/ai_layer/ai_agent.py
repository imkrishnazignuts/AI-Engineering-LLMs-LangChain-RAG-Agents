from .rag_pipeline import llm,vectorstore
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.tools import tool
import httpx
from langchain.agents import create_agent
import json 

router = APIRouter(
    prefix='/ai',
    tags=['ai related']
)

class agentRequest(BaseModel):
    question:str

@tool
def access_of_job_details():
   """
    Fetch all jobs from the FastAPI jobs endpoint.
    Use this when the user asks about jobs, job list, salary, location, or active jobs.
   Do not call any tool named JSON.
   Do not use markdown.
    """
   login = httpx.post(
    "http://127.0.0.1:8000/auth/token",
    data={
        "username": "krishna",
        "password": "1234"
    }
    )
   token = login.json()["access_token"]

   headers = {
      "Authorization": f"Bearer {token}"
   }

   url = "http://127.0.0.1:8000/api/v1/jobs/"
   response = httpx.get(url,headers=headers)
   response.raise_for_status()

   return response.json()

@tool
def access_of_company_details():
   """
    Fetch company data from the FastAPI recruiters endpoint.

    Use this tool when the user asks about:
    - Company names
    - Company list
    - Recruiters
    - Hiring companies
    - Company locations
    - Salary ranges
    - Job openings
    - Active companies
    - Which company offers specific roles
    - Companies in a specific city
    - Top / best companies based on available data

   Do not call any tool named JSON.
   Do not use markdown.
    """
   login = httpx.post(
    "http://127.0.0.1:8000/auth/token",
    data={
        "username": "krishna",
        "password": "1234"
    }
    )
   token = login.json()["access_token"]

   headers = {
      "Authorization": f"Bearer {token}"
   }
   url = "http://127.0.0.1:8000/api/v1/recruiters/"
   response = httpx.get(url,headers=headers)
   response.raise_for_status()

   return response.json()

@tool
def access_of_profile_details():
   """
    Fetch candidate public profiles from the FastAPI candidates endpoint.

    Use this tool when the user asks about:
    - Candidate profiles
    - Resume data
    - Available candidates
    - Candidate skills
    - Experience levels
    - Candidate locations
    - Best candidates for a role
    - Candidates with specific skills
    - Candidates in a specific city
    - Matching resumes for jobs
    - Shortlisting candidates 

    Returns:
        JSON string containing public candidate profile records from the API.
        Do not call any tool named JSON.
        Do not use markdown.
   Do not call any tool named JSON.
   Do not use markdown.
    """
   
   
   url = "http://127.0.0.1:8000/api/v1/candidates/public/profiles"
   response = httpx.get(url)
   response.raise_for_status()

   return response.json()

@tool
def vector_search(query:str):
   """
      Perform semantic similarity search in the vector database.

      Use this tool when the user asks about:
      - Job recommendations
      - Related jobs
      - Backend developer jobs
      - Python jobs
      - Django jobs
      - FastAPI jobs
      - AI / ML jobs
      - Cloud jobs
      - Remote jobs
      - Jobs matching specific skills
      - Natural language job search
      - Similar opportunities
      - Search by meaning instead of exact keyword
      - Find relevant jobs from user query text
      Do not call any tool named JSON.
      Do not use markdown.

   """

   docs = vectorstore.similarity_search(query,k=5)
   results = []

   for doc in docs:
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })

   return results


agent = create_agent(
    model=llm,
    tools=[access_of_job_details,access_of_company_details,access_of_profile_details,vector_search],
    system_prompt=
    """
You are an intelligent AI assistant for a Job Portal Platform.

Your role is to help users with:
- Job search
- Company information
- Recruiter details
- Candidate profiles
- Resume matching
- Skill-based hiring
- Job recommendations
- Hiring insights
- Semantic search across stored data

You have Only and strictly access to 4 tools:

1. access_of_job_details()
Use this tool when the user asks about:
- jobs
- job list
- vacancies
- openings
- active jobs
- salary
- job location
- job type
- remote jobs
- latest jobs
- jobs by city
- jobs by experience
- jobs by technology

2. access_of_company_details()
Use this tool when the user asks about:
- companies
- recruiters
- company names
- company list
- hiring companies
- company location
- salary ranges
- job openings by company
- top companies
- companies in specific city

3. access_of_profile_details()
Use this tool when the user asks about:
- candidates
- profiles
- resumes
- skills
- experience
- available candidates
- candidate location
- top candidates
- shortlist candidates
- profiles for specific role
- candidates with specific skills

4. vector_search(query: str)
Use this tool when the user asks about:
- semantic job search
- backend developer jobs
- python jobs
- django jobs
- AI jobs
- cloud jobs
- matching jobs from text
- jobs related to skills
- recommendations based on meaning
- find similar jobs
- search inside vector database
- natural language job search

TOOL SELECTION RULES:

- For direct structured job data → use access_of_job_details()
- For recruiter/company data → use access_of_company_details()
- For candidate/resume data → use access_of_profile_details()
- For smart semantic search / related jobs → use vector_search(query)
- Use multiple tools if needed
- Choose the most relevant tool based on user intent

IMPORTANT RULES:

- Always use tools when data is required
- Never make up jobs, companies, or candidates
- Use only tool results
- If no data found, clearly say so
- Understand user intent, not just keywords
- Compare results when user asks best/top/recommended
- Rank logically based on relevance
- Summarize cleanly instead of dumping raw data
- Keep responses professional and useful
- Return human-readable answers

FINAL OUTPUT RULES:

Return ONLY raw JSON text.

Do NOT use markdown.
Do NOT wrap response in ```json.
Do NOT call any tool named 'json'.
Do NOT return a function call.
Do NOT return this format:
{"name": "json", "arguments": {...}}

Your final response must directly be:

{
  "answer": "short answer here",
  "data": [],
  "sources_used": [],
  "status": "success"
}

If no data found:

{
  "answer": "No matching data found.",
  "data": [],
  "sources_used": [],
  "status": "not_found"
}

when you are returing data always check 3 times that returned data should be in JSON only strictly 
"""

)

@router.post('/agent')
def ask_agent(request:agentRequest):
    try:
        response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": request.question
                }
            ]
        })

        final_answer = response["messages"][-1].content

        try:
            parsed_answer = json.loads(final_answer)
        except Exception:
            parsed_answer = {
                "answer": str(final_answer),
                "data": [],
                "sources_used": [],
                "status": "invalid_json_from_llm"
            }

        return {
            "question": request.question,
            "result": parsed_answer
        }

    except Exception as e:
        return {
            "question": request.question,
            "result": {
                "answer": "Agent failed while processing request.",
                "error": str(e),
                "data": [],
                "sources_used": [],
                "status": "error"
            }
        }