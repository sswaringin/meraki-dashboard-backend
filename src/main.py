import os
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Meraki Reporting",
    description="A custom backend showcasing device reporting with Meraki APIs",
    version="0.1.1"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Meraki Reporting",
        "version": "0.1.1",
        "docs": "/docs"
    }