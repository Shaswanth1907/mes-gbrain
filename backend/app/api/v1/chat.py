from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest
from app.services.copilot_orchestrator import CopilotOrchestrator

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    copilot = CopilotOrchestrator(db)

    result = copilot.handle(request.question)

    return {
        "answer": result
    }