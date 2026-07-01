def build_trace_event(event_type: str, event_name: str, content: str | None = None) -> dict:
    return {"event_type": event_type, "event_name": event_name, "content": content}

