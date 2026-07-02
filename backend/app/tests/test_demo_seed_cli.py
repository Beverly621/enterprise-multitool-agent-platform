from app.seed import seed_demo_orders


def test_stage8_seed_defaults_match_demo_scale() -> None:
    assert seed_demo_orders.CATEGORIES
    assert len(seed_demo_orders.CATEGORIES) >= 10
    assert {"SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE"} <= set(
        seed_demo_orders.STATES
    )

