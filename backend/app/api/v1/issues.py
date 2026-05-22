from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.issue_repository import IssueRepository
from app.services.issue_service import IssueService
from app.schemas.issue import IssueCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/issues")
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    return repo.create(issue.model_dump())


@router.get("/issues")
def get_issues(db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    return repo.get_all()


@router.get("/issues/open/{machine_code}")
def get_open_issues(machine_code: str, db: Session = Depends(get_db)):
    service = IssueService(db)
    return service.get_open_issues(machine_code)


@router.post("/issues/{issue_ref}/close")
def close_issue(issue_ref: str, db: Session = Depends(get_db)):
    service = IssueService(db)
    return service.close_issue(issue_ref)