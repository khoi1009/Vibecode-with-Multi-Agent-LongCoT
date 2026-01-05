from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from sqlalchemy import create_engine


app = FastAPI(title="#_Mission API")


# Serve the Zero-Dependency Frontend
app.mount("/assets", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/api/status")
def read_status():
    return {"system": "#_Mission", "status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
