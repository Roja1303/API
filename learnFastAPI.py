from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base  # Make sure this line is included
from sqlalchemy.orm import sessionmaker


# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # This should work now

# Define the database  models
class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default=None)
    price = Column(Float)
    tax = Column(Float, default=None)

# Create the database table
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Define a Pydantic model for the item
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": item}

@app.post("/items/")
def create_item(item: Item):
    db = SessionLocal()
    item_db = ItemDB(**item.dict())
    db.add(item_db)
    db.commit()
    db.refresh(item_db)
    db.close()
    return {"item_id": item_db.id, "item": item}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    db = SessionLocal()
    item_db = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item_db is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.dict().items():
        setattr(item_db, key, value)
    db.commit()
    db.close()
    return {"item_id": item_id, "item": item}

@app.get("/items/")
def read_all_items():
    db = SessionLocal()
    items = db.query(ItemDB).all()
    db.close()
    return items
