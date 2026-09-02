# Polar Science Portal — SIH 26063 MVP

A college-level MVP for the Ministry of Earth Sciences / NCPOR problem statement 26063: Integrated Polar Science Outreach, Knowledge Repository and Media Dissemination Portal.

## Features
- FastAPI REST backend
- PostgreSQL-ready database (SQLite by default for local demo)
- JWT authentication + admin/researcher/public roles
- Expedition, resource, publication, dataset and media management
- Search and filtering
- File upload
- Public knowledge repository
- AI outreach-content generation when `OPENAI_API_KEY` is configured; deterministic fallback demo content otherwise
- Simple polar expedition map using Leaflet/OpenStreetMap
- Seed demo data
- Docker Compose for local deployment

## Local run
### Backend
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:3000

Default demo admin:
- Email: `admin@polar.local`
- Password: `Admin@123`

## Environment
Backend `.env`:
```env
DATABASE_URL=sqlite:///./polar.db
SECRET_KEY=change-this-in-production
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
CORS_ORIGINS=http://localhost:3000
UPLOAD_DIR=uploads
```

Frontend `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For hosted deployment, use PostgreSQL and object storage rather than local uploads. The API keeps file handling behind a service boundary so storage can be replaced without redesigning the database.
