"""Project models"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    """Project creation model"""
    title: str = Field(..., min_length=1, max_length=200)
    logline: str = Field(..., min_length=1, max_length=500)
    target_length_minutes: int = Field(..., ge=1, le=600)
    description: Optional[str] = None
    genre: Optional[str] = None
    status: str = Field(default="draft", pattern="^(draft|active|completed|archived)$")


class ProjectUpdate(BaseModel):
    """Project update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    logline: Optional[str] = Field(None, min_length=1, max_length=500)
    target_length_minutes: Optional[int] = Field(None, ge=1, le=600)
    description: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|completed|archived)$")


class ProjectResponse(BaseModel):
    """Project response model"""
    id: str
    title: str
    logline: str
    target_length_minutes: int
    description: Optional[str] = None
    genre: Optional[str] = None
    status: str
    userId: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

