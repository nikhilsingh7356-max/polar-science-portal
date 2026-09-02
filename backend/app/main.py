from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .models import User, Expedition, Resource, Media, OutreachContent
from .schemas import *
from .auth import hash_password, verify_password, create_token, current_user, require_roles
from .services import save_upload, generate_outreach
from .seed import seed_database

Base.metadata.create_all(engine)
Path(settings.upload_dir).mkdir(exist_ok=True)
if settings.seed_demo:
    seed_database()
app = FastAPI(title="Polar Science Portal API", version="1.0.0", description="SIH 2026 PS 26063 — Polar Science Knowledge & Outreach Portal")

@app.get("/")
def root():
    return {"name":"Polar Science Portal API", "docs":"/docs", "health":"/api/health"}
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/api/health")
def health(): return {"status":"ok", "service":"polar-science-portal"}

@app.post("/api/auth/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())): raise HTTPException(400, "Email already registered")
    u=User(name=data.name,email=data.email.lower(),password_hash=hash_password(data.password),role="public")
    db.add(u); db.commit(); db.refresh(u)
    return {"user": UserOut.model_validate(u), "access_token": create_token(u)}

@app.post("/api/auth/login")
def login(data: Login, db: Session = Depends(get_db)):
    u=db.scalar(select(User).where(User.email == data.email.lower()))
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Invalid email or password")
    return {"user": UserOut.model_validate(u), "access_token": create_token(u)}

@app.get("/api/auth/me", response_model=UserOut)
def me(user=Depends(current_user)): return user

@app.get("/api/expeditions", response_model=list[ExpeditionOut])
def expeditions(db: Session=Depends(get_db), q: str|None=None, year: int|None=None, region: str|None=None):
    stmt=select(Expedition).order_by(Expedition.year.desc())
    if q: stmt=stmt.where(Expedition.name.ilike(f"%{q}%"))
    if year: stmt=stmt.where(Expedition.year==year)
    if region: stmt=stmt.where(Expedition.region.ilike(f"%{region}%"))
    return db.scalars(stmt).all()

@app.post("/api/expeditions", response_model=ExpeditionOut)
def create_expedition(data: ExpeditionCreate, db: Session=Depends(get_db), user=Depends(require_roles("admin","researcher"))):
    x=Expedition(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@app.get("/api/resources", response_model=list[ResourceOut])
def resources(db: Session=Depends(get_db), q: str|None=None, resource_type: str|None=None, year: int|None=None, expedition_id: int|None=None, limit: int=50):
    stmt=select(Resource).where(Resource.status=="approved").order_by(Resource.created_at.desc()).limit(min(limit,100))
    if q:
        like=f"%{q}%"; stmt=stmt.where(or_(Resource.title.ilike(like),Resource.description.ilike(like),Resource.keywords.ilike(like),Resource.author.ilike(like)))
    if resource_type: stmt=stmt.where(Resource.resource_type==resource_type)
    if year: stmt=stmt.where(Resource.year==year)
    if expedition_id: stmt=stmt.where(Resource.expedition_id==expedition_id)
    return db.scalars(stmt).all()

@app.get("/api/resources/{rid}", response_model=ResourceOut)
def resource(rid:int, db:Session=Depends(get_db)):
    x=db.get(Resource,rid)
    if not x: raise HTTPException(404,"Resource not found")
    return x

@app.post("/api/resources", response_model=ResourceOut)
def create_resource(data: ResourceCreate, db:Session=Depends(get_db), user=Depends(require_roles("admin","researcher"))):
    status=data.status if user.role=="admin" else "pending"
    x=Resource(**data.model_dump(exclude={"status"}), status=status, created_by=user.id)
    db.add(x); db.commit(); db.refresh(x); return x

@app.post("/api/resources/{rid}/file")
def upload_resource_file(rid:int, file:UploadFile=File(...), db:Session=Depends(get_db), user=Depends(require_roles("admin","researcher"))):
    x=db.get(Resource,rid)
    if not x: raise HTTPException(404,"Resource not found")
    x.file_url=save_upload(file,file.filename); db.commit(); return {"file_url":x.file_url}

@app.get("/api/admin/pending", response_model=list[ResourceOut])
def pending(db:Session=Depends(get_db), user=Depends(require_roles("admin"))):
    return db.scalars(select(Resource).where(Resource.status=="pending").order_by(Resource.created_at.desc())).all()

@app.post("/api/admin/resources/{rid}/approve", response_model=ResourceOut)
def approve(rid:int, db:Session=Depends(get_db), user=Depends(require_roles("admin"))):
    x=db.get(Resource,rid)
    if not x: raise HTTPException(404,"Resource not found")
    x.status="approved"; db.commit(); db.refresh(x); return x

@app.get("/api/media")
def media(db:Session=Depends(get_db)):
    return db.scalars(select(Media).order_by(Media.id.desc())).all()

@app.post("/api/media")
def create_media(title:str, media_type:str, caption:str="", expedition_id:int|None=None, file:UploadFile|None=File(None), db:Session=Depends(get_db), user=Depends(require_roles("admin","researcher"))):
    url=save_upload(file,file.filename) if file else None
    x=Media(title=title,media_type=media_type,caption=caption,expedition_id=expedition_id,file_url=url); db.add(x); db.commit(); db.refresh(x); return x

@app.post("/api/outreach/generate")
def outreach(data:OutreachRequest, db:Session=Depends(get_db), user=Depends(require_roles("admin","researcher"))):
    r=db.get(Resource,data.resource_id)
    if not r: raise HTTPException(404,"Resource not found")
    content=generate_outreach(r.title,r.description,data.platform)
    x=OutreachContent(resource_id=r.id,platform=data.platform,title=r.title,content=content); db.add(x); db.commit(); db.refresh(x)
    return {"id":x.id,"title":x.title,"platform":x.platform,"content":x.content}

@app.get("/api/outreach/{rid}")
def outreach_history(rid:int, db:Session=Depends(get_db)):
    return db.scalars(select(OutreachContent).where(OutreachContent.resource_id==rid).order_by(OutreachContent.id.desc())).all()
