from __future__ import annotations

import zoneinfo
from datetime import datetime

from fastapi import FastAPI

from db import create_all_tables
from models import Invoice, Transaction

from .routers import customers, transactions

app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)


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


@app.post("/invoices")
async def create_invoice(invoice_data: Invoice):
    return invoice_data
