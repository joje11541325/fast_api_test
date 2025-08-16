from fastapi import FastAPI, Path

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


@app.get("/search_item/{item_id}")
def get_item(item_id: int = Path(description="The ID of the item you want to see")):
    return items[item_id]
