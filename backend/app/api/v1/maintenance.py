from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.maintenance_service import MaintenanceService

router = APIRouter()


@router.get("/maintenance/{machine_code}")
def get_maintenance_history(machine_code: str, db: Session = Depends(get_db)):
    service = MaintenanceService(db)
    return service.get_history(machine_code)
