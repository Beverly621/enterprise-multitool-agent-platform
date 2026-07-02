from app.services.intent_router_service import route_intent


def plan_intent(query: str) -> str:
    return route_intent(query).intent
