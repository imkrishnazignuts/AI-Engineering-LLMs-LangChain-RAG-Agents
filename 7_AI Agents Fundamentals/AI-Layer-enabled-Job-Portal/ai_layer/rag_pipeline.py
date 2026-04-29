from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
from fastapi.routing import APIRouter 
from fastapi import Query
from .chromadb_setup import vectorstore

router = APIRouter(
    prefix='/ai',
    tags=['ai related']
)

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_template("""
You are an AI assistant for a job portal.

Answer the user's question using ONLY the provided context.

Your job is to understand the user's intent, search inside the context, filter relevant information, compare items if needed, rank items if needed, and summarize the answer clearly.
                                          
TRY TO FOCUS ON MEANING NOT THE EXACT MATCH

Context:
{context}

User Question:
{question}

Instructions:
- Use only information available in the context.
- Do not invent missing details.
- If the question asks for "top", rank the most relevant items first.
- If the question asks for a time period like "last 30 days", use created_at/date fields from context.
- If the question asks for summary, summarize clearly.
- If the question asks for bullet points, return bullet points inside the answer string.
- If exact filtering is not possible from context, mention that clearly.
- Keep the response useful and direct.

Return ONLY valid JSON.
Do not write markdown outside JSON.
Do not wrap JSON in ```json.

Format:

{{
  "answer": "final answer here",
  "count": 0,
  "data": []
}}

If no relevant data is found:

{{
  "answer": "I don't have enough information in the database.",
  "count": 0,
  "data": []
}}
""")

@router.post('/ask')
def ask_ai(query:str=Query(...)):
    docs = vectorstore.similarity_search(query,k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    chain = prompt | llm | JsonOutputParser()

    answer = chain.invoke({
        "context":context,
        "question":query
    })

    return {
        "query": query,
        "answer": answer,
        "sources": [
            doc.metadata for doc in docs
        ]
    }

