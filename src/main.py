from fastapi import FastAPI
from dotenv import load_dotenv
from . import db

load_dotenv()

async def lifespan(app: FastAPI):
    db.init_db()
    yield

app = FastAPI(
    title="Meraki Reporting",
    description="A custom backend showcasing device reporting with Meraki APIs",
    version="0.1.1",
    lifespan=lifespan,
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Meraki Reporting",
        "version": "0.1.1",
        "docs": "/docs"
    }