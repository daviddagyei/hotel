from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import as_declarative

@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class BaseORMModel(Base):
    __abstract__ = True
    # ...existing code...
