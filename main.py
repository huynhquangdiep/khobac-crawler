
from pydantic import ValidationError
from sqlalchemy import create_engine
import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy.orm import sessionmaker
from schema import Content
from schema import Invoice
from models import ContentModel
from models import InvoiceModel
import os
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv('.env')
from datetime import datetime
app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.get("/")
async def root():
    return {"message": " hello"}

@app.post('/content', response_model=Content)
async def content(content: Content):
    try:
        db_content = ContentModel(
            content=content.content, 
            money=content.money, 
            invoice_id=content.invoice_id,
            time_updated=datetime.utcnow()  # Set time_updated to the current time
        )
        
        # Add to session and commit changes
        db.session.add(db_content)
        db.session.commit()
        db.session.refresh(db_content)

        return db_content
    except Exception as e:
        # Print or log the error
        print(f"Error: {str(e)}")
        # Raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/content')
async def content():
    content = db.session.query(ContentModel).all()
    return content

@app.post('/invoice', response_model=Invoice)
async def create_invoice(invoice: Invoice):
    try:
        db_invoice = InvoiceModel(
            code_invoice=invoice.code_invoice, 
            invoice_id=invoice.invoice_id,
            organization=invoice.organization, 
            organization_code=invoice.organization_code,
            document_number=invoice.document_number, 
            document_date=invoice.document_date,
            organization_received=invoice.organization_received, 
            bank_account=invoice.bank_account,
            location=invoice.location, 
            date=invoice.date,
            time_updated=datetime.utcnow()  # Set time_updated to the current time
        )

        db.session.add(db_invoice)
        db.session.commit()
        db.session.refresh(db_invoice)
        return db_invoice
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/invoice')
async def invoice():
    invoice = db.session.query(InvoiceModel).all()
    return invoice

@app.post('/create_invoice_with_contents')
def create_invoice_with_contents(invoice: Invoice):
    try:
        # Create an instance of InvoiceModel
        db_invoice = InvoiceModel(
            code_invoice=invoice.code_invoice, 
            invoice_id=invoice.invoice_id,
            organization=invoice.organization, 
            organization_code=invoice.organization_code,
            document_number=invoice.document_number, 
            document_date=invoice.document_date,
            organization_received=invoice.organization_received, 
            bank_account=invoice.bank_account,
            location=invoice.location, 
            date=invoice.date,
            time_updated=datetime.utcnow()  # Set time_updated to the current time
        )

        # Create instances of ContentModel and associate them with the invoice
        for content_data in invoice.contents:
            db_content = ContentModel(**content_data.dict())
            db_invoice.contents.append(db_content)
        # Add to session and commit changes
        db.session.add(db_invoice)
        db.session.commit()
        db.session.refresh(db_invoice)

        return db_invoice

    except ValueError as ve:
        # Handle the case where the conversion fails
        raise HTTPException(status_code=422, detail=f"Invalid integer format: {ve}")

    except ValidationError as ve:
        # Capture and return validation errors
        raise HTTPException(status_code=422, detail=ve.errors())

    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error creating invoice: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)