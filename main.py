from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ValidationError
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
from validators import is_valid_url, is_expired_date
import asyncio


class Link(BaseModel):
    url: str
    until: list[int]


class DB(BaseModel):
    response: dict[str, Link]


class Data(BaseModel):
    alias: str
    info: Link


with open("base.json", 'r') as file:
    database = DB(**json.load(file))

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Specify the directory where your HTML templates are located


def clean_db():
    global database
    db = database.model_dump()
    expired_list = []
    for alias in db["response"]:
        if not is_expired_date(db["response"][alias]["until"]):
            expired_list.append(alias)

    for alias in expired_list:
        db["response"].pop(alias)
    database = DB(**db)


async def schedule_periodic_task():
    while True:
        clean_db()  # Call your function
        await asyncio.sleep(86400)


@app.on_event("startup")
async def start_periodic_task():
    global database
    asyncio.create_task(schedule_periodic_task())


@app.on_event("shutdown")
async def save_to_db():
    with open("base.json", "w") as file:
        file.write(database.model_dump_json(indent=3))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{name}")
def hello(name: str):
    if name in database.response:
        return RedirectResponse(database.response[name].url)
    return "ERROR"


@app.post("/makenewlink")
def process(data: Data):
    if not data.alias:
        return {"status": "error", "message": "Alias can not be empty"}
    if data.alias in database.response:
        return {"status": "error", "message": "Alias exist"}
    if not is_valid_url(data.info.url):
        return {"status": "error", "message": "Invalid url"}
    if not is_expired_date(data.info.until):
        return {"status": "error", "message": "Invalid date"}

    # db = database.model_dump()
    #
    # db["response"][data.alias] = data.info.model_dump()
    # database = DB(**db)

    database.response[data.alias] = data.info

    with open("base.json", "w") as file:
        file.write(database.model_dump_json(indent=3))

    return {"status": "ok", "message": "Alias added successfully"}

