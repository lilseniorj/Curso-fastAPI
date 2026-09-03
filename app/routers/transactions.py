from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from db import SessionDependency
from models import Customer, Transaction, TransactionCreate

router = APIRouter()

@router.post("/transactions", status_code=201, tags=["transactions"])
async def create_transaction(transaction_data: TransactionCreate, session: SessionDependency):

    transaction_data_dict = transaction_data.model_dump()
    customer = session.get(Customer, transaction_data_dict.get("customer_id"))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    transaction_db= Transaction.model_validate(transaction_data_dict)
    session.add(transaction_db)
    session.commit()
    session.refresh(transaction_db)

    return transaction_db


@router.get("/transactions", tags=["transactions"])
async def list_transactions(
    session: SessionDependency,
    skip: int = Query(0, description="Omited transactions"),
    limit: int = Query(10, description="Limit of transactions to return"),
):
    query = select(Transaction).offset(skip).limit(limit)
    transactions = session.exec(query).all()
    return transactions
