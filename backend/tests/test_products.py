from conftest import create_product


def test_products_require_login(client):
    res = client.get("/products/")
    assert res.status_code == 401


def test_owner_can_create_and_list_products(client, owner_headers):
    create_product(client, owner_headers, name="Gloves")
    res = client.get("/products/", headers=owner_headers)
    assert res.status_code == 200
    assert [p["name"] for p in res.json()] == ["Gloves"]


def test_staff_cannot_create_products(client, staff_headers):
    res = client.post("/products/", json={"name": "Gloves", "price": 50}, headers=staff_headers)
    assert res.status_code == 403


def test_negative_price_is_rejected(client, owner_headers):
    res = client.post("/products/", json={"name": "Gloves", "price": -5}, headers=owner_headers)
    assert res.status_code == 422


def test_owner_can_update_product(client, owner_headers):
    product = create_product(client, owner_headers)
    res = client.patch(f"/products/{product['id']}", json={"price": 300}, headers=owner_headers)
    assert res.status_code == 200
    assert float(res.json()["price"]) == 300
    assert res.json()["name"] == "Safety Helmet"


def test_cannot_delete_product_with_sales(client, owner_headers):
    product = create_product(client, owner_headers)
    client.post("/sales/", json={"items": [{"product_id": product["id"], "quantity": 1}]}, headers=owner_headers)

    res = client.delete(f"/products/{product['id']}", headers=owner_headers)
    assert res.status_code == 409