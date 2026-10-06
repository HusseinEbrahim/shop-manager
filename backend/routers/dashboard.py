from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)

IST = "Asia/Kolkata"


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    # "Today" in Indian time, calculated inside the database
    sale_day = func.date(func.timezone(IST, models.Sale.created_at))
    today = func.date(func.timezone(IST, func.now()))

    today_total, today_count = (
        db.query(
            func.coalesce(func.sum(models.Sale.total_amount), 0),
            func.count(models.Sale.id),
        )
        .filter(sale_day == today)
        .one()
    )

    low_stock = (
        db.query(models.Product)
        .filter(models.Product.stock_quantity <= models.Product.low_stock_threshold)
        .order_by(models.Product.stock_quantity)
        .all()
    )

    top = (
        db.query(
            models.Product.id,
            models.Product.name,
            func.sum(models.SaleItem.quantity).label("units_sold"),
            func.sum(models.SaleItem.line_total).label("revenue"),
        )
        .join(models.SaleItem, models.SaleItem.product_id == models.Product.id)
        .join(models.Sale, models.Sale.id == models.SaleItem.sale_id)
        .filter(models.Sale.created_at >= func.now() - timedelta(days=30))
        .group_by(models.Product.id, models.Product.name)
        .order_by(func.sum(models.SaleItem.quantity).desc())
        .limit(5)
        .all()
    )

    return {
        "today_sales_total": today_total,
        "today_sales_count": today_count,
        "low_stock_products": low_stock,
        "top_products": [
            {
                "product_id": row.id,
                "name": row.name,
                "units_sold": row.units_sold,
                "revenue": row.revenue,
            }
            for row in top
        ],
    }