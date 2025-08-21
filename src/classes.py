from openai.types.responses import response_reasoning_item
from pydantic import BaseModel
from typing import Optional


class classification_output(BaseModel):
    """Base classification output class"""
    classification: Literal["Booking inquiries",
                            "price or serviceinquiries", "General/other inquiries"] = None
    reasoning: Optional[str] = None


class Email(BaseModel):
    """Base email class"""
    subject: Optional[str] = None
    body: Optional[str] = None
    email: Optional[str] = None
