import pytest
from uuid import uuid4
from app.models.schemas import EnquiryResponse, ClassificationResult
from app.services.enquiry_store import EnquiryStore


@pytest.mark.asyncio
async def test_save_and_retrieve_enquiry():
    store = EnquiryStore()
    enquiry = EnquiryResponse(
        original_text="Test enquiry",
        classification=ClassificationResult(
            type="general_question", confidence=0.5, explanation="test"
        ),
        priority="low",
        summary="A test",
        recommended_team="Sales",
        suggested_response="Thanks",
    )
    saved = await store.save(enquiry)
    assert saved.id == enquiry.id

    retrieved = await store.get(enquiry.id)
    assert retrieved is not None
    assert retrieved.original_text == "Test enquiry"


@pytest.mark.asyncio
async def test_list_enquiries_empty():
    store = EnquiryStore()
    result = await store.list_all()
    assert result == []


@pytest.mark.asyncio
async def test_list_enquiries_with_data():
    store = EnquiryStore()
    e1 = EnquiryResponse(
        original_text="First",
        classification=ClassificationResult(type="new_client", confidence=0.9, explanation=""),
    )
    e2 = EnquiryResponse(
        original_text="Second",
        classification=ClassificationResult(type="complaint", confidence=0.8, explanation=""),
    )
    await store.save(e1)
    await store.save(e2)
    result = await store.list_all()
    assert len(result) == 2
