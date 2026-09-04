from fastapi.testclient import TestClient


def test_client(client):
    assert type(client) == TestClient


def test_customer_fixture(customer):
    assert customer.id is not None
    assert customer.email == "fixture-test@ejemplo.com"