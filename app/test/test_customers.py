from fastapi import status
from fastapi.testclient import TestClient


def test_client(client):
    assert type(client) == TestClient

def test_customer_fixture(customer):
    assert customer.id is not None
    assert customer.email == "fixture-test@ejemplo.com"


def test_create_customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Jhon Do",
            "email": "jhon@example.com",
            "age": 33,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

def test_read_customer(client, customer):
    response = client.get(f"/customers/{customer.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == customer.name

def test_update_customer(client, customer):
    response = client.patch(f"/customers/{customer.id}", json={"age": 40})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["age"] == 40
    assert response.json()["name"] == customer.name    # ← no se tocó


def test_delete_customer(client, customer):
    response_read = client.delete(f"/customers/{customer.id}")
    assert response_read.status_code == status.HTTP_200_OK

    response_read = client.get(f"/customers/{customer.id}")
    assert response_read.status_code == status.HTTP_404_NOT_FOUND


def test_read_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_customer_invalid_email(client):
    response = client.post("/customers", json={"name": "X", "email": "no-es-un-email"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
