from app.agent.nodes.intent_router import route_intent


def plan_intent(query: str) -> str:
    return route_intent(query)

