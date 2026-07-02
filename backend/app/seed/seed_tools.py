from app.core.database import SessionLocal
from app.services.tool_registry import ToolRegistry


def seed() -> None:
    with SessionLocal() as db:
        synced = ToolRegistry(db).sync_builtin_tools()
        db.commit()
        print(f"Seeded {len(synced)} built-in tools.")


if __name__ == "__main__":
    seed()
