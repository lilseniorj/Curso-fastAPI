from __future__ import annotations

import os
import secrets
import time
import zoneinfo
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from db import create_all_tables
from models import Invoice

from .routers import customers, plans, transactions

load_dotenv()
app = FastAPI(lifespan=create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(plans.router)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    print(f"Request: {request.url} completed in: {process_time:.4f} seconds")

    return response

@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    print("--- Request Headers ---")
    for name, value in request.headers.items():
        print(f"{name}: {value}")

    response = await call_next(request)
    return response

security = HTTPBasic()

@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials ,Depends(security)]):
    if credentials.username == os.getenv("API_USERNAME") and secrets.compare_digest(credentials.password, os.getenv("API_PASSWORD")):
        return {"message": f"Hello, {credentials.username}!"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


country_timezone = {
    "CO": "America/Bogota",
    "US": "America/New_York",
    "MX": "America/Mexico_City",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}


@app.get("/time/{iso_code}")
async def get_time_by_iso_code(iso_code: str, format_24: bool = True):
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
