import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.demo_order import (
    DemoAfterSales,
    DemoCustomer,
    DemoOrder,
    DemoOrderItem,
    DemoProduct,
    DemoReview,
)

STATES = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "PE", "GO", "CE"]
CITIES = ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Salvador"]
CATEGORIES = [
    ("electronics", "consumer"),
    ("home_appliances", "home"),
    ("books", "media"),
    ("fashion", "retail"),
    ("sports", "retail"),
    ("beauty", "retail"),
    ("furniture", "home"),
]
ISSUE_TYPES = [
    "delivery_delay",
    "product_damage",
    "wrong_item",
    "refund_request",
    "payment_issue",
    "customer_complaint",
]


def seed(order_count: int = 240) -> None:
    random.seed(42)
    with SessionLocal() as db:
        if db.scalar(select(DemoOrder.id).limit(1)):
            print("Demo SQL Agent orders already exist; skipping.")
            return

        products = _build_products()
        customers = _build_customers(80)
        db.add_all(products)
        db.add_all(customers)
        db.flush()

        orders: list[DemoOrder] = []
        items: list[DemoOrderItem] = []
        reviews: list[DemoReview] = []
        after_sales: list[DemoAfterSales] = []
        now = datetime.now(UTC)

        for index in range(order_count):
            order_id = f"ORD-{100000 + index}"
            customer = customers[index % len(customers)]
            product = products[index % len(products)]
            purchased_at = now - timedelta(days=random.randint(0, 89))
            estimated = purchased_at + timedelta(days=random.randint(3, 12))
            delayed = index % 7 == 0
            canceled = index % 17 == 0
            unavailable = index % 23 == 0

            if canceled:
                status = "canceled"
                delivered = None
            elif unavailable:
                status = "unavailable"
                delivered = None
            else:
                status = random.choice(["delivered", "shipped", "processing"])
                delivered = (
                    estimated + timedelta(days=random.randint(1, 6))
                    if delayed
                    else estimated
                )

            quantity = random.randint(1, 4)
            payment_value = round(product.price * quantity + random.uniform(5, 35), 2)
            if index % 41 == 0:
                payment_value *= 3

            seller_id = f"SELLER-{index % 18:03d}"
            orders.append(
                DemoOrder(
                    order_id=order_id,
                    customer_id=customer.customer_id,
                    order_status=status,
                    order_purchase_timestamp=purchased_at,
                    order_delivered_customer_date=delivered,
                    order_estimated_delivery_date=estimated,
                    payment_value=payment_value,
                    seller_id=seller_id,
                    state=customer.state,
                )
            )
            items.append(
                DemoOrderItem(
                    order_id=order_id,
                    product_id=product.product_id,
                    seller_id=seller_id,
                    quantity=quantity,
                    price=product.price,
                    freight_value=round(random.uniform(5, 28), 2),
                )
            )

            low_score = index % 9 == 0 or delayed or canceled
            review_score = random.choice([1, 2]) if low_score else random.choice([3, 4, 5])
            reviews.append(
                DemoReview(
                    review_id=f"REV-{100000 + index}",
                    order_id=order_id,
                    review_score=review_score,
                    review_comment=_review_comment(review_score, delayed, status),
                )
            )

            if index % 6 == 0 or canceled or unavailable:
                issue_type = random.choice(ISSUE_TYPES)
                after_sales.append(
                    DemoAfterSales(
                        after_sales_id=f"AS-{100000 + index}",
                        order_id=order_id,
                        issue_type=issue_type,
                        issue_description=f"Demo after-sales case: {issue_type}",
                        status=random.choice(["open", "processing", "resolved", "rejected"]),
                    )
                )

        db.add_all(orders)
        db.add_all(items)
        db.add_all(reviews)
        db.add_all(after_sales)
        db.commit()
        print(f"Seeded {len(orders)} demo orders for SQL Agent.")


def reset_and_seed(order_count: int = 240) -> None:
    with SessionLocal() as db:
        for model in (
            DemoAfterSales,
            DemoReview,
            DemoOrderItem,
            DemoOrder,
            DemoProduct,
            DemoCustomer,
        ):
            db.execute(delete(model))
        db.commit()
    seed(order_count)


def _build_customers(count: int) -> list[DemoCustomer]:
    customers = []
    for index in range(count):
        state = STATES[index % len(STATES)]
        customers.append(
            DemoCustomer(
                customer_id=f"CUST-{10000 + index}",
                customer_name=f"Demo Customer {index + 1}",
                email=f"customer{index + 1}@example.com",
                state=state,
                city=CITIES[index % len(CITIES)],
            )
        )
    return customers


def _build_products() -> list[DemoProduct]:
    products = []
    for index in range(35):
        category, department = CATEGORIES[index % len(CATEGORIES)]
        products.append(
            DemoProduct(
                product_id=f"PROD-{1000 + index}",
                product_name=f"Demo {category.replace('_', ' ').title()} Item {index + 1}",
                category=category,
                department=department,
                price=round(random.uniform(15, 450), 2),
            )
        )
    return products


def _review_comment(score: int, delayed: bool, status: str) -> str:
    if score <= 2 and delayed:
        return "Low score due to delivery delay."
    if score <= 2 and status in {"canceled", "unavailable"}:
        return f"Low score due to order status: {status}."
    if score <= 2:
        return "Low score due to product or service issue."
    return "Demo review with acceptable customer experience."


if __name__ == "__main__":
    seed()
