# build a schema using pydantic
from pydantic import BaseModel

class Content(BaseModel):
    content: str
    money: float
    invoice_id: str

    class Config:
        orm_mode = True

class Invoice(BaseModel):
    code_invoice: str
    number_of_invoice: int
    organization: str
    organization_code: str
    document_number: str
    document_date: str
    organization_received: str
    bank_account: str
    location: str
    date: str

    class Config:
        orm_mode = True
    