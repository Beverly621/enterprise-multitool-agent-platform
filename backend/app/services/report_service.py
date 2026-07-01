def render_report(title: str, sections: list[str]) -> str:
    body = "\n\n".join(sections)
    return f"# {title}\n\n{body}"

