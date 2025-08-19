"""This api"""
from fastapi import FastAPI, Path, Query, HTTPException, status
from typing import Optional
from email_agent import graph
from classes import Email

app = FastAPI()

emails = {}


@app.post("/draft-email/{email_id}")
def draft_email(email_id: int, email: Email = None):
    emails[email_id] = email
    result = graph.invoke({"email": email})
    return result


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
