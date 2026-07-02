from app.services.sql_guardrails import validate_sql


def test_allows_select_and_adds_limit() -> None:
    result = validate_sql("SELECT state, COUNT(*) AS cnt FROM demo_orders GROUP BY state")

    assert result.safe is True
    assert result.sql is not None
    assert "LIMIT 100" in result.sql


def test_clamps_limit_to_100() -> None:
    result = validate_sql(
        "SELECT state, COUNT(*) AS cnt FROM demo_orders GROUP BY state LIMIT 1000"
    )

    assert result.safe is True
    assert result.sql is not None
    assert "LIMIT 100" in result.sql


def test_blocks_mutating_sql() -> None:
    dangerous = [
        "DELETE FROM demo_orders",
        "UPDATE demo_orders SET order_status = 'delivered'",
        "INSERT INTO demo_orders (order_id) VALUES ('x')",
        "DROP TABLE demo_orders",
        "ALTER TABLE demo_orders ADD COLUMN x text",
    ]

    for sql in dangerous:
        assert validate_sql(sql).safe is False


def test_blocks_select_star_and_multi_statement() -> None:
    assert validate_sql("SELECT * FROM demo_orders LIMIT 10").safe is False
    assert validate_sql("SELECT order_id FROM demo_orders; DROP TABLE users").safe is False


def test_blocks_sensitive_tables_and_fields() -> None:
    assert validate_sql("SELECT id, password_hash FROM users LIMIT 10").safe is False
    assert validate_sql("SELECT customer_id, email FROM demo_customers LIMIT 10").safe is False
