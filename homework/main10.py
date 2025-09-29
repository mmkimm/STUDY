from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union

app = FastAPI()

class Image(BaseModel):
    url: str
    name: str

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: List[str] = []
    images: Union[List[Image], None] = None

@app.post("/items/")
async def create_item(item: Item):
    return item
