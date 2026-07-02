from app.models.report import Report


def build_export_placeholder(report: Report) -> dict:
    return {
        "report_id": report.report_id,
        "status": "not_implemented",
        "message": "Report export will be implemented in a later phase.",
        "supported_formats": ["pdf", "docx", "html"],
    }
