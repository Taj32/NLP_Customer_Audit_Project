# create_db.py
# This script creates the database tables defined in the models. (just used once, removed later)
# backend/create_db.py
from app.database import Base, engine
from app import models


Base.metadata.create_all(bind=engine)
print("done.")