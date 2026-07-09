from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])

class AIQueryRequest(BaseModel):
    query: str
    employee_id: int | None = None

class AIQueryResponse(BaseModel):
    answer: str

@router.post("/query", response_model=AIQueryResponse)
def query_assistant(schema: AIQueryRequest, db: Session = Depends(get_db)):
    answer = AIService.process_query(db, schema.query, schema.employee_id)
    return AIQueryResponse(answer=answer)
