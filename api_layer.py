"""This api is the layer that interacts with the user"""
from fastapi import FastAPI, Path, HTTPException, status
from email_agent import graph
from classes import Email

app = FastAPI()

emails = {}


@app.post("/draft-email")
def draft_email(email: Email = None):
    result = graph.invoke({"email": email})
    return {"category": result["category"], "actions_needed": result["actions_needed"], "reasoning": result["reasoning"]}


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
