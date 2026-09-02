from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: str

class ExpeditionCreate(BaseModel):
    name: str
    year: int
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: str

class ExpeditionOut(ExpeditionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ResourceCreate(BaseModel):
    title: str
    description: str
    resource_type: str
    year: Optional[int] = None
    author: Optional[str] = None
    keywords: Optional[str] = None
    expedition_id: Optional[int] = None
    status: str = "approved"

class ResourceOut(ResourceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file_url: Optional[str] = None

class OutreachRequest(BaseModel):
    resource_id: int
    platform: str = "website"
