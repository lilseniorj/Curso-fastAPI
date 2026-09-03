from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import Field, Relationship, Session, SQLModel, select

from db import engine


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class CustomerPlan(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plan_id: int = Field(foreign_key="plan.id")
    customer_id: int = Field(foreign_key="customer.id")
    status: StatusEnum = Field(default=StatusEnum.active)


class Plan(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(default=None)
    description: str | None = None
    price: int = Field(default=None)
    customers: list["Customer"] = Relationship(
        back_populates="plans", link_model=CustomerPlan
    )


class CustomerBase(SQLModel):
    name: str | None = Field(default=None)
    description: str | None = None
    email: EmailStr | None= Field(default=None)
    age: int | None= Field(default=None)
    phone: str | None= Field(default=None)
    document_id: str | None= Field(default=None)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None:
            return value

        value = value.lower()

        with Session(engine) as session:
            query = select(Customer).where(Customer.email == value)
            result = session.exec(query).first()
            if result:
                raise ValueError("This Email is already registered")
            return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value

        value = value.replace(" ", "").replace("-", "")

        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        if len(value) != 10:
            raise ValueError("Phone number must be 10 digits long")
        return value

    @field_validator("document_id")
    @classmethod
    def validate_document_id(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value.isdigit():
            raise ValueError("Document ID must contain only digits")
        with Session(engine) as session:
            query = select(Customer).where(Customer.document_id == value)
            if session.exec(query).first():
                raise ValueError("This Document ID is already registered")
            return value

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass


class Customer(CustomerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    transactions: list["Transaction"] = Relationship(back_populates="customer")
    plans: list[Plan] = Relationship(
        back_populates="customers", link_model=CustomerPlan
    )

class TransactionBase(SQLModel):
    amount: int
    description: str

class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="transactions")


class TransactionCreate(TransactionBase):
    customer_id: int = Field(foreign_key="customer.id")

class Invoice(BaseModel):
    id: int
    customer: Customer
    transactions: list[Transaction]
    total: int

    @property
    def amount_total(self):
        return sum(transaction.amount for transaction in self.transactions)