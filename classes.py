from pydantic import BaseModel
from typing import Optional


class Email(BaseModel):
    """Base email class"""
    subject: Optional[str] = None
    body: Optional[str] = None
    email: Optional[str] = None
