"""Genera datos de prueba para probar la paginación.

Uso (desde la raíz del proyecto):
    python create_multiple_transactions.py
"""

from sqlmodel import Session, SQLModel

from db import engine
from models import Customer, Transaction

CANTIDAD = 100


def main():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        customer = Customer(
            name="Cliente de prueba",
            description="Generado para probar paginacion",
            email="pruebas@correo.com",
            age=33,
        )
        session.add(customer)
        session.commit()
        session.refresh(customer)

        for i in range(CANTIDAD):
            session.add(
                Transaction(
                    amount=(i + 1) * 100,
                    description=f"Transaccion numero {i + 1}",
                    customer_id=customer.id,
                )
            )

        session.commit()
        print(f"Listo: customer id={customer.id} con {CANTIDAD} transacciones")


if __name__ == "__main__":
    main()
