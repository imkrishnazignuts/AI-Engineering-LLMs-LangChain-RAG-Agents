from fastapi import FastAPI,Depends,HTTPException
from sqlmodel import SQLModel,Session,select
from database import engine
from routes import candidate,recruiter,job,tag,skill
import auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from ai_layer.sync_sql_chromadb import router as sync_router
from ai_layer.rag_pipeline import router as rag_router
from ai_layer.job_recommendation import router as job_recommendation_router
from ai_layer.improve_description import router as improve_desc_router
from ai_layer.ai_agent import router as agent_router
app = FastAPI()
add_pagination(app)

app.include_router(job_recommendation_router)
app.include_router(improve_desc_router)
app.include_router(auth.router)
app.include_router(candidate.router)
app.include_router(sync_router)
app.include_router(recruiter.router)
app.include_router(job.router)
app.include_router(tag.router)
app.include_router(skill.router)
app.include_router(rag_router)
app.include_router(agent_router)
@app.on_event('startup')
def startup():
    SQLModel.metadata.create_all(engine)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)