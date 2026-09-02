from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="public")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Expedition(Base):
    __tablename__ = "expeditions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    region: Mapped[str] = mapped_column(String(100), index=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text)
    resources: Mapped[list["Resource"]] = relationship(back_populates="expedition")

class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    resource_type: Mapped[str] = mapped_column(String(50), index=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    keywords: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="approved", index=True)
    expedition_id: Mapped[int | None] = mapped_column(ForeignKey("expeditions.id"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expedition: Mapped[Expedition | None] = relationship(back_populates="resources")

class Media(Base):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(30))
    caption: Mapped[str] = mapped_column(Text, default="")
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expedition_id: Mapped[int | None] = mapped_column(ForeignKey("expeditions.id"), nullable=True)

class OutreachContent(Base):
    __tablename__ = "outreach_content"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))
    platform: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
