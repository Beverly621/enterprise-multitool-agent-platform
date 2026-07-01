from app.seed.seed_demo_data import seed as seed_demo_data
from app.seed.seed_tools import seed as seed_tools
from app.seed.seed_users import seed as seed_users


def seed() -> None:
    seed_users()
    seed_tools()
    seed_demo_data()


if __name__ == "__main__":
    seed()

