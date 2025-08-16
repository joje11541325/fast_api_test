"""This api"""
from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

emails = {}


class Email(BaseModel):
    """give more"""
    subject: Optional[str] = None
    body: Optional[str] = None
    email: Optional[str] = None


@app.post("/draft-email/{email_id}")
def draft_email(email_id: int, email: Email = None):
    emails[email_id] = email
    return emails[email_id]


@app.get("/find-email/{email_id}")
def find_email(email_id: int = Path(description="Here du pass the id of the email you want to find")):
    if email_id in emails:
        return emails[email_id].subject
    return "No email with that id!"


@app.put("/edit-email/{email_id}")
def edit_email(email_id: int, email: Email):
    if email_id in emails:
        emails[email_id] = email
        return emails[email_id]

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="No item with that id")
