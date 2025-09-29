from fastapi import FastAPI, Query
from typing import List, Optional

app = FastAPI()

@app.get("/items/")
async def read_items(q: Optional[List[str]] = Query(None)):
    query_items = {"q": q}
    return query_items
