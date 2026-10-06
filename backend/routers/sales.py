from collections import defaultdict
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/", response_model=schemas.SaleResponse, status_code=201)
def create_sale(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    # Combine duplicates (e.g. the same product listed twice)
    quantities = defaultdict(int)
    for item in sale_in.items:
        quantities[item.product_id] += item.quantity

    # Lock these product rows so two sales at the same moment can't oversell stock
    products = (
        db.query(models.Product)
        .filter(models.Product.id.in_(quantities.keys()))
        .with_for_update()
        .all()
    )
    products_by_id = {p.id: p for p in products}

    missing = set(quantities) - set(products_by_id)
    if missing:
        raise HTTPException(status_code=404, detail=f"Products not found: {sorted(missing)}")

    for product_id, qty in quantities.items():
        product = products_by_id[product_id]
        if product.stock_quantity < qty:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}: {product.stock_quantity} available, {qty} requested",
            )

    sale = models.Sale(customer_name=sale_in.customer_name, total_amount=Decimal("0"))
    total = Decimal("0")

    for product_id, qty in quantities.items():
        product = products_by_id[product_id]
        line_total = product.price * qty
        sale.items.append(
            models.SaleItem(
                product_id=product_id,
                quantity=qty,
                unit_price=product.price,
                line_total=line_total,
            )
        )
        product.stock_quantity -= qty
        total += line_total

    sale.total_amount = total
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale

@router.get("/", response_model=list[schemas.SaleResponse])
def list_sales(db: Session = Depends(get_db)):
    return db.query(models.Sale).order_by(models.Sale.created_at.desc()).all()

@router.get("/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.get(models.Sale, sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale