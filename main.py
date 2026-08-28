import zoneinfo
from datetime import datetime

from fastapi import FastAPI, HTTPException

from db import SessionDependency, create_all_tables
from models import Customer, CustomerCreate, Invoice, Transaction
from sqlmodel import select

app = FastAPI(lifespan=create_all_tables)



@app.get("/")
async def root():

    return {"message": "Hello Lil Seniorj"}


country_timezone = {
    "CO": "America/Bogota",
    "US": "America/New_York",
    "MX": "America/Mexico_City",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}


@app.get("/time/{iso_code}")
async def time(iso_code: str, format_24: bool = True):
    iso = iso_code.upper()
    timezone_str = country_timezone.get(iso, "UTC")
    tz = zoneinfo.ZoneInfo(timezone_str)
    datetime_format = "%H:%M:%S" if format_24 else "%I:%M:%S %p"
    return {
        "iso_code": iso,
        "timezone": timezone_str,
        "time": datetime.now(tz).strftime(datetime_format),
    }

db_customers: list[Customer] = []

@app.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDependency):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@app.get("/customers", response_model=list[Customer])
async def list_customer(session: SessionDependency):
    return session.exec(select(Customer)).all()


@app.get("/customers/{id}", response_model=Customer)
async def get_customer(id: int):
    for customer in db_customers:
        if customer.id == id:
            return customer
    raise HTTPException(status_code=404, detail="Customer no encontrado")

@app.post("/transactions")
async def create_transaction(transaction_data: Transaction):
    return transaction_data


@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
