from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base  = declarative_base()

class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True)
    content = Column(String, index=True)
    money = Column(Float)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    invoice_id = Column(String, ForeignKey('invoice.code_invoice'))

    Invoice = relationship('Invoice')

class Invoice(Base):
    __tablename__ = 'invoice'
    code_invoice  = Column(String, primary_key=True, index=True)
    number_of_invoice = Column(String)
    organization = Column(String)
    organization_code = Column(String)
    document_number = Column(String)
    document_date = Column(String)
    organization_received = Column(String)
    bank_account = Column(String)
    location = Column(String)
    date = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())