# build a schema using pydantic
from pydantic import BaseModel
from typing import Optional
from typing import Union

class Content(BaseModel):
    invoice_id: Optional[str] = None
    bill_code: Optional[str] = None
    bill_date: Optional[str] = None
    content: Optional[str] = None
    money: Union[int, str] = None

    class Config:
        from_attributes  = True

class Invoice(BaseModel):
    code_invoice: Optional[str] = None 
    invoice_id: Optional[str] = None
    organization: Optional[str] = None
    organization_code: Optional[str] = None
    document_number: Optional[str] = None
    document_date: Optional[str] = None
    organization_received: Optional[str] = None
    bank_account: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None

    class Config:
        from_attributes  = True

class InvoiceContents(Invoice):
    contents: list[Content]

    class Config:
        from_attributes  = True
    