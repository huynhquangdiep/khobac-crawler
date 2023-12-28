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
from datetime import datetime
import tantivy
from index import index
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
        writer = index.writer()
        writer.add_document(tantivy.Document(
            invoice_id=[str(db_invoice.invoice_id)],
            content=[str(db_invoice.content)],
            money=[str(db_invoice.money)],
            organization=[str(db_invoice.organization)],
            bill_code=[str(db_invoice.bill_code)],
            NDKT_code=[str(db_invoice.NDKT_code)],
            economic_code=[str(db_invoice.economic_code)],
            NSNN_code=[str(db_invoice.NSNN_code)],
            organization_received=[str(db_invoice.organization_received)],
            chapter_code=[str(db_invoice.chapter_code)],
        ))
        writer.commit()
        index.reload()

        db.session.add(db_invoice)
        db.session.commit()
        db.session.refresh(db_invoice)
            
        return db_invoice
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/invoices')
async def invoice():
    invoice = db.session.query(InvoiceModel).all()
    return invoice


@app.get("/fulltext-search-invoice")
def fulltext_search_invoice(text: str):
    index.reload()
    searcher = index.searcher()
    query = index.parse_query(text, ["invoice_id", "content", "money", "organization", "bill_code", "NDKT_code", "economic_code", "NSNN_code", "organization_received", "chapter_code"])
    search_results = searcher.search(query, 100)
    print(search_results)
    result = []
    for score, doc_address in search_results.hits:
        # Retrieve the document
        document = searcher.doc(doc_address)
        content = document.get_first("content")
        invoice_id = document.get_first("invoice_id")
        money = document.get_first("money")
        organization = document.get_first("organization")
        bill_code = document.get_first("bill_code")
        NDKT_code = document.get_first("NDKT_code")
        economic_code = document.get_first("economic_code")
        NSNN_code = document.get_first("NSNN_code")
        organization_received = document.get_first("organization_received")
        chapter_code = document.get_first("chapter_code")

        template = {
            'content': content,
            'invoice_id': invoice_id,
            'money': money,
            'organization': organization,
            'bill_code': bill_code,
            'NDKT_code': NDKT_code,
            'economic_code': economic_code,
            'NSNN_code': NSNN_code,
            'organization_received': organization_received,
            'chapter_code': chapter_code
        }

        result.append(template)


@app.get("/search-invoices")
def search_invoices(
    invoice_id: str = None,
    organization: str = None,
    code_invoice: str = None,
    content: str = None,
    money: str = None,
    bill_code: str = None,
    NDKT_code: str = None,
    economic_code: str = None,
    NSNN_code: str = None,
    organization_received:  str = None,
    chapter_code: str = None,
    signature_date_1_start: str = None,
    signature_date_1_end: str = None,
):
    query = db.session.query(InvoiceModel)

    # Add conditions based on provided parameters
    if invoice_id:
        query = query.filter(InvoiceModel.invoice_id == invoice_id)

    if organization:
        query = query.filter(func.unaccent(InvoiceModel.organization).ilike(func.unaccent(f"%{organization}%")))

    if code_invoice:
        query = query.filter(InvoiceModel.code_invoice == code_invoice)

    if content:
        query = query.filter(func.unaccent(InvoiceModel.content).ilike(func.unaccent(f"%{content}%")))

    if money:
        query = query.filter(InvoiceModel.money == money)

    if bill_code:
        query = query.filter(InvoiceModel.bill_code == bill_code)

    if NDKT_code:
        query = query.filter(InvoiceModel.NDKT_code == NDKT_code)

    if economic_code:
        query = query.filter(InvoiceModel.economic_code == economic_code)

    if NSNN_code:
        query = query.filter(InvoiceModel.NSNN_code == NSNN_code)

    if organization_received:
        query = query.filter(func.unaccent(InvoiceModel.organization_received).ilike(func.unaccent(f"%{organization_received}%")))

    if chapter_code:
        query = query.filter(InvoiceModel.chapter_code == chapter_code)

    if signature_date_1_start and signature_date_1_end:
        query = query.filter(
            and_(
                InvoiceModel.signature_date_1 >= signature_date_1_start,
                InvoiceModel.signature_date_1 <= signature_date_1_end
            )
        )

    # Execute the query and return the results
    result = query.all()
    return result

# To run locally
if __name__ == '__main__':
    module = "main:app"
    uvicorn.run(module, host='0.0.0.0', port=8002, reload=True)