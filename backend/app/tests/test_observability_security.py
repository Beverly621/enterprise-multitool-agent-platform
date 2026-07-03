from app.services.provider_metrics_service import _sanitize_error


def test_provider_metric_error_sanitizer_redacts_secrets() -> None:
    message = _sanitize_error("Authorization=Bearer secret-token api_key=sk-test123456789012")

    assert "secret-token" not in message
    assert "sk-test" not in message
    assert "[REDACTED]" in message
