import csv
import re
from pathlib import Path


def _repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "data").exists() and (candidate / "docs").exists():
            return candidate
    workspace = Path("/workspace")
    if (workspace / "data").exists() and (workspace / "docs").exists():
        return workspace
    return Path(__file__).resolve().parents[3]


REPO_ROOT = _repo_root()
DEMO_ORDERS = REPO_ROOT / "data" / "demo_orders"
DEMO_DOCS = REPO_ROOT / "data" / "demo_docs"


def _rows(filename: str) -> list[dict[str, str]]:
    with (DEMO_ORDERS / filename).open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


def test_demo_csv_dataset_meets_stage8_size_requirements() -> None:
    assert len(_rows("demo_customers.csv")) >= 50
    assert len(_rows("demo_products.csv")) >= 30
    assert len(_rows("demo_orders.csv")) >= 300
    assert len(_rows("demo_order_items.csv")) >= 400
    assert len(_rows("demo_reviews.csv")) >= 200
    assert len(_rows("demo_after_sales.csv")) >= 80


def test_demo_csv_dataset_covers_regions_categories_and_abnormal_signals() -> None:
    orders = _rows("demo_orders.csv")
    products = _rows("demo_products.csv")
    reviews = _rows("demo_reviews.csv")
    after_sales = _rows("demo_after_sales.csv")

    assert {"SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE"} <= {
        row["state"] for row in orders
    }
    assert {
        "electronics",
        "home_appliances",
        "books",
        "beauty",
        "sports",
        "toys",
        "fashion",
        "food",
        "baby",
        "health",
    } <= {row["category"] for row in products}
    assert {"canceled", "unavailable"} <= {row["order_status"] for row in orders}
    assert any("delivery_delay" in row["abnormal_flags"] for row in orders)
    assert any(int(row["review_score"]) <= 2 for row in reviews)
    assert {
        "refund_request",
        "product_damage",
        "wrong_item",
        "payment_issue",
        "customer_complaint",
    } <= {row["issue_type"] for row in after_sales}


def test_demo_docs_support_required_rag_questions() -> None:
    docs = "\n".join(path.read_text(encoding="utf-8") for path in DEMO_DOCS.glob("*.md"))

    required_phrases = [
        "Conflicts of Interest",
        "Human Approval",
        "Data Security",
        "Customer Complaint",
        "Delayed Delivery",
        "Product Damage",
        "Wrong Item",
        "Refund",
        "Abnormal Order",
    ]
    for phrase in required_phrases:
        assert phrase.lower() in docs.lower()


def test_stage8_public_files_do_not_contain_high_confidence_secrets() -> None:
    pattern = re.compile(
        r"(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|"
        r"ghp_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})"
    )
    scan_roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs",
        REPO_ROOT / "data",
        REPO_ROOT / "scripts",
    ]

    for root in scan_roots:
        paths = [root] if root.is_file() else root.rglob("*")
        for path in paths:
            if path.is_file():
                assert not pattern.search(path.read_text(encoding="utf-8", errors="ignore")), path
