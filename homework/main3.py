from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_item(q: str = None):
    return {"q": q}
