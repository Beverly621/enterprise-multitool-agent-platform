from types import SimpleNamespace

from app.services.approval_service import requires_human_approval, serialize_approval


def test_send_email_draft_requires_approval() -> None:
    assert requires_human_approval("send_email_draft") is True
    assert requires_human_approval("query_order_status") is False


def test_serialize_approval_prefers_phase_four_payload() -> None:
    approval = SimpleNamespace(
        id=1,
        approval_id="ap_1",
        tool_call_id="tc_1",
        user_id=2,
        tool_name="send_email_draft",
        approval_type="TOOL_CALL",
        status="PENDING",
        reason=None,
        request_payload={"draft_id": "draft_1"},
        payload_json={"legacy": True},
        approval_result=None,
        requested_by=2,
        requester_id=2,
        approved_by=None,
        approver_id=None,
        created_at=None,
        updated_at=None,
        approved_at=None,
        rejected_at=None,
    )

    data = serialize_approval(approval)

    assert data["request_payload"] == {"draft_id": "draft_1"}
    assert data["tool_name"] == "send_email_draft"
