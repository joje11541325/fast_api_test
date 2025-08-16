"""This api"""
from fastapi import FastAPI, Path
from pydantic import BaseModel

app = FastAPI()

items = {1: {"name": "eggs", "price": 4.44},
         2: {"name": "chicken", "price": 100.44}}


@app.get("/")
def firstpage():
    return {"Where you are": "Second page man."}


@app.get("/om oss")
def aboutus():
    return {"Info": """Vi är ett företag med kärlek för det äkta
    Vi tar inget för givet
    Ge mig lite"""}


items = {1: {"name": "eggs", "price": 4.44},
         2: {"name": "chicken", "price": 100.44}}


@app.get("/search_item")
def get_item(name: str = None):
    for item in items.values():
        if item["name"] == name:
            return item
    return "no items found"


class Email(BaseModel):
    subject: str
    body: str
    email: str


@app.post("/draft-email")
def draft_email(email: Email = None):
    return {"data": "you uploaded an email"}
