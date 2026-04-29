from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from model import Candidate_Profile, Recruiter_Profile, Job
from .table_to_document import candidate_to_document, job_to_document, company_to_document
from .chromadb_setup import vectorstore
from auth import get_db   
from sqlmodel import select
from sqlalchemy.orm import selectinload

router = APIRouter(
    prefix="/vectordb",
    tags=["sync"]
)
def rebuild_candidate_vector(candidate):
    doc_id = f"candidate_{candidate.id}"
    doc = candidate_to_document(candidate)

    vectorstore.delete(ids=[doc_id])
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )


def rebuild_job_vector(job):
    doc_id = f"job_{job.id}"
    doc = job_to_document(job)

    vectorstore.delete(ids=[doc_id])
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )


def rebuild_company_vector(recruiter):
    doc_id = f"company_{recruiter.id}"
    doc = company_to_document(recruiter)

    vectorstore.delete(ids=[doc_id])
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )


def sync_all_vectors(db):
    candidates = db.exec(
        select(Candidate_Profile).options(
            selectinload(Candidate_Profile.skills)
        )
    ).all()

    jobs = db.exec(
        select(Job).options(
            selectinload(Job.tags),
            selectinload(Job.recruiter)
        )
    ).all()

    companies = db.exec(
        select(Recruiter_Profile)
    ).all()

    for candidate in candidates:
        rebuild_candidate_vector(candidate)

    for job in jobs:
        rebuild_job_vector(job)

    for company in companies:
        rebuild_company_vector(company)

    return {
        "candidates_synced": len(candidates),
        "jobs_synced": len(jobs),
        "companies_synced": len(companies)
    }


@router.post("/sync")
def sync_vector_db(db: Session = Depends(get_db)):
    result = sync_all_vectors(db)

    return {
        "message": "Vector DB synced successfully using LangChain",
        "data": result
    }