from pydantic import ValidationError
from sqlalchemy import create_engine
import uvicorn
from fastapi import FastAPI
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


# @app.post('/create_invoice_with_contents')
# def create_invoice_with_contents(invoice: Invoice):

#     print(invoice)

#     for content_data in invoice.contents:
        
#         db_content = ContentModel(**content_data.dict())
#         db_invoice.contents.append(db_content)

#     # Declaring our schema.
#     try:
#         # Create an instance of InvoiceModel
#         db_invoice = InvoiceModel(
#             code_invoice=invoice.code_invoice, 
#             invoice_id=invoice.invoice_id,
#             organization=invoice.organization, 
#             organization_code=invoice.organization_code,
#             document_number=invoice.document_number, 
#             document_date=invoice.document_date,
#             organization_received=invoice.organization_received, 
#             bank_account=invoice.bank_account,
#             location=invoice.location, 
#             date=invoice.date,
#             time_updated=datetime.utcnow()  # Set time_updated to the current time
#         )
#         # Create instances of ContentModel and associate them with the invoice
#         writer = index.writer()
#         for content_data in invoice.contents:
#             db_content = ContentModel(**content_data.dict())
#             db_invoice.contents.append(db_content)

#             writer.add_document(tantivy.Document(
#                 invoice_id=[str(content_data.invoice_id)],
#                 content=[str(content_data.content)],
#                 money=[str(content_data.money)],
#                 organization=[str(invoice.organization)],
#             ))
#             writer.commit()
#         index.reload()

#         db.session.add(db_invoice)
#         db.session.commit()
#         db.session.refresh(db_invoice)

#         return db_invoice

#     # except ValueError as ve:
#     #     # Handle the case where the conversion fails
#     #     raise HTTPException(status_code=422, detail=f"Invalid integer format: {ve}")

#     # except ValidationError as ve:
#     #     # Capture and return validation errors
#     #     raise HTTPException(status_code=422, detail=ve.errors())

#     except Exception as e:
#         # Log the error or handle it as needed
#         print(f"Error creating invoice: {e}")
    


# @app.get("/search-invoice")
# def search_invoice(text: str):
#     index.reload()
#     searcher = index.searcher()
#     query = index.parse_query(text, ["invoice_id", "content", "money"])
#     search_results = searcher.search(query, 100)
#     print(search_results)
#     result = []
#     for score, doc_address in search_results.hits:
#         # Retrieve the document
#         document = searcher.doc(doc_address)
#         content = document.get_first("content")
#         invoice_id = document.get_first("invoice_id")
#         money = document.get_first("money")
#         organization = document.get_first("organization")

#         template = {
#             'content': content,
#             'invoice_id': invoice_id,
#             'money': money,
#             'organization': organization
#         }

#         result.append(template)

        
#     return result

# To run locally
if __name__ == '__main__':
    module = "main:app"
    uvicorn.run(module, host='0.0.0.0', port=8002, reload=True)