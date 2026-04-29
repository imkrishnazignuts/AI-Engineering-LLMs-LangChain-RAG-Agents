from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime

# user stuff 
class CreateUser(SQLModel):
    username:str=Field(unique=True)
    password:str=Field(nullable=False)
    email:str=Field(index=True,unique=True)
    role:str=Field(nullable=False,index=True)
    
class User(CreateUser,table=True):
    __tablename__ :str= 'users'
    
    id:Optional[int] = Field(default=None,primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    is_active:bool=Field(default=True)
    candidate_profile:Optional['Candidate_Profile'] = Relationship(back_populates='user')
    recruiter_profile:Optional['Recruiter_Profile'] = Relationship(back_populates='user')

class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    
# candidate stuff 

class CreateCandidate_Profile(SQLModel):
    full_name: str
    phone: Optional[str]
    location: Optional[str] = Field(index=True)
    experience_years: Optional[int] = Field(index=True)
    current_company: Optional[str]
    resume_url: Optional[str]
    bio: Optional[str]
 
class CandidateSkill(SQLModel, table=True):
    __tablename__ :str = "candidate_skills"

    candidate_id: Optional[int] = Field(
        default=None, foreign_key="candidates.id", primary_key=True
    )
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skills.id", primary_key=True
    )
       
class Candidate_Profile(CreateCandidate_Profile,table=True):
    __tablename__ :str = 'candidates'
    
    id:Optional[int]=Field(primary_key=True,default=None)
    user_id : int = Field(foreign_key="users.id" ,index=True)
    
    user : User = Relationship(back_populates='candidate_profile')
    skills: List['Skill'] = Relationship(
        back_populates="candidates",
        link_model=CandidateSkill
    )
    application : List['JobApplication'] = Relationship(back_populates='candidate')

# recruiter stuff 

class CreateRecruiter_Profile(SQLModel):
    company_name: str = Field(index=True)
    company_website: Optional[str]
    company_description: Optional[str]

class Recruiter_Profile(CreateRecruiter_Profile,table=True):
    __tablename__ :str= 'recruiters'
    
    id:Optional[int]= Field(primary_key=True,default=None)
    user_id:int=Field(foreign_key='users.id',index=True)
    
    user:User = Relationship(back_populates='recruiter_profile')
    jobs:List['Job'] = Relationship(back_populates='recruiter')




class JobTagLink(SQLModel, table=True):
    __tablename__ :str = "job_tag_links"

    job_id: Optional[int] = Field(
        default=None,
        foreign_key="jobs.id",
        primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tags.id",
        primary_key=True
    )
    
# job stuff 
class CreateJob(SQLModel):
    title: str = Field(index=True)
    description: str
    location: str = Field(index=True)
    salary_min: Optional[int] = Field(index=True)
    salary_max: Optional[int] = Field(index=True)
    job_type: str = Field(index=True)  # full-time, part-time, remote
    experience_required: Optional[int] = Field(index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class Job(CreateJob,table=True):
    __tablename__ :str= 'jobs'
    id:Optional[int] = Field(primary_key=True,default=None)
    recruiter_id: int = Field(foreign_key="recruiters.id", index=True)

    recruiter :Recruiter_Profile =Relationship(back_populates='jobs')
    tags : List['Tag']= Relationship(back_populates="jobs",link_model=JobTagLink)
    applications: List["JobApplication"] = Relationship(back_populates="job",sa_relationship_kwargs={"cascade": "all, delete"})
 
# tag -> job stuff 
   
class CreateTag(SQLModel):
    name: str = Field(index=True, unique=True)
    
class Tag(CreateTag, table=True):
    __tablename__:str = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    jobs : List['Job']= Relationship(back_populates="tags",link_model=JobTagLink)
    


# skill related stuff 

class CreateSkill(SQLModel):
    name: str = Field(index=True, unique=True)


class Skill(CreateSkill, table=True):
    __tablename__ :str= "skills"

    id: Optional[int] = Field(default=None, primary_key=True)

    candidates: List["Candidate_Profile"] = Relationship(
        back_populates="skills",
        link_model=CandidateSkill
    )
# job application stuff 

class UpdateJobApplication(SQLModel):
    status: Optional[str] = Field(default="applied", index=True)  
    
class CreateJobApplication(UpdateJobApplication):

    cover_letter: Optional[str]
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    
class JobApplication(CreateJobApplication, table=True):
    __tablename__:str = "job_applications"
    job_id: int = Field(foreign_key="jobs.id", index=True)

    candidate_id: int = Field(foreign_key="candidates.id", index=True)
    id: Optional[int] = Field(default=None, primary_key=True)


    job: Job = Relationship(back_populates="applications")
    candidate: Candidate_Profile = Relationship(back_populates="application")
    
    
