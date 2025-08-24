from pydantic import BaseModel
from typing import Optional, Literal
from langgraph.graph import MessagesState

class Email(BaseModel):
    """Base email class"""
    subject: Optional[str] = None
    body: Optional[str] = None
    email: Optional[str] = None
    
class classification_output(BaseModel):
    """Base classification output class"""
    category: Literal["Booking inquiries",
                            "Price or service inquiries", "General/other inquiries"] = None
    reasoning: Optional[str] = None

class AgentState(MessagesState):
    email: Email
    category: classification_output = None
    tool_calls: list[tool_calls] = []
    email_response: Optional[str] = None

class tool_calls(BaseModel):
    name: str
    args: dict
    result: str





