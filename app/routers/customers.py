from fastapi import APIRouter, HTTPException
from sqlmodel import select

from db import SessionDependency
from models import Customer, CustomerCreate, CustomerPlan, CustomerUpdate, Plan

router = APIRouter()


db_customers: list[Customer] = []


@router.post("/customers", response_model=Customer, tags=["customers"])
async def create_customer(customer_data: CustomerCreate, session: SessionDependency):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("/customers/{customer_id}", response_model=Customer, tags=["customers"])
async def read_customer(customer_id: int, session: SessionDependency):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_db


@router.patch("/customers/{customer_id}", response_model=Customer, tags=["customers"])
async def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDependency
):
    # 1. Buscar si el cliente existe en la base de datos
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=404, detail="Customer not found")

    # 2. Extraer solo los campos que el usuario envió en el JSON (ignora los omitidos)
    update_data = customer_data.model_dump(exclude_unset=True)

    # 3. Actualizar el objeto usando la función nativa de SQLModel (¡Adiós al bucle for!)
    customer_db.sqlmodel_update(update_data)

    # 4. Confirmar cambios y refrescar
    session.add(customer_db)
    session.commit()
    session.refresh(customer_db)

    return customer_db


@router.delete("/customers/{customer_id}", tags=["customers"])
async def delete_customer(customer_id: int, session: SessionDependency):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    session.delete(customer_db)
    session.commit()
    return {"detail": "Ok, customer deleted successfully"}


@router.get("/customers", response_model=list[Customer], tags=["customers"])
async def list_customer(session: SessionDependency):
    return session.exec(select(Customer)).all()


@router.get("/customers/{id}", response_model=Customer, tags=["customers"])
async def get_customer(id: int):
    for customer in db_customers:
        if customer.id == id:
            return customer
    raise HTTPException(status_code=404, detail="Customer no encontrado")


@router.post("/customers/{customer_id}/plans/{plan_id}")
async def subscribe_customer_to_plan(
    customer_id: int, plan_id: int, session: SessionDependency
):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(status_code=404, detail="Customer or Plan not found")

    customer_plan_db = CustomerPlan(plan_id=plan_db.id, customer_id=customer_db.id)

    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    return customer_plan_db


@router.get("/customers/{customer_id}/plans")
async def list_customer_plans(customer_id: int, session: SessionDependency):
    customer_db = session.get(Customer, customer_id)

    if not customer_db:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer_db.plans
