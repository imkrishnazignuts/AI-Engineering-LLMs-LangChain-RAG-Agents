# AI-Layer-enabled-Job-Portal

A FastAPI backend for a job portal with authentication, recruiter/candidate workflows, and an AI layer for semantic search, job recommendations, and job-description enhancement.

## Tech Stack

- FastAPI
- SQLModel + SQLite
- JWT authentication
- ChromaDB
- LangChain
- Hugging Face embeddings
- Groq-hosted LLM integration

## Project Structure

```text
.
├── main.py
├── auth.py
├── database.py
├── model.py
├── requirements.txt
├── Dockerfile
├── routes/
│   ├── candidate.py
│   ├── recruiter.py
│   ├── job.py
│   ├── tag.py
│   └── skill.py
├── ai_layer/
│   ├── ai_agent.py
│   ├── chromadb_setup.py
│   ├── improve_description.py
│   ├── job_recommendation.py
│   ├── rag_pipeline.py
│   ├── sync_sql_chromadb.py
│   └── table_to_document.py
└── chroma_db/
```

## What This Project Does

This API supports:

- user registration and login
- recruiter and candidate profile creation
- job posting and job applications
- skill and tag management
- semantic search over jobs, companies, and candidates
- resume-based job recommendation
- AI-powered job description rewriting
- agent-style querying over portal data

## Main Modules

### `main.py`

Creates the FastAPI app, enables CORS, registers pagination, and includes all route modules.

### `auth.py`

Handles:

- signup at `/auth/`
- token generation at `/auth/token`
- current-user decoding at `/auth/me`

It uses JWT tokens and bcrypt password hashing.

### `model.py`

Defines the main SQLModel entities:

- `User`
- `Candidate_Profile`
- `Recruiter_Profile`
- `Job`
- `Skill`
- `Tag`
- `JobApplication`

It also defines the link tables for candidate-skills and job-tags.

### `routes/`

Contains the core business APIs:

- `candidate.py` for candidate profiles and skill linking
- `recruiter.py` for recruiter profiles and application review
- `job.py` for CRUD, applications, and search
- `tag.py` for tag creation and linking
- `skill.py` for skill creation and listing

### `ai_layer/`

Contains the AI features:

- `chromadb_setup.py`
  - initializes Chroma with Hugging Face embeddings
- `table_to_document.py`
  - converts SQL records into LangChain documents
- `sync_sql_chromadb.py`
  - rebuilds vector data from SQL tables
- `rag_pipeline.py`
  - semantic question-answering over vectorized data
- `job_recommendation.py`
  - resume PDF to job recommendation flow
- `improve_description.py`
  - improves job descriptions in multiple styles
- `ai_agent.py`
  - agent endpoint with tools for jobs, companies, candidates, and vector search

## API Overview

### Auth

Base path: `/auth`

- `POST /auth/`
- `POST /auth/token`
- `GET /auth/me`

### Candidates

Base path: `/api/v1/candidates`

- create profile
- view/update own profile
- add/remove skills
- public candidate profile endpoints

### Recruiters

Base path: `/api/v1/recruiters`

- create profile
- view/update own profile
- list recruiters
- review and update applications

### Jobs

Base path: `/api/v1/jobs`

- create, update, delete jobs
- list and fetch jobs
- apply for jobs
- view candidate applications
- search by company, city, and tags

### Tags and Skills

- `/api/v1/tags`
- `/api/v1/skills`

These endpoints manage reusable tags and skills plus their links to jobs/candidates.

### AI Endpoints

- `POST /vectordb/sync`
- `POST /ai/ask`
- `POST /ai/recommend`
- `POST /ai/improve-description`
- `POST /ai/agent`

## Local Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Note: the current `requirements.txt` does not appear to include every AI dependency imported by the code. You will likely also need packages such as:

```bash
pip install langchain langchain-core langchain-chroma langchain-huggingface langchain-groq chromadb sentence-transformers pypdf python-dotenv httpx
```

### 3. Add environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

### 4. Run the app

```bash
uvicorn main:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Docker

Build:

```bash
docker build -t ai-job-portal .
```

Run:

```bash
docker run -p 8000:8000 --env GROQ_API_KEY=your_groq_api_key ai-job-portal
```

## Current Observations

- The app uses `major-project.db` as its SQLite database.
- SQL tables are created automatically on startup.
- CORS currently allows all origins.
- Vector data is persisted in `chroma_db/`.
- The AI agent endpoint expects the app to be reachable on `http://127.0.0.1:8000`.
- `auth.py` contains a hardcoded `SECRET_KEY`, which should be moved to environment variables.
- Public signup blocks `admin` creation, while the skill creation route expects an admin user.

## Suggested Improvements

- move secrets and config into `.env`
- add automated tests
- align `requirements.txt` with imported packages
- add request/response examples
- tighten CORS and auth rules
- use PostgreSQL for production

## License

No license file is currently present in this folder.
