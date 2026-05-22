from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.work_order_service import WorkOrderService

router = APIRouter()


@router.post("/work-orders")
def create_work_order(
    machine_code: str,
    description: str,
    priority: str = "MEDIUM",
    db: Session = Depends(get_db)
):
    service = WorkOrderService(db)
    return service.create_work_order(machine_code, description, priority)


@router.get("/work-orders/open/{machine_code}")
def get_open_work_orders(machine_code: str, db: Session = Depends(get_db)):
    service = WorkOrderService(db)
    return service.get_open_work_orders(machine_code)


@router.post("/work-orders/{work_order_ref}/close")
def close_work_order(work_order_ref: str, db: Session = Depends(get_db)):
    service = WorkOrderService(db)
    return service.close_work_order(work_order_ref)
