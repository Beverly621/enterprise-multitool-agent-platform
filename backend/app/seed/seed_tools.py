from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.tool import AgentTool


DEMO_TOOLS = [
    {
        "name": "order_status_lookup",
        "description": "Look up enterprise order status by order id.",
        "schema_json": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
        "endpoint": "mock://order_status_lookup",
        "requires_approval": False,
    },
    {
        "name": "refund_request",
        "description": "Create a refund request that requires human approval.",
        "schema_json": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
                "reason": {"type": "string"},
            },
            "required": ["order_id", "amount", "reason"],
        },
        "endpoint": "mock://refund_request",
        "requires_approval": True,
    },
]


def seed() -> None:
    with SessionLocal() as db:
        for item in DEMO_TOOLS:
            tool = db.scalar(select(AgentTool).where(AgentTool.name == item["name"]))
            if tool is None:
                db.add(AgentTool(**item))
            else:
                tool.description = item["description"]
                tool.schema_json = item["schema_json"]
                tool.endpoint = item["endpoint"]
                tool.requires_approval = item["requires_approval"]
        db.commit()
        print("Seeded demo tools.")


if __name__ == "__main__":
    seed()

