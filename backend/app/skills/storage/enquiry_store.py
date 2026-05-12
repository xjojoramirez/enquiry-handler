import json
from uuid import UUID
from typing import Optional

from app.skills.storage.database import get_pool
from app.skills.classification.schemas import ClassificationResult, EnquiryResponse


class EnquiryStore:
    async def save(self, enquiry: EnquiryResponse) -> EnquiryResponse:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO enquiries (id, original_text, classification, priority,
                                       summary, entities, recommended_team, suggested_response)
                VALUES ($1, $2, $3::jsonb, $4, $5, $6::jsonb, $7, $8)
                """,
                enquiry.id,
                enquiry.original_text,
                enquiry.classification.model_dump_json(),
                enquiry.priority,
                enquiry.summary,
                enquiry.entities,
                enquiry.recommended_team,
                enquiry.suggested_response,
            )
        return enquiry

    async def get(self, enquiry_id: UUID) -> Optional[EnquiryResponse]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM enquiries WHERE id = $1", enquiry_id
            )
        if row is None:
            return None
        return self._row_to_enquiry(row)

    async def list_all(self) -> list[EnquiryResponse]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM enquiries ORDER BY created_at DESC"
            )
        return [self._row_to_enquiry(row) for row in rows]

    def _row_to_enquiry(self, row) -> EnquiryResponse:
        cls_data = json.loads(row["classification"])
        return EnquiryResponse(
            id=row["id"],
            original_text=row["original_text"],
            classification=ClassificationResult(**cls_data),
            priority=row["priority"],
            summary=row["summary"] or "",
            entities=json.loads(row["entities"]) if isinstance(row["entities"], str) else row["entities"] or {},
            recommended_team=row["recommended_team"] or "",
            suggested_response=row["suggested_response"] or "",
            timestamp=row["created_at"],
        )
