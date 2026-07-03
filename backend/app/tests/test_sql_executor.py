from types import SimpleNamespace

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.sql_executor import execute_safe_sql


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


def test_postgres_executor_uses_independent_connection() -> None:
    class FakeResult:
        def keys(self):
            return ["cnt"]

        def fetchmany(self, max_rows):
            return [SimpleNamespace(_mapping={"cnt": 1})]

    class FakeTransaction:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

    class FakeConnection:
        def __init__(self):
            self.statements = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

        def begin(self):
            return FakeTransaction()

        def execute(self, statement):
            self.statements.append(str(statement))
            if str(statement).startswith("SET LOCAL"):
                return None
            return FakeResult()

    class FakeBind:
        dialect = SimpleNamespace(name="postgresql")

        def __init__(self):
            self.connection = FakeConnection()

        def connect(self):
            return self.connection

    class FakeSession:
        def __init__(self):
            self.bind = FakeBind()

        def get_bind(self):
            return self.bind

        def execute(self, statement):
            raise AssertionError("PostgreSQL SQL execution must not use the caller session.")

    db = FakeSession()
    result = execute_safe_sql(db, "SELECT 1 AS cnt")

    assert result.error is None
    assert result.rows == [{"cnt": 1}]
    assert db.bind.connection.statements == [
        "SET LOCAL TRANSACTION READ ONLY",
        "SET LOCAL statement_timeout = 5000",
        "SELECT 1 AS cnt",
    ]
