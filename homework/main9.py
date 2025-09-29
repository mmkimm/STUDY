from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., title="Name of the item", max_length=50)
    description: str | None = Field(None, title="Description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item
