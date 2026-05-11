from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    type: str
    subtype: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str = ""


class EnquiryResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    original_text: str
    classification: ClassificationResult
    priority: str = "medium"
    summary: str = ""
    entities: dict = {}
    recommended_team: str = ""
    suggested_response: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    classification: ClassificationResult
    priority: str
    summary: str
    entities: dict
    recommended_team: str
    suggested_response: str


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
