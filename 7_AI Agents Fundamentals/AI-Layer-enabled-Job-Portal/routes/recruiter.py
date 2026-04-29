from database import engine
from fastapi.routing import APIRouter
from model import CreateRecruiter_Profile,Recruiter_Profile,JobApplication,UpdateJobApplication,Job,Candidate_Profile
from fastapi import Depends,HTTPException
from sqlmodel import Session,select
from auth import get_current_user
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from ai_layer.table_to_document import company_to_document
from ai_layer.chromadb_setup import vectorstore

def get_db():
    db=Session(engine)
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix='/api/v1/recruiters',
    tags=['recruiter related']
)

@router.post('/profile')
def create_recruiter(recruiter:CreateRecruiter_Profile,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only Recruiter allowed')
    
    existing = db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if existing:
        raise HTTPException(status_code=400,detail='Profile already exists')
    
    db_recruiter = Recruiter_Profile(user_id=user['userid'],**recruiter.model_dump())
    doc_id = f'company_{db_recruiter.id}'
    doc = company_to_document(db_recruiter)
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )
    
    db.add(db_recruiter)
    db.commit()
    db.refresh(db_recruiter)
    return db_recruiter
    
@router.get('/me')
def get_own_profile_recruiter(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only recruiter allowed')
    
    profile=  db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    if not profile:
        raise HTTPException(status_code=400,detail='No profile found')
    return profile
    
@router.get('/',response_model=Page[Recruiter_Profile])   
def get_all_recruiters(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=403,detail='Login to view')
    
    query = select(Recruiter_Profile)
    return paginate(db,query)

             

@router.put('/me')
def Update_profile_recruiter(recruiter:CreateRecruiter_Profile,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only recruiter allowed')
    
    db_recruiter = db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if not db_recruiter:
        raise HTTPException(status_code=400,detail='No recruiter profile found')
    
    for key, value in recruiter.model_dump().items():
        setattr(db_recruiter, key, value)
        
    db.commit()
    db.refresh(db_recruiter)

    return db_recruiter
        
@router.get('/applications')
def get_applications(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):

    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403, detail='Only recruiter allowed')

    recruiter = db.exec(
        select(Recruiter_Profile)
        .where(Recruiter_Profile.user_id == user['userid'])
    ).first()

    if not recruiter:
        raise HTTPException(status_code=404, detail='No recruiter found')
    
    result = db.exec(select(JobApplication,Candidate_Profile).join(Job,JobApplication.job_id == Job.id).where(JobApplication.candidate_id == Candidate_Profile.id)).all() # type: ignore
    
    applications = []
    print(result)
    for jobapplication,candidate in result:
        applications.append({
            'id':jobapplication.id,
           'status':jobapplication.status,
           'applied_at':jobapplication.applied_at,
           'cover_letter':jobapplication.cover_letter,
           'candidate':{
               'candidate_id':candidate.id,
               'phone':candidate.phone,
               'location':candidate.location,
               'current_company':candidate.current_company,
               'full_name':candidate.full_name,
               'experience':candidate.experience_years,
               'resume-url':candidate.resume_url
           }
        })
    
    return applications

@router.put('/application/{id}')
def update_application(id:int,jobapplication:UpdateJobApplication,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    
    if user['role'] != 'recruiter':
        raise HTTPException(status_code=403,detail='Only recruiter allowed')
    
    recruiter = db.exec(select(Recruiter_Profile).where(Recruiter_Profile.user_id == user['userid'])).first()
    
    if not recruiter:
        raise HTTPException(status_code=404,detail='No recruiter found')
        
    db_application = db.exec(select(JobApplication).where(JobApplication.id == id)).first()
    if not db_application:
        raise HTTPException(status_code=404,detail='No Application found')
    
    for key,value in jobapplication.model_dump().items():
        setattr(db_application,key,value)
    
    db.commit()
    db.refresh(db_application)
    return db_application
    
    
    