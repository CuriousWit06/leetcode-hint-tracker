from fastapi import FastAPI
from priority import get_due_problems
from pydantic import BaseModel
from llm_client import get_hint
from sync import sync_db
from db import create_db

app = FastAPI()

@app.get("/problems/due")
def get_due():
    return get_due_problems()

class sub_query(BaseModel):
    title_slug: str
    level: int
    previous_hints: list[str]

@app.post("/hint")
def generate_hint(query: sub_query):
    return get_hint(query.title_slug, query.level, query.previous_hints)

@app.post("/sync")
def sync():
    sync_db()
    return {"status": "sync complete"}

@app.post("/initialise")
def create():
    create_db()
    sync_db()
    return {"status": "initialisation complete"}