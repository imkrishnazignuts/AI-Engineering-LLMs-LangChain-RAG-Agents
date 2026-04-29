from database import engine
from fastapi.routing import APIRouter
from model import CreateTag,Tag,Job,JobTagLink
from fastapi import Depends,HTTPException
from sqlmodel import Session,select
from auth import get_current_user

def get_db():
    db=Session(engine)
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix='/api/v1/tags',
    tags=['tag related']
)

@router.post('/')
def createTag(tag:CreateTag,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role']!='recruiter':
        raise HTTPException(status_code=403,detail='Only recruietr allowed')
    
    existing = db.exec(
        select(Tag).where(Tag.name == tag.name)
    ).first()

    if existing:
        raise HTTPException(400, "Tag already exists")
    
    db_tag = Tag(**tag.model_dump())
    
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get('/')
def get_all_tags(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user:
        return db.exec(select(Tag)).all()
    
    raise HTTPException(status_code=401,detail='Login to view')

@router.post("/jobs/{job_id}/tags/{tag_id}")
def add_tag_to_job(
    job_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    # Ensure recruiter role
    if user["role"] != "recruiter":
        raise HTTPException(403, "Only recruiter allowed")

    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(404, "Tag not found")

    # Prevent duplicate linking
    existing_link = db.exec(
        select(JobTagLink)
        .where(JobTagLink.job_id == job_id)
        .where(JobTagLink.tag_id == tag_id)
    ).first()

    if existing_link:
        raise HTTPException(400, "Tag already added to this job")

    link = JobTagLink(job_id=job_id, tag_id=tag_id)
    db.add(link)
    db.commit()

    return {"message": "Tag added successfully"}

@router.delete("/jobs/{job_id}/tags/{tag_id}")
def remove_tag_from_job(
    job_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if user["role"] != "recruiter":
        raise HTTPException(403, "Only recruiter allowed")

    link = db.exec(
        select(JobTagLink)
        .where(JobTagLink.job_id == job_id)
        .where(JobTagLink.tag_id == tag_id)
    ).first()

    if not link:
        raise HTTPException(404, "Tag not linked to this job")

    db.delete(link)
    db.commit()

    return {"message": "Tag removed successfully"}

@router.get('job/tags/{job_id}')
def get_job_tags(job_id:int,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401,detail='Only user allowed')
    
    job = db.exec(select(Job).where(Job.id == job_id)).first()
    if not job:
        raise HTTPException(status_code=401,detail='No job found')
    
    return job.tags               
    
    