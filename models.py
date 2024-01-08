from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Invoice table model
class InvoiceModel(Base):
    __tablename__ = "invoice"
    invoice_id = Column(String)
    code_invoice = Column(String)
    sub_invoice_id = Column(String)
    temp_payment_07 = Column(String)
    organization = Column(String)
    organization_code = Column(String)
    bill_code = Column(String)  # Fixed the colon to equal sign here
    bill_date = Column(String)  # Fixed the colon to equal sign here
    NDKT_code = Column(String)
    chapter_code = Column(String)
    economic_code = Column(String)
    NSNN_code = Column(String)
    content = Column(String)
    money = Column(String)
    organization_received = Column(String)
    bank_account = Column(String)
    location = Column(String)
    signature_date_1 = Column(String)
    signature_date_2 = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    id = Column(String, primary_key=True, index=True)
