from typing import Optional
from database import engine
from fastapi.routing import APIRouter
from model import CreateJob,Job,Recruiter_Profile,Candidate_Profile,CreateJobApplication,JobApplication, Tag
from fastapi import Depends,HTTPException
from sqlmodel import Session, col,select
from auth import get_current_user
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import selectinload
from ai_layer.table_to_document import job_to_document
from ai_layer.chromadb_setup import vectorstore
def get_db():
    db=Session(engine)
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix='/api/v1/jobs',
    tags=['Job related']
)

@router.post('/')
def create_job(job:CreateJob,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only Recruiter allowed')
    
    recruiter=db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if not recruiter:
        raise HTTPException(status_code=403,detail='Recruiter not found')
    
    db_job = Job(recruiter_id=recruiter.id,**job.model_dump()) # type: ignore
    doc_id = f'job_{db_job.id}'
    doc = job_to_document(db_job)
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
    
        
    

    
@router.get('/{job_id}')
def get_job(job_id:int,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=403,detail='Please Login First')
    
    job=db.exec(select(Job).where(Job.id == job_id)).first()
    
    if not job:
        raise HTTPException(status_code=404,detail='job not found')
            
    return job
        

@router.put('/{job_id}')
def Update_job(job_id:int,job:CreateJob,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only recruiter allowed')
    
    recruiter=db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if not recruiter:
        raise HTTPException(status_code=404,detail='Recruiter Profile not found')
        
    db_job=db.exec(select(Job).where(Job.id == job_id)).first()
    
    if not db_job:
        raise HTTPException(status_code=404,detail='job not found')
    
    if db_job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=403,detail='This job is not belongs to you')
    
    for key,value in job.model_dump().items():
        setattr(db_job,key,value)
    
    vectorstore.delete(
        ids=[f'job_{db_job.id}']
    )
    doc_id = f'job_{db_job.id}'
    doc = job_to_document(db_job)

    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )

    db.commit()
    db.refresh(db_job)
    return db_job
    

    
@router.delete('/{job_id}',status_code=204)
def delete_job(job_id:int,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only recruiter allowed')
    
    recruiter=db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if not recruiter:
        raise HTTPException(status_code=404,detail='Recruiter Profile not found')
        
    db_job=db.exec(select(Job).where(Job.id == job_id)).first()
    
    if not db_job:
        raise HTTPException(status_code=404,detail='job not found')
    
    if db_job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=403,detail='This job is not belongs to you')
    
    vectorstore.delete(
        ids=[f'job_{db_job.id}']
    )
    db.delete(db_job)
    db.commit()
    return {'deleted successfully'}
    

@router.get("/", response_model=Page[Job])
def get_all_jobs(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401)

    query = select(Job).order_by(Job.created_at.desc()) # type: ignore

    return paginate(db, query)
        

@router.post('/{job_id}/apply',status_code=201)
def apply_for_job(job_id:int,jobapplication:CreateJobApplication,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'candidate':
        raise HTTPException(status_code=403,detail='Only candidate can apply')
    
    candidate = db.exec(select(Candidate_Profile).where(Candidate_Profile.user_id == user['userid'])).first()
    
    if not candidate:
        raise HTTPException(status_code=404,detail='No Profile found')
    
    existing_application = db.exec(
        select(JobApplication).where(
            JobApplication.candidate_id == candidate.id,
            JobApplication.job_id == job_id
        )
    ).first()

    if existing_application:
        raise HTTPException(status_code=400, detail="Already applied")

    db_job_application = JobApplication(
        candidate_id=candidate.id,
        job_id=job_id,
        **jobapplication.model_dump()
    )

    db.add(db_job_application)
    db.commit()
    db.refresh(db_job_application)

    return db_job_application

@router.get('/applications/me')
def get_my_job_applications(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):

    if user['role'] != 'candidate':
        raise HTTPException(status_code=403, detail='Only candidate can view their applications')

    candidate = db.exec(
        select(Candidate_Profile)
        .where(Candidate_Profile.user_id == user['userid'])
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail='No candidate found')

    results = db.exec(
        select(JobApplication, Job)
        .join(Job, Job.id == JobApplication.job_id) # type: ignore
        .where(JobApplication.candidate_id == candidate.id)
    ).all()

    response = []

    for application, job in results:
        response.append({
            "id": application.id,
            "status": application.status,
            "applied_at": application.applied_at,
            "cover_letter": application.cover_letter,
            "job": {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "location": job.location
            }
        })

    return response

@router.post('recruiter/jobs')
def get_recruiter_own_jobs(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=401,detail='Only recruiter allowed')
    
    recruiter = db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if not recruiter:
        raise HTTPException(status_code=404,detail='Recruiter not found')
    
    return recruiter.jobs

@router.get("/search/job")
def get_search_job(
    company_name: Optional[str] = None,
    city: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    # Base query: only active jobs
    statement = select(Job).where(col(Job.is_active) == True)

    # Filter by company name (join recruiter)
    if company_name:
        statement = (
            statement
            .join(Job.recruiter)
            .where(
                col(Recruiter_Profile.company_name)
                .ilike(f"%{company_name.strip()}%")
            )
        )

    if city:
        statement = statement.where(
            col(Job.location).ilike(f"%{city.strip()}%")
        )


    if tags:
        tags = tags.lower()
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            statement = (
                statement
                .join(Job.tags)
                .where(
                    col(Tag.name).in_(tag_list)
                )
            )


    statement = statement.distinct()

    # Eager load related data
    statement = statement.options(
        selectinload(Job.recruiter),
        selectinload(Job.tags),
    )

    jobs = db.exec(statement).all()

    return jobs