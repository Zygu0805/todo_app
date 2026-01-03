from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(String(400))
    completed = Column(Boolean, default=False)
    created_at = Column(String, default=datetime.now)
    updated_at = Column(String, default=datetime.now, onupdate=datetime.now)

    

