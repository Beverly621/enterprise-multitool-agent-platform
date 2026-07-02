from app.seed.seed_demo_data import seed as seed_demo_data
from app.seed.seed_demo_orders import seed as seed_demo_orders
from app.seed.seed_tools import seed as seed_tools
from app.seed.seed_users import seed as seed_users


def seed(reset: bool = False) -> None:
    seed_users()
    seed_tools()
    seed_demo_data(reset=reset)
    if reset:
        from app.seed.seed_demo_orders import reset_and_seed

        reset_and_seed()
    else:
        seed_demo_orders()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    seed(reset=args.reset)
