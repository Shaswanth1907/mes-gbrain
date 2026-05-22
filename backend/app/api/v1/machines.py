from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.machine_repository import MachineRepository
from app.services.machine_service import MachineService
from app.schemas.machine import MachineCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/machines")
def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    repo = MachineRepository(db)
    return repo.create(machine.model_dump())


@router.get("/machines")
def get_machines(db: Session = Depends(get_db)):
    repo = MachineRepository(db)
    return repo.get_all()


@router.get("/machines/{machine_code}")
def get_machine(machine_code: str, db: Session = Depends(get_db)):
    repo = MachineRepository(db)
    return repo.get_by_code(machine_code)


@router.get("/machines/{machine_code}/status")
def get_machine_status(machine_code: str, db: Session = Depends(get_db)):
    service = MachineService(db)
    return service.get_machine_status(machine_code)