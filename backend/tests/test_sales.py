from decimal import Decimal

from conftest import create_product


def test_sale_reduces_stock_and_calculates_total(client, owner_headers, staff_headers):
    helmet = create_product(client, owner_headers, name="Helmet", price=250, stock_quantity=40)
    gloves = create_product(client, owner_headers, name="Gloves", price=49.5, stock_quantity=100)

    res = client.post(
        "/sales/",
        json={"items": [
            {"product_id": helmet["id"], "quantity": 2},
            {"product_id": gloves["id"], "quantity": 4},
        ]},
        headers=staff_headers,
    )
    assert res.status_code == 201
    assert Decimal(res.json()["total_amount"]) == Decimal("698.00")

    helmet_after = client.get(f"/products/{helmet['id']}", headers=owner_headers).json()
    gloves_after = client.get(f"/products/{gloves['id']}", headers=owner_headers).json()
    assert helmet_after["stock_quantity"] == 38
    assert gloves_after["stock_quantity"] == 96


def test_not_enough_stock_is_rejected_and_stock_unchanged(client, owner_headers):
    product = create_product(client, owner_headers, stock_quantity=3)

    res = client.post("/sales/", json={"items": [{"product_id": product["id"], "quantity": 5}]}, headers=owner_headers)
    assert res.status_code == 400

    after = client.get(f"/products/{product['id']}", headers=owner_headers).json()
    assert after["stock_quantity"] == 3


def test_unknown_product_returns_404(client, owner_headers):
    res = client.post("/sales/", json={"items": [{"product_id": 999, "quantity": 1}]}, headers=owner_headers)
    assert res.status_code == 404


def test_duplicate_items_are_combined(client, owner_headers):
    product = create_product(client, owner_headers, price=100, stock_quantity=10)

    res = client.post(
        "/sales/",
        json={"items": [
            {"product_id": product["id"], "quantity": 2},
            {"product_id": product["id"], "quantity": 3},
        ]},
        headers=owner_headers,
    )
    assert res.status_code == 201
    assert len(res.json()["items"]) == 1
    assert res.json()["items"][0]["quantity"] == 5


def test_sale_records_who_made_it(client, owner_headers, staff_headers):
    product = create_product(client, owner_headers)
    res = client.post("/sales/", json={"items": [{"product_id": product["id"], "quantity": 1}]}, headers=staff_headers)
    assert res.json()["created_by"]["username"] == "staff"


def test_invoice_returns_pdf(client, owner_headers):
    product = create_product(client, owner_headers)
    sale = client.post("/sales/", json={"items": [{"product_id": product["id"], "quantity": 1}]}, headers=owner_headers).json()

    res = client.get(f"/sales/{sale['id']}/invoice", headers=owner_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")