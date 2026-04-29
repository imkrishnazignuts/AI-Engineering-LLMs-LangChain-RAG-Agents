from database import engine
from fastapi.routing import APIRouter
from model import CreateCandidate_Profile,Candidate_Profile,Skill
from fastapi import Depends,HTTPException
from sqlmodel import Session,select
from auth import get_current_user
from ai_layer.table_to_document import candidate_to_document
from ai_layer.chromadb_setup import vectorstore
from sqlalchemy.orm import selectinload
def get_db():
    db=Session(engine)
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix='/api/v1/candidates',
    tags=['candidate related']
)

@router.post('/profile')
def create_candidate(candidate:CreateCandidate_Profile,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'candidate':
        raise HTTPException(status_code=403,detail='Only candidate allowed')
    
    existing = db.exec(select(Candidate_Profile).where(Candidate_Profile.user_id == user['userid'])).first()
    
    if existing:
        raise HTTPException(status_code=400,detail='Profile already exists')
    
    db_candidate = Candidate_Profile(user_id=user['userid'],**candidate.model_dump())
    doc_id = f"candidate_{db_candidate.id}"
    doc = candidate_to_document(db_candidate)
    vectorstore.delete(ids=[doc_id])
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )
    print('NEW USER ADDED VECTOR DATABASE')
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate 
    
@router.get('/me')
def get_own_profile_candidate(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'candidate':
        raise HTTPException(status_code=403,detail='Only candidate allowed')
    
    profile= db.exec(select(Candidate_Profile).where(Candidate_Profile.user_id == user['userid'])).first()
    if not profile:
        raise HTTPException(status_code=400,detail='No profile found')
    return profile

@router.put('/me')
def Update_profile_candidate(candidate:CreateCandidate_Profile,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user['role'] != 'candidate':
        raise HTTPException(status_code=403,detail='Only candidate allowed')
    
    db_candidate = db.exec(select(Candidate_Profile).where(Candidate_Profile.user_id == user['userid'])).first()
    
    if not db_candidate:
        raise HTTPException(status_code=400,detail='No candidate profile found')
    
    for key, value in candidate.model_dump().items():
        setattr(db_candidate, key, value)

    vectorstore.delete(
        ids=[f'candidate_{db_candidate.id}']
    )

    doc_id = f'candidate_{db_candidate.id}'
    doc = candidate_to_document(db_candidate)
    vectorstore.add_documents(
        documents=[doc],
        ids=[doc_id]
    )

    db.commit()
    db.refresh(db_candidate)

    return db_candidate
        


    

@router.post("/candidates/{candidate_id}/skills/{skill_id}")
def add_skill_to_candidate(
    candidate_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    candidate = db.get(Candidate_Profile, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    # Security: ensure ownership
    if candidate.user_id != user["userid"]:
        raise HTTPException(403, "Not allowed")

    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(404, "Skill not found")

    # Prevent duplicate
    if skill in candidate.skills:
        raise HTTPException(400, "Skill already added")

    candidate.skills.append(skill)
    db.add(candidate)
    db.commit()

    return {"message": "Skill added successfully"}

@router.delete("/candidates/{candidate_id}/skills/{skill_id}")
def remove_skill_from_candidate(
    candidate_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    candidate = db.get(Candidate_Profile, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    if candidate.user_id != user["userid"]:
        raise HTTPException(403, "Not allowed")

    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(404, "Skill not found")

    if skill not in candidate.skills:
        raise HTTPException(400, "Skill not linked")

    candidate.skills.remove(skill)
    db.commit()

    return {"message": "Skill removed successfully"}

@router.get('/public/profile/{id}')
def public_profile_of_candidate(id:int,db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401,detail='Login First')
    candidate = db.exec(select(Candidate_Profile).where(Candidate_Profile.id == id)).first()
    if not candidate:
        raise HTTPException(status_code=404,detail='Candidate not found')
    skills = candidate.skills
    
    return {'candidate details':candidate,'candidate skills ':skills} 
        
@router.get('/public/profiles')
def public_profile_of_candidates(db: Session = Depends(get_db)):

    candidates = db.exec(
        select(Candidate_Profile).options(
            selectinload(Candidate_Profile.skills)
        )
    ).all()

    if not candidates:
        raise HTTPException(status_code=404, detail='Candidates not found')

    return {
        "candidate_details": [
            {
                "id": candidate.id,
                "full_name": candidate.full_name,
                "phone": candidate.phone,
                "location": candidate.location, 
                "experience_years": candidate.experience_years,
                "current_company": candidate.current_company,
                "bio": candidate.bio,
                "skills": [
                    {
                        "id": skill.id,
                        "name": skill.name
                    }
                    for skill in candidate.skills
                ]
            }
            for candidate in candidates
        ]
    }