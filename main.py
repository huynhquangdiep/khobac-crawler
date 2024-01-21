# from collections import defaultdict
from collections import defaultdict
from operator import and_
from pydantic import ValidationError
from sqlalchemy import create_engine, func
import uvicorn
from fastapi import FastAPI, Query
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy.orm import sessionmaker
from schema import Invoice
from models import InvoiceModel
import os
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv('.env')
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
async def root():
    return {"message": " hello"}

@app.post('/invoices', response_model=Invoice)
async def create_invoice(invoice: Invoice):
    try:
        db_invoice = InvoiceModel(**invoice.dict())

        db.session.add(db_invoice)
        db.session.commit()
        db.session.refresh(db_invoice)
            
        return db_invoice
    except Exception as e:
        # # Log the error or handle it as needed
        # print(f"Error creating invoice: {e}")
        # raise HTTPException(status_code=500, detail="Internal Server Error")
        return False

@app.get('/invoices')
async def invoice():
    invoice = db.session.query(InvoiceModel).all()
    return invoice

@app.get('/get-invoice-detail')
async def get_invoice_detail(sub_invoice_id: str):
    data_response = []
    invoices = db.session.query(InvoiceModel).filter(InvoiceModel.sub_invoice_id == sub_invoice_id).all()

    if not invoices:
        return data_response

    result = defaultdict(dict)
    for invoice in invoices:
        invoice_id = invoice.invoice_id
        # Remove unnecessary fields for the summary
        summary_fields = ["temp_payment_07", "bank_account", "location", "signature_date_1", "signature_date_2",
            "invoice_id", "time_created", "organization", "time_updated", "code_invoice", "organization_code", 
            "sub_invoice_id", "organization_received", "chief_accountant", "chief"]
        summary_data = {field: getattr(invoice, field, None) for field in summary_fields}
        
        # Create or update the dictionary for the current invoice_id
        if invoice_id not in result:
            result[invoice_id] = summary_data
            result[invoice_id]["details"] = []
        
        # Append details to the "details" list
        result[invoice_id]["details"].append({
            "id": invoice.id,
            "NDKT_code": invoice.NDKT_code,
            "chapter_code": invoice.chapter_code,
            "economic_code": invoice.economic_code,
            "NSNN_code": invoice.NSNN_code,
            "content": invoice.content,
            "money": invoice.money,
            "bill_code": invoice.bill_code,
            "bill_date": invoice.bill_date,
            # Add other fields as needed
        })
    
    data_response = list(result.values())

    return data_response[0]


@app.get("/search-invoices")
def search_invoices(
    invoice_id: str = None,
    organization: str = None,
    content: str = None,
    money: str = None,
    organization_received:  str = None,
    NDKT_code_start: str = None,
    NDKT_code_stop: str = None,
):
    query = db.session.query(InvoiceModel)

    # Add conditions based on provided parameters
    if invoice_id:
        query = query.filter(func.unaccent(InvoiceModel.invoice_id).ilike(func.unaccent(f"%{invoice_id}%")))

    if organization:
        query = query.filter(func.unaccent(InvoiceModel.organization).ilike(func.unaccent(f"%{organization}%")))

    if content:
        query = query.filter(func.unaccent(InvoiceModel.content).ilike(func.unaccent(f"%{content}%")))

    if money:
        query = query.filter(InvoiceModel.money == money)

    if organization_received:
        query = query.filter(func.unaccent(InvoiceModel.organization_received).ilike(func.unaccent(f"%{organization_received}%")))

    if NDKT_code_start and NDKT_code_stop:
        query = query.filter(
            and_(
                InvoiceModel.NDKT_code >= NDKT_code_start,
                InvoiceModel.NDKT_code <= NDKT_code_stop
            )
        )

    # Execute the query and return the results
    result = query.all()
    return result

# To run locally
if __name__ == '__main__':
    module = "main:app"
    uvicorn.run(module, host='0.0.0.0', port=8000, reload=True)