import re

from fastapi import status


def test_root(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()


def test_time_returns_country_timezone(client):
    response = client.get("/time/CO")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["iso_code"] == "CO"
    assert body["timezone"] == "America/Bogota"


def test_time_normalizes_lowercase_iso_code(client):
    response = client.get("/time/co")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["iso_code"] == "CO"


def test_time_unknown_country_falls_back_to_utc(client):
    # Comportamiento actual: un pais no listado devuelve UTC en vez de 404.
    response = client.get("/time/JP")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["timezone"] == "UTC"


def test_time_uses_24h_format_by_default(client):
    response = client.get("/time/CO")
    hora = response.json()["time"]
    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", hora)


def test_time_12h_format_includes_meridiem(client):
    response = client.get("/time/CO?format_24=false")
    hora = response.json()["time"]
    assert re.fullmatch(r"\d{2}:\d{2}:\d{2} (AM|PM)", hora)


def test_time_rejects_invalid_format_24(client):
    response = client.get("/time/CO?format_24=banana")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
