from app.services.sql_executor import execute_safe_sql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def test_sql_executor_returns_columns_rows_and_count() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE demo_orders (state TEXT, order_status TEXT)"))
        connection.execute(
            text(
                "INSERT INTO demo_orders (state, order_status) "
                "VALUES ('SP', 'canceled'), ('RJ', 'delivered')"
            )
        )

    with Session(engine) as db:
        result = execute_safe_sql(
            db,
            "SELECT state, COUNT(*) AS cnt FROM demo_orders GROUP BY state LIMIT 100",
        )

    assert result.error is None
    assert result.columns == ["state", "cnt"]
    assert result.row_count == 2
    assert result.rows[0]["state"] in {"SP", "RJ"}


def test_sql_executor_captures_query_errors() -> None:
    engine = create_engine("sqlite:///:memory:")

    with Session(engine) as db:
        result = execute_safe_sql(db, "SELECT missing FROM demo_orders LIMIT 100")

    assert result.error is not None
    assert result.row_count == 0

