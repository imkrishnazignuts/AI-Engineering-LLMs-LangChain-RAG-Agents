from database import engine
from fastapi.routing import APIRouter
from model import CreateSkill,Skill,Candidate_Profile,CandidateSkill
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
    prefix='/api/v1/skills',
    tags=['skill related']
)

@router.post('/')
def create_skill(
    skill: CreateSkill,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if user["role"] != "admin":
        raise HTTPException(403, "Only admin can create skills")

    existing = db.exec(
        select(Skill).where(Skill.name == skill.name)
    ).first()

    if existing:
        raise HTTPException(400, "Skill already exists")

    db_skill = Skill(name=skill.name)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)

    return db_skill

@router.get('/')
def get_all_skills(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    if user:
        return db.exec(select(Skill)).all()
    
    raise HTTPException(status_code=401,detail='Login to view')

@router.get('/candidate/skills')
def get_candidate_skills(db:Session=Depends(get_db),user:dict=Depends(get_current_user)):
    
    if user['role'] != 'candidate':
        raise HTTPException(status_code=404,detail='only candidate allowed')
    
    candidate = db.exec(select(Candidate_Profile).where(Candidate_Profile.user_id == user['userid'])).first()
    skills = candidate.skills 
    
    return skills