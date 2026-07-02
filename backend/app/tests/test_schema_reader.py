from app.services.schema_reader import read_allowed_schema


def test_schema_reader_exposes_only_demo_tables() -> None:
    schema = read_allowed_schema()
    table_names = {table["table_name"] for table in schema["tables"]}

    assert table_names == {
        "demo_orders",
        "demo_order_items",
        "demo_customers",
        "demo_products",
        "demo_reviews",
        "demo_after_sales",
    }
    assert "users" not in table_names
    assert "permissions" not in table_names


def test_schema_reader_has_column_descriptions() -> None:
    schema = read_allowed_schema()

    for table in schema["tables"]:
        assert table["description"]
        assert table["columns"]
        for column in table["columns"]:
            assert column["name"]
            assert column["type"]
            assert column["description"]

