"""
This module provides the API endpoint for the dashboard.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List, Optional
from backend.pulsecse.models import User
from backend.pulsecse.auth import get_current_active_user
from backend.pulsecse.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class DashboardData(BaseModel):
    """Dashboard data model."""
    user_count: int
    post_count: int
    comment_count: int

@router.get("/dashboard/")
async def read_dashboard_data(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Read dashboard data."""
    # Get user count
    user_count = db.query(User).count()
    
    # Get post count
    post_count = db.query(Post).count()
    
    # Get comment count
    comment_count = db.query(Comment).count()
    
    dashboard_data = DashboardData(user_count=user_count, post_count=post_count, comment_count=comment_count)
    
    return JSONResponse(content=jsonable_encoder(dashboard_data), media_type="application/json")

class Post(BaseModel):
    """Post data model."""
    id: int
    title: str
    content: str

class Comment(BaseModel):
    """Comment data model."""
    id: int
    post_id: int
    content: str