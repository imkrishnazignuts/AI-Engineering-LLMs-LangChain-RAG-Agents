from langchain_core.documents import Document


def candidate_to_document(candidate):
    skills = ", ".join([skill.name for skill in candidate.skills]) if candidate.skills else "No skills"

    return Document(
        page_content=f"""
Type: Candidate Profile
Candidate ID: {candidate.id}
User ID: {candidate.user_id}
Full Name: {candidate.full_name}
Phone: {candidate.phone}
Location: {candidate.location}
Experience Years: {candidate.experience_years}
Current Company: {candidate.current_company}
Resume URL: {candidate.resume_url}
Bio: {candidate.bio}
Skills: {skills}
        """,
        metadata={
            "type": "candidate",
            "sql_id": candidate.id,
            "user_id": candidate.user_id,
            "full_name": candidate.full_name,
            "location": candidate.location,
            "experience_years": candidate.experience_years,
            "current_company": candidate.current_company,
            "resume_url": candidate.resume_url,
            "skills": skills,
        }
    )


def job_to_document(job):
    tags = ", ".join([tag.name for tag in job.tags]) if job.tags else "No tags"

    company_name = None
    company_website = None
    company_description = None

    if job.recruiter:
        company_name = job.recruiter.company_name
        company_website = job.recruiter.company_website
        company_description = job.recruiter.company_description

    return Document(
        page_content=f"""
Type: Job
Job ID: {job.id}
Recruiter ID: {job.recruiter_id}
Title: {job.title}
Description: {job.description}
Location: {job.location}
Salary Min: {job.salary_min}
Salary Max: {job.salary_max}
Job Type: {job.job_type}
Experience Required: {job.experience_required}
Is Active: {job.is_active}
Created At: {job.created_at}
Company Name: {company_name}
Company Website: {company_website}
Company Description: {company_description}
Tags: {tags}
        """,
        metadata={
            "type": "job",
            "sql_id": job.id,
            "recruiter_id": job.recruiter_id,
            "title": job.title,
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "job_type": job.job_type,
            "experience_required": job.experience_required,
            "is_active": job.is_active,
            "created_at": str(job.created_at),
            "company_name": company_name,
            "company_website": company_website,
            "tags": tags,
        }
    )


def company_to_document(recruiter):
    return Document(
        page_content=f"""
Type: Company
Recruiter ID: {recruiter.id}
User ID: {recruiter.user_id}
Company Name: {recruiter.company_name}
Company Website: {recruiter.company_website}
Company Description: {recruiter.company_description}
        """,
        metadata={
            "type": "company",
            "sql_id": recruiter.id,
            "user_id": recruiter.user_id,
            "company_name": recruiter.company_name,
            "company_website": recruiter.company_website,
        }
    )