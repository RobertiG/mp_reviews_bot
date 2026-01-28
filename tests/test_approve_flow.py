from mp_reviews_bot.approvals import service as approvals_service


def test_approve_flow_updates_status_and_audit_fields():
    approved = approvals_service.approve_draft(draft_id="draft-1", approver_id="user-1")

    assert approved.status == "approved"
    assert approved.approved_by == "user-1"
    assert approved.approved_at is not None
