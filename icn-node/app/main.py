
from fastapi import FastAPI

app = FastAPI(title="ICN Node", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "node": "icn-mvp"}
