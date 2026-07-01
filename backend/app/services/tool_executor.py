def execute_mock_tool(name: str, args: dict) -> dict:
    return {"tool": name, "args": args, "status": "mock_executed"}

