from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColumnInfo:
    name: str
    type: str
    description: str


@dataclass(frozen=True, slots=True)
class TableInfo:
    table_name: str
    description: str
    columns: list[ColumnInfo]


ALLOWED_SQL_TABLES = {
    "demo_orders",
    "demo_order_items",
    "demo_customers",
    "demo_products",
    "demo_reviews",
    "demo_after_sales",
}


DEMO_SCHEMA = [
    TableInfo(
        table_name="demo_orders",
        description="Demo e-commerce order table. Abnormal statuses are canceled and unavailable.",
        columns=[
            ColumnInfo("order_id", "string", "Unique order id."),
            ColumnInfo("customer_id", "string", "Customer id joined to demo_customers."),
            ColumnInfo(
                "order_status",
                "string",
                "delivered, shipped, processing, canceled, unavailable.",
            ),
            ColumnInfo("order_purchase_timestamp", "timestamp", "When the order was purchased."),
            ColumnInfo(
                "order_delivered_customer_date",
                "timestamp",
                "Actual customer delivery time.",
            ),
            ColumnInfo(
                "order_estimated_delivery_date",
                "timestamp",
                "Estimated delivery deadline.",
            ),
            ColumnInfo("payment_value", "number", "Total payment value for the order."),
            ColumnInfo("seller_id", "string", "Demo seller id."),
            ColumnInfo("state", "string", "Customer state for order aggregation."),
        ],
    ),
    TableInfo(
        table_name="demo_order_items",
        description="Demo order item table for product and seller level analysis.",
        columns=[
            ColumnInfo("order_id", "string", "Order id joined to demo_orders."),
            ColumnInfo("product_id", "string", "Product id joined to demo_products."),
            ColumnInfo("seller_id", "string", "Demo seller id."),
            ColumnInfo("quantity", "integer", "Quantity of products in the order item."),
            ColumnInfo("price", "number", "Item unit price."),
            ColumnInfo("freight_value", "number", "Freight value for the item."),
        ],
    ),
    TableInfo(
        table_name="demo_customers",
        description="Demo customer table. Email is sensitive and must not be selected.",
        columns=[
            ColumnInfo("customer_id", "string", "Customer id joined to demo_orders."),
            ColumnInfo("customer_name", "string", "Demo customer display name."),
            ColumnInfo("state", "string", "Customer state."),
            ColumnInfo("city", "string", "Customer city."),
            ColumnInfo("created_at", "timestamp", "Customer record creation time."),
        ],
    ),
    TableInfo(
        table_name="demo_products",
        description="Demo product catalog table for category and department analysis.",
        columns=[
            ColumnInfo("product_id", "string", "Product id joined to demo_order_items."),
            ColumnInfo("product_name", "string", "Demo product display name."),
            ColumnInfo("category", "string", "Product category."),
            ColumnInfo("department", "string", "Product department."),
            ColumnInfo("price", "number", "Product list price."),
        ],
    ),
    TableInfo(
        table_name="demo_reviews",
        description="Demo review table. review_score <= 2 indicates low-score abnormal orders.",
        columns=[
            ColumnInfo("review_id", "string", "Unique review id."),
            ColumnInfo("order_id", "string", "Order id joined to demo_orders."),
            ColumnInfo("review_score", "integer", "Score from 1 to 5."),
            ColumnInfo("review_comment", "string", "Demo review comment."),
            ColumnInfo("created_at", "timestamp", "Review creation time."),
        ],
    ),
    TableInfo(
        table_name="demo_after_sales",
        description="Demo after-sales table. Any issue_type can indicate after-sales abnormality.",
        columns=[
            ColumnInfo("after_sales_id", "string", "Unique after-sales case id."),
            ColumnInfo("order_id", "string", "Order id joined to demo_orders."),
            ColumnInfo(
                "issue_type",
                "string",
                "delivery_delay, product_damage, refund_request, etc.",
            ),
            ColumnInfo("issue_description", "string", "Demo issue description."),
            ColumnInfo("status", "string", "open, processing, resolved, rejected."),
            ColumnInfo("created_at", "timestamp", "Case creation time."),
        ],
    ),
]


def read_allowed_schema() -> dict:
    return {
        "tables": [
            {
                "table_name": table.table_name,
                "description": table.description,
                "columns": [
                    {
                        "name": column.name,
                        "type": column.type,
                        "description": column.description,
                    }
                    for column in table.columns
                ],
            }
            for table in DEMO_SCHEMA
        ]
    }


def allowed_table_names() -> set[str]:
    return set(ALLOWED_SQL_TABLES)
