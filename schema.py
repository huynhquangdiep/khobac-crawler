# build a schema using pydantic
from pydantic import BaseModel
from typing import Optional
from typing import Union

class Invoice(BaseModel):
    id:Optional[str] = None
    invoice_id: Optional[str] = None
    code_invoice: Optional[str] = None 
    sub_invoice_id: Optional[str] = None
    organization: Optional[str] = None
    organization_code: Optional[str] = None
    bill_code: Optional[str] = None
    bill_date: Optional[str] = None
    NDKT_code: Optional[str] = None
    chapter_code: Optional[str] = None
    economic_code: Optional[str] = None
    NSNN_code: Optional[str] = None
    content: Optional[str] = None
    money: Union[int, str] = None
    organization_received: Optional[str] = None
    bank_account: Optional[str] = None
    location: Optional[str] = None
    signature_date_1: Optional[str] = None
    signature_date_2: Optional[str] = None

    class Config:
        from_attributes  = True

    