import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import Content as SchemaContent
from schema import Invoice as SchemaInvoice

from schema import Content
from schema import Invoice

from models import Content as ModelContent
from models import Invoice as ModelInvoice

import os
from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.get("/")
async def root():
    return {"message": "hello world"}

@app.post('/content/', response_model=SchemaContent)
async def content(content: SchemaContent):
    db_content = ModelContent(
        content=content.content, 
        money=content.money, 
        invoice_id = content.invoice_id
        )
    db.session.add(db_content)
    db.session.commit()
    return db_content


@app.get('/content/')
async def content():
    return {"message": "content"}
    # print('ffff')
    # content = db.session.query(ModelContent).all()
    # return content

@app.post('/invoice/', response_model=SchemaInvoice)
async def invoice(invoice:SchemaInvoice):
    db_invoice = ModelInvoice(
        code_invoice=invoice.code_invoice, 
        number_of_invoice=invoice.number_of_invoice,
        organization=invoice.organization, 
        organization_code=invoice.organization_code,
        document_number=invoice.document_number, 
        document_date=invoice.document_date,
        organization_received=invoice.organization_received, 
        bank_account=invoice.bank_account,
        location=invoice.location, 
        date=invoice.date
        )
    db.session.add(db_invoice)
    db.session.commit()
    return db_invoice

@app.get('/invoice/')
async def invoice():
    invoice = db.session.query(ModelInvoice).all()
    return invoice


# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)