import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from database import SessionLocal
from auth import hash_password
import models

PRODUCTS = [
    ("Safety Helmet", "PPE", "249.00", "ABC Safety Supplies"),
    ("Nitrile Gloves (Box of 100)", "PPE", "399.00", "MediGuard"),
    ("Reflective Safety Vest", "PPE", "180.00", "ABC Safety Supplies"),
    ("Safety Goggles", "PPE", "150.00", "VisionPro"),
    ("N95 Mask (Pack of 10)", "PPE", "450.00", "MediGuard"),
    ("Steel Toe Boots", "PPE", "1499.00", "WorkSafe India"),
    ("Claw Hammer", "Hardware", "320.00", "Taparia Tools"),
    ("Screwdriver Set", "Hardware", "550.00", "Taparia Tools"),
    ("Measuring Tape 5m", "Hardware", "199.00", "Stanley"),
    ("Adjustable Wrench", "Hardware", "420.00", "Stanley"),
    ("Electrical Tape", "Hardware", "35.00", "Anchor"),
    ("Cable Ties (Pack of 100)", "Hardware", "90.00", "Anchor"),
]

CUSTOMERS = [None, None, "Rahul Builders", "Patil Constructions", "Sharma Electricals", "Kulkarni & Sons"]


def main():
    random.seed(42)
    db = SessionLocal()
    try:
        # Wipe existing data
        db.query(models.SaleItem).delete()
        db.query(models.Sale).delete()
        db.query(models.Product).delete()
        db.query(models.User).delete()
        db.commit()

        owner = models.User(username="demo", hashed_password=hash_password("demo12345"), role="owner")
        staff = models.User(username="staff", hashed_password=hash_password("staff12345"), role="staff")
        db.add_all([owner, staff])

        products = [
            models.Product(
                name=name,
                category=category,
                price=Decimal(price),
                stock_quantity=random.randint(60, 150),
                low_stock_threshold=10,
                supplier=supplier,
            )
            for name, category, price, supplier in PRODUCTS
        ]
        db.add_all(products)
        db.flush()  # assigns IDs

        now = datetime.now(timezone.utc)
        for days_ago in range(30, -1, -1):
            for _ in range(random.randint(1, 4)):
                sale = models.Sale(
                    customer_name=random.choice(CUSTOMERS),
                    total_amount=Decimal("0"),
                    created_by_id=random.choice([owner, staff]).id,
                    created_at=now - timedelta(days=days_ago, minutes=random.randint(0, 300)),
                )
                total = Decimal("0")
                for product in random.sample(products, random.randint(1, 3)):
                    qty = min(random.randint(1, 5), product.stock_quantity)
                    if qty == 0:
                        continue
                    line_total = product.price * qty
                    sale.items.append(
                        models.SaleItem(
                            product_id=product.id,
                            quantity=qty,
                            unit_price=product.price,
                            line_total=line_total,
                        )
                    )
                    product.stock_quantity -= qty
                    total += line_total
                if sale.items:
                    sale.total_amount = total
                    db.add(sale)

        # Make a few products low on stock so the dashboard has something to show
        products[1].stock_quantity = 6
        products[5].stock_quantity = 3
        products[10].stock_quantity = 8

        db.commit()
        print("Demo data created. Logins: demo / demo12345 (owner), staff / staff12345 (staff)")
    finally:
        db.close()


if __name__ == "__main__":
    main()