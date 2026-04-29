from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi.routing import APIRouter
from sqlmodel import Session,select
from database import engine
from model import CreateUser,User,UserResponse
from fastapi import Depends,HTTPException
from datetime import datetime,timedelta 
from jose import jwt, JWTError
SECRET_KEY = '1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9olp0'
ALGORITHM = 'HS256'

oauth_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/',status_code=201,response_model=UserResponse)
def createUser(user:CreateUser,db:Session=Depends(get_db)):
    if user.role == 'admin':
        raise HTTPException(status_code=401,detail='unauthorized access')
    
    existing = db.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400,detail='Email is already used')
    
    existing = db.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400,detail='Username taken')
    
    db_user = User(username=user.username,email=user.email,role=user.role,password=pwd_context.hash(user.password))
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post('/token')
def generate_token(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = authenticate_user(form.username,form.password,db)
    
    token = make_token(user.username,user.id,user.role,timedelta(minutes=10)) # type: ignore
    return {
        'access_token':token,
        'token_type':'Bearer'
    }
    
    
def authenticate_user(username:str,password:str,db:Session):
    db_user = db.exec(select(User).where(User.username == username)).first()
    
    if not db_user:
        raise HTTPException(status_code=404,detail='User not found')
    
    if not pwd_context.verify(password,db_user.password):
        raise HTTPException(status_code=401,detail='wrong password')
    
    return db_user

def make_token(username:str,userid:int,role:str,expire:timedelta):
    to_encode = {'sub':username,'userid':userid,'role':role}
    to_encode.update({'exp':datetime.utcnow()+expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

@router.get('/me')
def get_current_user(token:str=Depends(oauth_scheme)):
    try:
        payload = jwt.decode(token=token,key=SECRET_KEY,algorithms=[ALGORITHM])
        return {'username':payload.get('sub') , 'userid':payload.get('userid'),'role':payload.get('role')}
    except JWTError:
        raise HTTPException(status_code=400,detail='error while getting user')
