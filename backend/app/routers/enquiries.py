from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException

from app.config.settings import settings
from app.models.schemas import ClassifyRequest, ClassifyResponse, EnquiryResponse
from app.services.ai_service import classify_enquiry
from app.services.enquiry_store import EnquiryStore

router = APIRouter(prefix="/api", tags=["enquiries"])
store = EnquiryStore()


async def _fire_webhook(enquiry: EnquiryResponse):
    if not settings.webhook_url:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                settings.webhook_url,
                json=enquiry.model_dump(mode="json"),
            )
    except Exception:
        pass


@router.post("/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Enquiry text cannot be empty")
    try:
        result = await classify_enquiry(req.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    return ClassifyResponse(**result)


@router.post("/enquiries", response_model=EnquiryResponse, status_code=201)
async def create_enquiry(req: ClassifyRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Enquiry text cannot be empty")
    try:
        result = await classify_enquiry(req.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    enquiry = EnquiryResponse(
        original_text=req.text,
        classification=result["classification"],
        priority=result.get("priority", "medium"),
        summary=result.get("summary", ""),
        entities=result.get("entities", {}),
        recommended_team=result.get("recommended_team", ""),
        suggested_response=result.get("suggested_response", ""),
    )
    saved = await store.save(enquiry)
    await _fire_webhook(saved)
    return saved


@router.get("/enquiries", response_model=list[EnquiryResponse])
async def list_enquiries():
    return await store.list_all()


@router.get("/enquiries/{enquiry_id}", response_model=EnquiryResponse)
async def get_enquiry(enquiry_id: UUID):
    enquiry = await store.get(enquiry_id)
    if enquiry is None:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return enquiry


@router.get("/enquiries/export", response_model=list[EnquiryResponse])
async def export_enquiries():
    return await store.list_all()
