from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment or default to local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://meraki:meraki_password@db:5432/meraki"
)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class DeviceDB(Base):
    """SQLAlchemy model for devices table"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer = Column(String, nullable=False, index=True)
    address = Column(Text, nullable=True)
    configupdated = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    firmware = Column(String, nullable=False, index=True)
    lanip = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    mac = Column(String, nullable=False, unique=True)
    model = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    networkid = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    producttype = Column(String, nullable=False, index=True)  # wireless, switch, appliance
    serial = Column(String, nullable=False, unique=True, index=True)
    tags = Column(Text, nullable=True)
    url = Column(String, nullable=False)


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
