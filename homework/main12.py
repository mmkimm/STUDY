from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, date, time, timedelta
from uuid import UUID

app = FastAPI()

class Item(BaseModel):
    id: UUID
    timestamp: datetime
    date: date
    time: time
    duration: timedelta

@app.post("/items/")
async def create_item(item: Item):
    return item
