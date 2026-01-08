from fastapi import FastAPI
from dotenv import load_dotenv
from . import db
from . import seed_data

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

@app.get("/seed")
async def root():
    # Seed with 10 customers, ~15 devices each
    seed_data.seed_database(num_customers=10, devices_per_customer=15)
