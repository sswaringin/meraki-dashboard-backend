from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import db as database
from . import seed_data

load_dotenv()

app = FastAPI(
    title="Meraki Reporting",
    description="A custom backend showcasing device reporting with Meraki APIs",
    version="0.1.1",
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
    """
    Seed with 10 customers, ~15 devices each
    """
    seed_data.seed_database(num_customers=10, devices_per_customer=15)
    return {
        "message": "Successfully created some data."
    }

@app.get("/api/v1/organizations")
async def get_organizations(db: Session = Depends(database.get_db)):
    """
    Returns list of all organizations (customers)
    """
    # Get unique customer names from devices
    customers = db.query(database.DeviceDB.customer).distinct().all()
    
    organizations = []
    for idx, (customer,) in enumerate(customers, start=1):
        organizations.append({
            "id": f"org_{idx}",
            "name": customer
        })
    
    return organizations