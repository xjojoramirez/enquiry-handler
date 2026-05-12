import pytest
from app.skills.classification.ai_service import classify_enquiry, GibberishDetector


def test_gibberish_detection():
    detector = GibberishDetector()
    assert detector.is_gibberish("xkvwjzqnrbhdfgyml")
    assert not detector.is_gibberish("Hi, I would like information about your services")
    assert detector.is_gibberish("")


@pytest.mark.asyncio
async def test_classify_enquiry_returns_expected_structure():
    result = await classify_enquiry("I want to buy a strata property")
    assert "classification" in result
    assert "priority" in result
    assert "summary" in result
    assert "recommended_team" in result
    assert "suggested_response" in result
